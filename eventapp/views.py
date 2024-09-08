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

    event = Event.query.filter_by(id=event_id).first()

    if event:
        readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
        readable_time_slot = f'{event.title} - {readable_start}'
        total_price = tickets * event.price_per_ticket
        session['event_id'] = event_id  # Store event ID only
        session['tickets'] = tickets
    else:
        readable_time_slot = 'Unknown Time Slot'
        total_price = 0

    # noinspection PyUnresolvedReferences
    return render_template('some_template.html', time_slot=readable_time_slot, tickets=tickets,
                           total_price=total_price, paypal_client_id=paypal_client_id)



@views.route('/select_tickets')
def select_tickets():
    paypal_client_id = current_app.config['PAYPAL_CLIENT_ID']
    # noinspection PyUnresolvedReferences
    return render_template(
        'select_tickets.html',
        paypal_client_id=paypal_client_id
    )
@views.route('/select_easter')
def select_easter():
    # noinspection PyUnresolvedReferences
    return render_template('select_easter.html')


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
            phone=phone)
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
    events = Event.query.all()
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
        <body>
            <h1>Payment Receipt</h1>
            <p><strong>Name:</strong> {order_details['name']}</p>
            <p><strong>Email:</strong> {order_details['email']}</p>
            <p>Phone Number: {order_details['phone']}<p>
            <p>Order ID: {order_details['order_id']}</p>
            <p>Total Amount: {order_details['amount']}</p>
            <p>Currency: {order_details['currency']}</p>
            <p>Status: {order_details['status']}</p>
            <p>Time slot: {order_details['time_slot']}</p>
            <p>Number of Tickets: {order_details['tickets']}</p>
            <p>Please review and sign the waiver if you did not already finish the registration after checkout<a href="{order_details['waiver_url']}">here</a>.</p>
        </body>
    </html>
    """
    return html_content
