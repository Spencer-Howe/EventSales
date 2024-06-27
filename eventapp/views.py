import os
import requests
from datetime import datetime
from flask import jsonify, render_template, request, redirect, url_for, session, Blueprint, current_app
from flask_mail import Message
from eventapp.models import Booking, User, Event, Waiver
from eventapp import db, mail

from flask_login import LoginManager, login_user, logout_user, login_required

views = Blueprint('views', __name__)

#admin
@views.route('/admin')
@login_required
def admin_home():
    return render_template('home.html')

@views.route('/api/bookings')
def bookings():
    bookings = Booking.query.all()
    return jsonify([b.serialize() for b in bookings])
@views.route('/admin/booking/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('base1.html', booking=booking)

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@views.route('/')
def index():
    return render_template('index')

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@views.route('/')
def home():
    return render_template('home.html')




@views.route('/calculate_price', methods=['POST'])
def calculate_price():
    time_slot_code = request.form.get('time_slot')
    tickets_str = request.form.get('tickets')
    try:
        tickets = int(tickets_str)
    except (ValueError, TypeError):
        tickets = 0

    event = Event.query.filter_by(id=time_slot_code).first()

    if event:
        try:
            readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
            readable_time_slot = f'{event.title} - {readable_start}'
            total_price = tickets * event.price_per_ticket
        except ValueError as e:
            print(f"Error parsing datetime: {e}")
            readable_time_slot = "Error in date format"
            total_price = 0
        session['time_slot'] = time_slot_code
        session['tickets'] = tickets
    else:
        readable_time_slot = 'Unknown Time Slot'
        total_price = 0

    return render_template('some_template.html', time_slot=readable_time_slot, tickets=tickets,
                           total_price=total_price, )


@views.route('/select_tickets')
def select_tickets():
    return render_template('select_tickets.html')
@views.route('/select_easter')
def select_easter():
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


@views.route('/receipt/<order_id>')
def show_receipt(order_id):
    access_token = get_paypal_access_token()
    if not access_token:
        return "Failed to obtain access token", 500
    verified, order_details = verify_order_with_paypal(order_id, access_token)
    if verified:
        time_slot = session.get('time_slot')
        tickets = session.get('tickets')
        phone = session.get('phone')
        session.pop('time_slot', None)
        session.pop('tickets', None)
        session.pop('phone', None)
        payer_info = order_details.get('payer', {})
        name = f"{payer_info.get('name').get('given_name')} {payer_info.get('name').get('surname')}"
        email = payer_info.get('email_address')
        amount = order_details['purchase_units'][0]['amount']['value']
        currency = order_details['purchase_units'][0]['amount']['currency_code']
        status = order_details.get('status')
        new_booking = Booking(time_slot=convert_time_slot(time_slot), tickets=tickets, order_id=order_id,
                              amount_paid=amount, currency=currency, status=status, name=name, email=email, phone=phone)
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
            'time_slot': convert_time_slot(time_slot),
            'tickets': tickets

        }
        waiver_url = url_for('sign_waiver', order_id=order_id, _external=True)
        email_order_details['waiver_url'] = waiver_url
        html_content = create_receipt_email_content(email_order_details)
        subject = "Your Payment Receipt"
        sender = current_app.config['MAIL_USERNAME']
        recipients = [email, sender]
        msg = Message(subject, sender=sender, recipients=recipients, html=html_content)
        mail.send(msg)
        return render_template('receipt.html', order_id=order_id, name=name, email=email,
                               time_slot=convert_time_slot(time_slot), tickets=tickets, amount=amount,
                               currency=currency, status=status, phone=phone)
    else:
        return "Verification failed or order not completed", 400

@views.route('/waiver/<order_id>', methods=['GET', 'POST'])
def sign_waiver(order_id):
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
        return redirect(url_for('thank_you_page'))
    return render_template('waiver_form.html', order_id=order_id)

@views.route('/thank_you')
def thank_you_page():
    return render_template('thank_you.html')

@views.route('/get_events')
def get_events():
    events = Event.query.all()
    events_data = [{
        'id': event.id,
        'title': event.title,
        'start': event.start.isoformat(),
        'end': event.end.isoformat(),
        'description': event.description
    } for event in events]
    return jsonify(events_data)


def convert_time_slot(time_slot_code):
    event = Event.query.filter_by(id=time_slot_code).first()
    if event:
        return f'{event.title} - {event.start.isoformat()}'
    return 'Unknown Time Slot'

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
