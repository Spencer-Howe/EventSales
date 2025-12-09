"""
PayPal Webhook Handler - Idempotent booking creation
Only creates bookings via PAYMENT.CAPTURE.COMPLETED webhook
"""
import os
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime
from flask import Blueprint, request, current_app, jsonify
from flask_mail import Message
from .extensions import db, mail
from .models import Booking, Customer, Payment, Event
from .views import send_admin_booking_notification, create_receipt_email_content

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/paypal/webhook', methods=['POST'])
def handle_paypal_webhook():
    """
    Handle PayPal PAYMENT.CAPTURE.COMPLETED webhooks
    Only source of truth for booking creation
    """
    try:
        # Get webhook payload
        payload = request.get_data(as_text=True)
        webhook_data = request.get_json()
        
        current_app.logger.info(f"PayPal webhook received: {webhook_data.get('event_type', 'unknown')}")
        
        # Verify webhook signature
        if not verify_webhook_signature(payload, request.headers):
            current_app.logger.error("Invalid webhook signature")
            return jsonify({"error": "Invalid signature"}), 400
        
        # Only process PAYMENT.CAPTURE.COMPLETED events
        event_type = webhook_data.get('event_type')
        if event_type != 'PAYMENT.CAPTURE.COMPLETED':
            current_app.logger.info(f"Ignoring webhook event type: {event_type}")
            return jsonify({"message": "Event ignored"}), 200
        
        # Extract order information from webhook
        resource = webhook_data.get('resource', {})
        
        # Get order_id from supplementary_data or directly
        order_id = None
        supplementary_data = resource.get('supplementary_data', {})
        if supplementary_data and 'related_ids' in supplementary_data:
            order_id = supplementary_data['related_ids'].get('order_id')
        
        if not order_id:
            # Fallback: get order_id from capture_id by calling PayPal API
            capture_id = resource.get('id')
            if capture_id:
                order_id = get_order_id_from_capture(capture_id)
        
        if not order_id:
            current_app.logger.error("Could not extract order_id from webhook")
            return jsonify({"error": "Missing order_id"}), 400
        
        current_app.logger.info(f"Processing webhook for order_id: {order_id}")
        
        # Idempotency check - if booking exists, do nothing
        existing_booking = Booking.query.filter_by(order_id=order_id).first()
        if existing_booking:
            current_app.logger.info(f"Booking already exists for order_id: {order_id}")
            return jsonify({"message": "Booking already processed"}), 200
        
        # Get full order details from PayPal
        order_details = get_order_details_from_paypal(order_id)
        if not order_details:
            current_app.logger.error(f"Could not fetch order details for {order_id}")
            return jsonify({"error": "Could not fetch order details"}), 400
        
        # Extract metadata from custom_id
        custom_id = None
        purchase_units = order_details.get('purchase_units', [])
        if purchase_units:
            custom_id = purchase_units[0].get('custom_id')
        
        if not custom_id:
            current_app.logger.error(f"Missing custom_id metadata for order {order_id}")
            return jsonify({"error": "Missing booking metadata"}), 400
        
        try:
            booking_metadata = json.loads(custom_id)
        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON in custom_id for order {order_id}")
            return jsonify({"error": "Invalid booking metadata"}), 400
        
        # Create booking from webhook data
        success = create_booking_from_webhook(order_id, order_details, booking_metadata)
        
        if success:
            current_app.logger.info(f"Booking created successfully for order {order_id}")
            return jsonify({"message": "Booking created"}), 200
        else:
            current_app.logger.error(f"Failed to create booking for order {order_id}")
            return jsonify({"error": "Booking creation failed"}), 500
            
    except Exception as e:
        current_app.logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


