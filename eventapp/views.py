import os
import requests
from datetime import datetime, timedelta
from flask import jsonify, render_template, request, redirect, url_for, session, Blueprint, current_app
from flask_mail import Message
from flask_login import login_user, logout_user, login_required
# noinspection PyUnresolvedReferences
from .extensions import db, mail, login_manager




views = Blueprint('views', __name__)




@views.route('/api/bookings')
def bookings():
    from eventapp.models import Booking
    bookings = Booking.query.all()
    return jsonify([b.serialize() for b in bookings])
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
        tickets = int(float(tickets))  # Convert to float first, then cast to int
    except (ValueError, TypeError):
        tickets = 0  # Default to 0 if there's an issue with conversion

    # Query the event from the database
    from .models import Event
    from .pricing import get_total_price, get_booking_summary
    
    event = Event.query.get_or_404(event_id)

    # Calculate the total price using pricing module
    total_price = get_total_price(event, tickets)

    # Get formatted booking summary
    booking_summary = get_booking_summary(event, tickets, total_price)

    # Pass all details to the template
    return render_template('some_template.html',
                           event_id=event.id,
                           event_title=booking_summary['event_title'],
                           event_description=booking_summary['event_description'],
                           time_slot=booking_summary['time_slot'],
                           tickets=tickets,
                           total_price=total_price,
                           paypal_client_id=current_app.config['PAYPAL_CLIENT_ID'])


@views.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    data = request.get_json()
    phone = data.get('phone')
    order_id = request.json.get('orderID')
    access_token = get_paypal_access_token()
    if not access_token:
        return jsonify({"verified": False, "reason": "Failed to obtain access token"}), 500
    verified, order_details = verify_order_with_paypal(order_id, access_token)
    if verified:
        # No longer storing in session - phone will be passed via URL parameters
        return jsonify({"verified": True, "orderID": order_id, "details": order_details})
    else:
        return jsonify({"verified": False, "reason": "Verification failed or order not completed"}), 400


@views.route('/waiver/<order_id>', methods=['GET', 'POST'])
def sign_waiver(order_id):
    from eventapp.models import Waiver
    if request.method == 'POST':
        signature = request.form.get('signature')
        new_waiver = Waiver(order_id=order_id, signature=signature, signed_date=datetime.utcnow())
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
    from eventapp.models import Booking, Event
    
    # Check if this booking already exists in database (crypto or existing PayPal)
    existing_booking = Booking.query.filter_by(order_id=order_id).first()
    if existing_booking:
        # This is a completed booking - show receipt from database
        return render_template('receipt.html', 
                             order_id=existing_booking.order_id,
                             name=existing_booking.name,
                             email=existing_booking.email,
                             time_slot=existing_booking.time_slot,
                             tickets=existing_booking.tickets,
                             amount=existing_booking.amount_paid,
                             currency=existing_booking.currency,
                             status=existing_booking.status,
                             phone=existing_booking.phone)
    
    # No existing booking found - this must be a new PayPal payment
    # Verify with PayPal and create booking if valid
    access_token = get_paypal_access_token()
    if not access_token:
        return "Failed to obtain access token", 500
    
    verified, order_details = verify_order_with_paypal(order_id, access_token)
    if verified:
        # Get event_id and tickets from URL parameters
        event_id = request.args.get('event_id')
        tickets = request.args.get('tickets')
        phone = request.args.get('phone')
        user_email = request.args.get('email')  # Optional user-provided email
        
        if not event_id or not tickets:
            return "Missing booking details", 400
            
        try:
            tickets = int(tickets)
        except (ValueError, TypeError):
            return "Invalid ticket count", 400
            
        event = Event.query.filter_by(id=event_id).first()
        if not event:
            return "Event not found", 404
        
        # Create new booking from PayPal details
        payer_info = order_details.get('payer', {})
        name = f"{payer_info.get('name').get('given_name')} {payer_info.get('name').get('surname')}"
        paypal_email = payer_info.get('email_address')
        # Use user-provided email if provided
        email = user_email if user_email else paypal_email
        amount = order_details['purchase_units'][0]['amount']['value']
        currency = order_details['purchase_units'][0]['amount']['currency_code']
        status = order_details.get('status')
        
        new_booking = Booking(
            time_slot=event.start,
            tickets=tickets,
            order_id=order_id,
            amount_paid=amount,
            currency=currency,
            status=status,
            name=name,
            email=email,
            phone=phone,
            reminder_sent=False,
            payment_method='paypal'
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        # Send confirmation email
        email_order_details = {
            'name': name,
            'email': email,
            'phone': phone,
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'status': status,
            'time_slot': event.start,
            'tickets': tickets
        }
        
        waiver_url = url_for('views.sign_waiver', order_id=order_id, _external=True)
        email_order_details['waiver_url'] = waiver_url
        html_content = create_receipt_email_content(email_order_details)
        subject = "Your Payment Receipt"
        sender = current_app.config['MAIL_USERNAME']
        recipients = [email, sender]
        msg = Message(subject, sender=sender, recipients=recipients, html=html_content)
        mail.send(msg)
        
        # Show receipt
        return render_template('receipt.html', 
                             order_id=order_id,
                             name=name,
                             email=email,
                             time_slot=event.start,
                             tickets=tickets,
                             amount=amount,
                             currency=currency,
                             status=status,
                             phone=phone)
    else:
        return "PayPal verification failed or payment not completed", 400



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
            <hr style="margin: 30px 0;">
            <h2 style="color: #2e6c80;">Thank You & Important Visit Information</h2>
            <p>
                Thank you for purchasing passes to the <strong>Mini Moos experience</strong> at Howe Ranch! You’re officially on our guest list—just identify yourself at the welcome table when you arrive. 
                Our event is held at:
            </p>
            <p>
                <strong>22053 Highland St<br>
                Wildomar, CA 92595</strong>
            </p>
            <p>
                To help us ensure a smooth, safe, and enjoyable experience for all our guests and animals, please take a moment to review the visit guidelines below:
            </p>
            <ul style="padding-left: 20px;">
                <li>
                    <strong>Arrival Time:</strong><br>
                    Please do <strong>not arrive earlier than your reserved time slot at {order_details['time_slot']}</strong>. Early arrivals are not permitted, as we are actively preparing the animals and property for your visit.<br><br>
                    Please <strong>do not stage on the private road</strong>, as this creates a safety and liability concern.
                </li>
                <br>
                <li>
                    <strong>Best Time to Arrive:</strong><br>
                    Animal interactions are available throughout your reserved window. Most guests find the sweet spot is arriving about 15–30 minutes after the start time to enjoy the full experience.
                </li>
                <br>
                <li>
                    <strong>Parking:</strong><br>
                    Enter through the red gate <strong>after your start time</strong> and take the left at the welcome sign.
                </li>
                <br>
                <li>
    			<strong>What to Bring:</strong><br>
    			Be sure to bring drinking water, wear closed-toed shoes, and dress comfortably for walking around the farm.
		        </li>

            </ul>
            <p>
                We’re so excited to welcome you to the ranch and share the magic of our animals with you. Thank you for helping us keep the experience safe and enjoyable for all.
            </p>
            <p>Warmly,<br>Spencer Howe</p>
        </body>
    </html>


    """
    return html_content

