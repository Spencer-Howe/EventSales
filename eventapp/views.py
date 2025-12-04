import os
import requests
from datetime import datetime, timedelta
import pytz
from flask import jsonify, render_template, request, redirect, url_for, session, Blueprint, current_app, Response
from flask_mail import Message
from flask_login import login_user, logout_user, login_required
import qrcode
import io
import base64
# noinspection PyUnresolvedReferences
from .extensions import db, mail, login_manager




views = Blueprint('views', __name__)




@views.route('/admin/booking/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    from eventapp.models import Booking
    booking = Booking.query.get_or_404(booking_id)
    # noinspection PyUnresolvedReferences
    return render_template('base1.html', booking=booking)

@views.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        from eventapp.models import User
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            return 'Invalid credentials'
    # noinspection PyUnresolvedReferences
    return render_template('login.html')

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@views.route('/')
def home():
    # noinspection PyUnresolvedReferences
    return render_template('home.html')

# Note: calculate_price route moved to booking.py blueprint



@views.route('/test')
def test():
    return render_template('test.html')

@views.route('/select_tickets')
def select_tickets():
    paypal_client_id = current_app.config['PAYPAL_CLIENT_ID']
    # noinspection PyUnresolvedReferences
    return render_template(
        'select_tickets.html',
        paypal_client_id=paypal_client_id
    )

@views.route('/tourbook')
def select_tourbook():
    # noinspection PyUnresolvedReferences
    return render_template('tourbook.html')

@views.route('/checkout', methods=['GET'])
def checkout():
    # Retrieve the event ID and number of tickets from the URL query parameters
    event_id = request.args.get('event_id')
    tickets = request.args.get('tickets')

    try:
        event_id = int(event_id)  # Convert event_id to integer
    except (ValueError, TypeError):
        return "Invalid event ID", 400
        
    try:
        tickets = int(float(tickets))  # Convert to float first, then cast to int
    except (ValueError, TypeError):
        tickets = 0  # Default to 0 if there's an issue with conversion

    # Query the event from the database
    from .models import Event
    from .pricing import get_total_price, get_booking_summary, check_capacity
    
    event = Event.query.get_or_404(event_id)

    # Check capacity first
    can_book, capacity_error = check_capacity(event, tickets)
    if not can_book:
        return render_template('checkout.html',
                             time_slot='Event Full',
                             tickets=tickets,
                             total_price=0,
                             paypal_client_id=current_app.config['PAYPAL_CLIENT_ID'],
                             event_title=event.title,
                             event_description=event.description,
                             error_message=capacity_error)

    # Calculate the total price using pricing module
    total_price = get_total_price(event, tickets)

    # Get formatted booking summary
    booking_summary = get_booking_summary(event, tickets, total_price)

    # Pass all details to the template
    return render_template('checkout.html',
                           event_id=event.id,
                           event_title=booking_summary['event_title'],
                           event_description=booking_summary['event_description'],
                           time_slot=booking_summary['time_slot'],
                           tickets=tickets,
                           total_price=total_price,
                           paypal_client_id=current_app.config['PAYPAL_CLIENT_ID'],
                           error_message=None)


@views.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    data = request.get_json()
    phone = data.get('phone')
    order_id = request.json.get('orderID')
    event_id = data.get('event_id')
    tickets = data.get('tickets')
    
    access_token = get_paypal_access_token()
    if not access_token:
        return jsonify({"verified": False, "reason": "Failed to obtain access token"}), 500
    verified, order_details = verify_order_with_paypal(order_id, access_token)
    if verified:
        # Check if booking already exists (prevent duplicates)
        from .models import Booking
        existing_booking = Booking.query.filter_by(order_id=order_id).first()
        if existing_booking:
            return jsonify({
                "verified": True, 
                "orderID": order_id, 
                "details": order_details,
                "booking_exists": True
            })
        
        # Create booking immediately after PayPal verification
        try:
            from .models import Event, Customer, Payment
            
            # Get event
            event = Event.query.filter_by(id=event_id).first()
            if not event:
                raise Exception(f"Event {event_id} not found")
                
            # Extract PayPal details
            payer_info = order_details.get('payer', {})
            name = f"{payer_info.get('name').get('given_name')} {payer_info.get('name').get('surname')}"
            paypal_email = payer_info.get('email_address')
            amount = order_details['purchase_units'][0]['amount']['value']
            currency = order_details['purchase_units'][0]['amount']['currency_code']
            status = order_details.get('status')
            
            # Find or create customer with PayPal email
            customer = Customer.query.filter_by(email=paypal_email).first()
            if not customer:
                customer = Customer(
                    name=name,
                    email=paypal_email,
                    phone=phone
                )
                db.session.add(customer)
                db.session.flush()
            
            # Holiday Minis: force tickets to 1 regardless of guest count
            stored_tickets = 1 if "Holiday Minis" in event.title else int(tickets)
            
            # Create booking
            new_booking = Booking(
                customer_id=customer.id,
                event_id=event.id,
                tickets=stored_tickets,
                order_id=order_id,
                reminder_sent=False
            )
            db.session.add(new_booking)
            db.session.flush()
            
            # Create payment record
            payment = Payment(
                booking_id=new_booking.id,
                amount_paid=float(amount),
                currency=currency,
                status=status,
                payment_method='paypal',
                paypal_order_id=order_id
            )
            db.session.add(payment)
            
            # Mark private event as booked when PayPal payment is completed
            if event.is_private and status == 'COMPLETED' and "Holiday Minis" not in event.title:
                event.is_booked = True
            
            # Commit booking immediately after PayPal verification
            db.session.commit()
            
            return jsonify({
                "verified": True, 
                "orderID": order_id, 
                "details": order_details,
                "booking_created": True
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Booking creation failed for {order_id}: {str(e)}")
            return jsonify({
                "verified": True,
                "orderID": order_id,
                "details": order_details,
                "booking_created": False,
                "error": str(e)
            }), 500
    else:
        return jsonify({"verified": False, "reason": "Verification failed or order not completed"}), 400


@views.route('/update_booking_email', methods=['POST'])
def update_booking_email():
    """Update email for existing booking"""
    data = request.get_json()
    order_id = data.get('order_id')
    new_email = data.get('email')
    
    if not order_id or not new_email:
        return jsonify({"success": False, "error": "Missing order_id or email"}), 400
    
    # Find existing booking
    from eventapp.models import Booking
    booking = Booking.query.filter_by(order_id=order_id).first()
    if not booking:
        return jsonify({"success": False, "error": "Booking not found"}), 404
    
    try:
        # Update customer email
        booking.customer.email = new_email
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email update failed for {order_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@views.route('/waiver/<order_id>', methods=['GET', 'POST'])
def sign_waiver(order_id):
    from eventapp.models import Waiver, Booking
    
    # Check if waiver already exists (for both GET and POST)
    existing_waiver = Waiver.query.filter_by(order_id=order_id).first()
    if existing_waiver:
        # Waiver already signed, redirect to thank you page
        return redirect(url_for('views.thank_you_page'))
    
    if request.method == 'POST':
        signature = request.form.get('signature')
        
        # Find booking to get customer
        booking = Booking.query.filter_by(order_id=order_id).first()
        if not booking or not booking.customer:
            return "Booking not found", 404
            
        new_waiver = Waiver(
            customer_id=booking.customer.id,
            order_id=order_id,
            signature=signature, 
            signed_date=datetime.utcnow()
        )
        db.session.add(new_waiver)
        db.session.commit()
        subject = f"New Waiver Submitted: {order_id}"
        sender = current_app.config['MAIL_USERNAME']
        recipients = [sender]
        body = f"""
        A new waiver has been submitted.

        Details:
        ID: {new_waiver.id}
        Order ID: {order_id}
        Signature: {signature}
        Signed Date: {new_waiver.signed_date}

        Please review the submission in your system.
        """
        message = Message(subject, sender=sender, recipients=recipients, body=body)
        mail.send(message)
        return redirect(url_for('views.thank_you_page'))
    # noinspection PyUnresolvedReferences
    return render_template('waiver_form.html', order_id=order_id)

@views.route('/receipt/<order_id>')
def show_receipt(order_id):
    from eventapp.models import Booking
    
    # Find existing booking (should exist since booking is created in verify_transaction)
    existing_booking = Booking.query.filter_by(order_id=order_id).first()
    if not existing_booking:
        return "Booking not found. Please contact support with order ID: " + order_id, 404
    
    # Show receipt from database
    qr_code = generate_qr_code(order_id)
    booking_info_url = f"https://thehoweranchpayment.com/api/booking/{order_id}"
    
    # Get latest payment for display
    latest_payment = existing_booking.payments[0] if existing_booking.payments else None
    
    # Send confirmation email if not already sent (safety check)
    try:
        send_confirmation_email_for_booking(existing_booking, latest_payment, order_id)
    except Exception as email_error:
        current_app.logger.error(f"Failed to send confirmation email for {order_id}: {str(email_error)}")
        # Continue showing receipt even if email fails
    
    return render_template('receipt.html', 
                         order_id=existing_booking.order_id,
                         name=existing_booking.customer.name if existing_booking.customer else "Unknown",
                         email=existing_booking.customer.email if existing_booking.customer else "Unknown",
                         time_slot=existing_booking.event.start if existing_booking.event else None,
                         tickets=existing_booking.tickets,
                         amount=latest_payment.amount_paid if latest_payment else 0,
                         currency=latest_payment.currency if latest_payment else "USD",
                         status=latest_payment.status if latest_payment else "Unknown",
                         phone=existing_booking.customer.phone if existing_booking.customer else None,
                         qr_code=qr_code,
                         checkin_url=booking_info_url)


def send_confirmation_email_for_booking(booking, payment, order_id):
    """Send confirmation email for existing booking"""
    if not booking or not booking.customer or not payment:
        return
        
    # Prepare email details
    email_order_details = {
        'name': booking.customer.name,
        'email': booking.customer.email,
        'phone': booking.customer.phone,
        'order_id': order_id,
        'amount': payment.amount_paid,
        'currency': payment.currency,
        'status': payment.status,
        'time_slot': booking.event.start if booking.event else 'Unknown',
        'tickets': booking.tickets
    }
    
    waiver_url = url_for('views.sign_waiver', order_id=order_id, _external=True)
    receipt_url = url_for('views.show_receipt', order_id=order_id, _external=True)
    email_order_details['waiver_url'] = waiver_url
    email_order_details['receipt_url'] = receipt_url
    
    # Add check-in URL for reference
    booking_info_url = f"https://thehoweranchpayment.com/api/booking/{order_id}"
    email_order_details['checkin_url'] = booking_info_url
    
    html_content = create_receipt_email_content(email_order_details)
    subject = "Your Payment Receipt"
    sender = current_app.config['MAIL_USERNAME']
    recipients = [booking.customer.email, 'howeranchservices@gmail.com']
    msg = Message(subject, sender=sender, recipients=recipients, html=html_content)
    mail.send(msg)



@views.route('/qr_download/<order_id>')
def download_qr_code(order_id):
    """Download QR code as PNG file"""
    from eventapp.models import Booking
    
    # Verify booking exists
    booking = Booking.query.filter_by(order_id=order_id).first()
    if not booking:
        return "Booking not found", 404
    
    # Generate QR code
    booking_info_url = f"https://thehoweranchpayment.com/api/booking/{order_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(booking_info_url)
    qr.make(fit=True)
    
    # Generate the QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes for download
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return Response(
        buffer.getvalue(),
        mimetype='image/png',
        headers={
            'Content-Disposition': f'attachment; filename="qr_code_{order_id}.png"',
            'Content-Type': 'image/png'
        }
    )

@views.route('/thank_you')
def thank_you_page():
    # noinspection PyUnresolvedReferences
    return render_template('thank_you.html')

@views.route('/get_events')
def get_events():
    from eventapp.models import Event

    from sqlalchemy import and_

    events = Event.query.filter(
        and_(Event.private.is_(False), Event.is_booked.is_(False))
    ).all()

    events_data = [{
        'id': event.id,
        'title': event.title,
        'start': event.start.isoformat(),
        'end': event.end.isoformat(),
        'description': event.description
    } for event in events]
    return jsonify(events_data)








def generate_qr_code(order_id):
    """Generate QR code for booking info (safe for public access)"""
    # QR code now contains the safe booking info URL instead of direct check-in
    booking_info_url = f"https://thehoweranchpayment.com/api/booking/{order_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(booking_info_url)
    qr.make(fit=True)
    
    # Generate the QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{qr_code_base64}"


def get_paypal_access_token():
    url = f"{current_app.config['PAYPAL_API_BASE']}/v1/oauth2/token"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, headers=headers, data=data, auth=(os.getenv('PAYPAL_CLIENT_ID'), os.getenv('PAYPAL_CLIENT_SECRET')))
    if response.status_code != 200:
        current_app.logger.error(f"Failed to get PayPal access token: {response.text}")
        return None
    return response.json().get('access_token')

def verify_order_with_paypal(order_id, access_token):
    url = f"{current_app.config['PAYPAL_API_BASE']}/v2/checkout/orders/{order_id}"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        order_details = response.json()
        return order_details['status'] == 'COMPLETED', order_details
    return False, None

def create_receipt_email_content(order_details):
    html_content = f"""
    
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2e6c80;">Payment Receipt</h1>
            <p><strong>Name:</strong> {order_details['name']}</p>
            <p><strong>Email:</strong> {order_details['email']}</p>
            <p><strong>Phone Number:</strong> {order_details['phone']}</p>
            <p><strong>Order ID:</strong> {order_details['order_id']}</p>
            <p><strong>Total Amount:</strong> {order_details['amount']}</p>
            <p><strong>Currency:</strong> {order_details['currency']}</p>
            <p><strong>Status:</strong> {order_details['status']}</p>
            <p><strong>Time Slot:</strong> {order_details['time_slot']}</p>
            <p><strong>Number of Tickets:</strong> {order_details['tickets']}</p>
            <p>Please review and sign the waiver if you did not already finish the registration after checkout 
                <a href="{order_details['waiver_url']}" style="color: #1a73e8;">here</a>.
            </p>
            
            <!-- Receipt & QR Code Link -->
            <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #007bff; border-radius: 10px; background-color: #f8f9fa;">
                <h3 style="color: #007bff; margin-bottom: 15px;">📱 Check-in QR Code</h3>
                <p style="margin-bottom: 15px;"><strong>Access your QR code for instant check-in at the ranch!</strong></p>
                <a href="{order_details['receipt_url']}" style="display: inline-block; background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px;">
                    View Receipt & QR Code
                </a>
                <p style="margin-top: 10px; font-size: 0.9rem; color: #6c757d;">
                    Save this link or bookmark it for easy access on your phone
                </p>
            </div>
            
            <hr style="margin: 30px 0;">
            <h2 style="color: #2e6c80;">Thank You & Important Visit Information</h2>
            <p>
                Thank you for purchasing passes to the Mini Moos experience at Howe Ranch! Our miniature Highland cows and their barn friends are excited to show you the magical place they call home:
            </p>
            <p>
                <strong>22053 Highland St<br>
                Wildomar, CA 92595</strong>
            </p>
            <p>
                To be compliant with our neighborhood's no impact policies and liability regulations, and ensure a safe and enjoyable experience for the animals and you, we must ask that you please confirm that you have reviewed the visit guidelines below, as posted on our website:
            </p>
            
            <h3 style="color: #d9534f; margin-top: 25px;">Arrival Guidelines - No Early Arrivals</h3>
            <ul style="padding-left: 20px;">
                <li>
                    <strong>EARLY ARRIVALS STRICTLY PROHIBITED:</strong> Guests must not arrive before the event start time. Entry is strictly prohibited before your scheduled time slot due to farm liability management guidelines, which includes moving animals across the parking access area. Early arrivals disrupt operations, compromise safety while moving animals, and will not be accommodated. You will not miss anything by arriving after your scheduled time. We recommend Montage Brothers and Starbucks coffee houses down the street if you arrive in the area early.
                </li>
                <br>
                <li>
                    <strong>PRIVATE ROAD LAWS:</strong> Stopping or staging on the private farm road is strictly prohibited. Strict 15 MPH speed limit on the monitored, unpaved street leading to Howe Ranch as posted— speeding will result in loss of your pass(es).
                </li>
            </ul>
            
            <h3 style="color: #2e6c80; margin-top: 25px;">Animal Interactions & Safety</h3>
            <ul style="padding-left: 20px;">
                <li>
                    <strong>NO DOGS:</strong> For the safety of our animals and guests, our farm cannot accommodate dogs. Most of our animals are prey species, their reactions would make the encounter unsafe for all, and we have trained livestock guardians to protect from unknown canines on site.
                </li>
                <br>
                <li>
                    <strong>SAFETY:</strong> Sunscreen, hat, and closed-toed shoes. Important: Bring water for hydration.
                </li>
                <br>
                <li>
                    <strong>SUPERVISED ONLY:</strong> For your safety and the safety of our animals, please do not approach any animals until staff has reviewed safety guidelines with you and is present. Children must be supervised by your group at all time.
                </li>
            </ul>
            <p style="margin-top: 15px;">
                If you arrive and do not see a staff member immediately, please call or text (424) 219-4212 and remain in the designated waiting area. We might be assisting other guests or preparing animals for your experience.
            </p>
            
            <h3 style="color: #2e6c80; margin-top: 25px;">Transferable Only — No Refunds or Reschedules</h3>
            <p>
                The moment your experience is booked, resources are reserved and your time slot is blocked from other visitors. Booked experiences are transferable to other guests in your network, but not refundable, and cannot be rescheduled. Because our team is fully dedicated to caring for the animals and hosting scheduled guests, requests for exceptions cannot be accommodated and will not receive a response. If you transfer your experience, we must receive the guest's name prior to arrival.
            </p>
            
            <p style="margin-top: 25px;">
                We're so excited to welcome you to the ranch and share the magic of our animals and their farm with you. Thank you for helping us keep our doors open by being a thoughtful steward of small farm experiences in our beautiful area.
            </p>
            <p style="margin-top: 15px;">
                When you arrive, turn left at the Parking Sign and show your QR Pass to the gatekeeper, who will direct you to the parking area. Have fun!
            </p>
            <p>Warmly,<br>Spencer Howe</p>
        </body>
    </html>


    """
    return html_content