def verify_webhook_signature(payload, headers):
    """
    Verify PayPal webhook signature
    Returns True if signature is valid
    """
    try:
        webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')
        if not webhook_id:
            current_app.logger.warning("PAYPAL_WEBHOOK_ID not configured - skipping signature verification")
            return True  # Allow during development/testing
        
        # Get signature headers
        transmission_id = headers.get('PAYPAL-TRANSMISSION-ID')
        cert_id = headers.get('PAYPAL-CERT-ID')
        auth_algo = headers.get('PAYPAL-AUTH-ALGO')
        transmission_sig = headers.get('PAYPAL-TRANSMISSION-SIG')
        timestamp = headers.get('PAYPAL-TRANSMISSION-TIME')
        
        if not all([transmission_id, cert_id, auth_algo, transmission_sig, timestamp]):
            return False
        
        # Call PayPal verification API
        verification_url = f"{current_app.config['PAYPAL_API_BASE']}/v1/notifications/verify-webhook-signature"
        
        access_token = get_paypal_access_token()
        if not access_token:
            return False
        
        verification_data = {
            'auth_algo': auth_algo,
            'cert_id': cert_id,
            'transmission_id': transmission_id,
            'transmission_sig': transmission_sig,
            'transmission_time': timestamp,
            'webhook_id': webhook_id,
            'webhook_event': json.loads(payload)
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(verification_url, json=verification_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('verification_status') == 'SUCCESS'
        
        return False
        
    except Exception as e:
        current_app.logger.error(f"Signature verification error: {str(e)}")
        return False


def get_order_id_from_capture(capture_id):
    """
    Get order_id from capture_id using PayPal API
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
        
        url = f"{current_app.config['PAYPAL_API_BASE']}/v2/payments/captures/{capture_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            capture_data = response.json()
            supplementary_data = capture_data.get('supplementary_data', {})
            if supplementary_data and 'related_ids' in supplementary_data:
                return supplementary_data['related_ids'].get('order_id')
        
        return None
        
    except Exception as e:
        current_app.logger.error(f"Error getting order_id from capture {capture_id}: {str(e)}")
        return None


def get_order_details_from_paypal(order_id):
    """
    Fetch complete order details from PayPal API
    """
    try:
        access_token = get_paypal_access_token()
        if not access_token:
            return None
        
        url = f"{current_app.config['PAYPAL_API_BASE']}/v2/checkout/orders/{order_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        
        current_app.logger.error(f"Failed to fetch order details: {response.status_code}")
        return None
        
    except Exception as e:
        current_app.logger.error(f"Error fetching order details for {order_id}: {str(e)}")
        return None


def get_paypal_access_token():
    """
    Get PayPal access token for API calls
    """
    try:
        url = f"{current_app.config['PAYPAL_API_BASE']}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(
            url, 
            headers=headers, 
            data=data, 
            auth=(os.getenv('PAYPAL_CLIENT_ID'), os.getenv('PAYPAL_CLIENT_SECRET'))
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        current_app.logger.error(f"Failed to get access token: {response.status_code}")
        return None
        
    except Exception as e:
        current_app.logger.error(f"Access token error: {str(e)}")
        return None


def create_booking_from_webhook(order_id, order_details, booking_metadata):
    """
    Create booking, customer, and payment records from webhook data
    This is the ONLY function that creates bookings
    """
    try:
        # Extract booking metadata
        event_id = booking_metadata.get('event_id')
        tickets = booking_metadata.get('tickets')
        phone = booking_metadata.get('phone')
        user_email = booking_metadata.get('email')  # Optional user-provided email
        
        if not event_id or not tickets:
            current_app.logger.error(f"Missing required metadata: event_id={event_id}, tickets={tickets}")
            return False
        
        # Get event
        event = Event.query.get(event_id)
        if not event:
            current_app.logger.error(f"Event {event_id} not found")
            return False
        
        # Extract PayPal order details
        payer_info = order_details.get('payer', {})
        payer_name = payer_info.get('name', {})
        name = f"{payer_name.get('given_name', '')} {payer_name.get('surname', '')}"
        paypal_email = payer_info.get('email_address')
        
        # Use user-provided email if available, otherwise PayPal email
        email = user_email if user_email else paypal_email
        
        purchase_units = order_details.get('purchase_units', [])
        if not purchase_units:
            current_app.logger.error("No purchase units in order")
            return False
        
        amount = float(purchase_units[0]['amount']['value'])
        currency = purchase_units[0]['amount']['currency_code']
        status = order_details.get('status')
        
        # Find or create customer
        customer = Customer.query.filter_by(email=email).first()
        if not customer:
            customer = Customer(
                name=name.strip(),
                email=email,
                phone=phone
            )
            db.session.add(customer)
            db.session.flush()
        
        # Holiday Minis: force tickets to 1 regardless of guest count
        stored_tickets = 1 if "Holiday Minis" in event.title else int(tickets)
        
        # Create booking
        booking = Booking(
            customer_id=customer.id,
            event_id=event.id,
            tickets=stored_tickets,
            order_id=order_id,
            reminder_sent=False,
            receipt_sent=False
        )
        db.session.add(booking)
        db.session.flush()
        
        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            amount_paid=amount,
            currency=currency,
            status=status,
            payment_method='paypal',
            paypal_order_id=order_id
        )
        db.session.add(payment)
        
        # Mark private event as booked when payment is completed
        if event.is_private and status == 'COMPLETED' and "Holiday Minis" not in event.title:
            event.is_booked = True
        
        # Commit all database changes first
        db.session.commit()
        
        # Send customer confirmation email (also to admin)
        try:
            # Create application context for url_for() to work
            with current_app.app_context():
                send_customer_confirmation_email(booking, payment, order_id)
            current_app.logger.info(f"Customer confirmation sent for {order_id}")
        except Exception as e:
            current_app.logger.error(f"Failed to send customer confirmation for {order_id}: {str(e)}")
            # Don't fail webhook - booking is already committed
        
        current_app.logger.info(f"Booking created successfully: {order_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Booking creation failed for {order_id}: {str(e)}")
        return False


def send_customer_confirmation_email(booking, payment, order_id):
    """
    Send customer confirmation email with receipt and waiver links
    Always sends - no receipt_sent tracking needed
    """
    from flask import url_for
    from .views import create_receipt_email_content
    
    # Prepare email details
    email_order_details = {
        'name': booking.customer.name,
        'email': booking.customer.email,
        'phone': booking.customer.phone,
        'order_id': order_id,
        'amount': payment.amount_paid,
        'currency': payment.currency,
        'status': payment.status,
        'time_slot': booking.event.start.strftime('%m/%d/%Y %I:%M %p') if booking.event.start else 'TBD',
        'tickets': booking.tickets
    }
    
    # Build URLs
    waiver_url = url_for('views.sign_waiver', order_id=order_id, _external=True)
    receipt_url = url_for('views.show_receipt', order_id=order_id, _external=True)
    email_order_details['waiver_url'] = waiver_url
    email_order_details['receipt_url'] = receipt_url
    email_order_details['checkin_url'] = f"https://thehoweranchpayment.com/api/booking/{order_id}"
    
    # Always send email - webhook only runs once per order
    html_content = create_receipt_email_content(email_order_details)
    subject = "Your Payment Receipt"
    sender = current_app.config['MAIL_USERNAME']
    recipients = [booking.customer.email, 'howeranchservices@gmail.com']
    
    msg = Message(subject, sender=sender, recipients=recipients, html=html_content)
    mail.send(msg)