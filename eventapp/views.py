import os
import requests
from datetime import datetime
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

@views.route('/calculate_price', methods=['POST'])
def calculate_price():
    from eventapp.models import Event
    event_id = request.form['event_id']
    tickets_str = request.form.get('tickets')
    paypal_client_id = current_app.config['PAYPAL_CLIENT_ID']

    try:
        tickets = int(tickets_str)
    except (ValueError, TypeError):
        tickets = 0

    # Query the event from the database
    event = Event.query.filter_by(id=event_id).first()
    error_message = None
    if event:
        readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
        readable_time_slot = f'{event.title} - {readable_start}'
        if event.title in ["Private Experience"]:
            if tickets <= 10:
                total_price = 250

            else:
                error_message = ("For groups larger than 10, please contact us to book a special event.")
                total_price = None  # Optional: Set `total_price` to None or handle it differently
        else:
            total_price = tickets * event.price_per_ticket


# Pass the title and description to the template
        event_title = event.title
        event_description = event.description

        session['event_id'] = event_id  # Store event ID only
        session['tickets'] = tickets
    else:
        readable_time_slot = 'Unknown Time Slot'
        total_price = 0
        event_title = 'Unknown Event'
        event_description = 'No description available'

    # Render the template and pass the required data
    return render_template('some_template.html',
                           time_slot=readable_time_slot,
                           tickets=tickets,
                           total_price=total_price,
                           paypal_client_id=paypal_client_id,
                           event_title=event_title,
                           event_description=event_description,
                            error_message=error_message)



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
    event = Event.query.get_or_404(event_id)

    session['event_id'] = event.id
    session['tickets'] = tickets

    # Calculate the total price
    total_price = tickets * event.price_per_ticket

    # Format the event start time
    readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
    readable_time_slot = f'{event.title} - {readable_start}'

    # Pass event_id, event_title, event_description, and other details to the template
    event_description = event.description  # Fetch event description from the database
    return render_template('some_template.html',
                           event_id=event.id,  # Pass event ID
                           event_title=event.title,  # Pass event title
                           event_description=event_description,  # Pass event description
                           time_slot=readable_time_slot,  # Pass formatted time slot
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
        session['phone'] = phone
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
    access_token = get_paypal_access_token()
    if not access_token:
        return "Failed to obtain access token", 500
    verified, order_details = verify_order_with_paypal(order_id, access_token)
    if verified:
        event_id = session.get('event_id')
        tickets = session.get('tickets')
        phone = session.get('phone')
        session.pop('event_id', None)
        session.pop('tickets', None)
        session.pop('phone', None)
        event = Event.query.filter_by(id=event_id).first()
        if not event:
            return "Event not found", 404
        if event.is_private:
            event.is_booked = True
        time_slot = event.start
        payer_info = order_details.get('payer', {})
        name = f"{payer_info.get('name').get('given_name')} {payer_info.get('name').get('surname')}"
        email = payer_info.get('email_address')
        amount = order_details['purchase_units'][0]['amount']['value']
        currency = order_details['purchase_units'][0]['amount']['currency_code']
        status = order_details.get('status')
        new_booking = Booking(
            time_slot=time_slot,
            tickets=tickets,
            order_id=order_id,
            amount_paid=amount,
            currency=currency,
            status=status,
            name=name,
            email=email,
            phone=phone,
            reminder_sent=False)
        db.session.add(new_booking)
        db.session.commit()
        email_order_details = {
            'name': name,
            'email': email,
            'phone': phone,
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'status': status,
            'time_slot': time_slot,
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
        # noinspection PyUnresolvedReferences
        return render_template('receipt.html', order_id=order_id, name=name, email=email,
                               time_slot=time_slot, tickets=tickets, amount=amount,
                               currency=currency, status=status, phone=phone)
    else:
        return "Verification failed or order not completed", 400



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
