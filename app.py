from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, BaseView, expose
from wtforms.fields import DateTimeLocalField
from wtforms import TextAreaField
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
from datetime import datetime
import requests

app = Flask(__name__)

# Load environment variables
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.local')

# App configuration
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_development_secret_key')
PAYPAL_API_BASE = os.getenv('PAYPAL_API_BASE')
# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('GMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_PASSWORD')
mail = Mail(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///yourdatabase.db')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
 
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    description = db.Column(db.Text)
    price_per_ticket = db.Column(db.Float, nullable=False, default=0.0)


# EventModelView for Flask-Admin
class EventModelView(ModelView):
    form_overrides = {
        'start': DateTimeLocalField,
        'end': DateTimeLocalField,
        'description': TextAreaField
    }
    form_args = {
        'start': {
            'format': '%Y-%m-%dT%H:%M'
        },
        'end': {
            'format': '%Y-%m-%dT%H:%M'
        }
    }
    form_columns = ['title', 'start', 'end', 'price_per_ticket', 'description']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Custom AdminIndexView
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class CalendarView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/calendar.html')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    


# Initialize Flask-Admin
admin = Admin(app, index_view=MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(EventModelView(Event, db.session, name='Event Model'))

admin.add_view(CalendarView(name='Calendar', endpoint='calendar'))

@app.route('/api/bookings')
def bookings():
    bookings = Booking.query.all()
    return jsonify([b.serialize() for b in bookings])
@app.route('/admin/booking/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('base1.html', booking=booking)

# Routes
@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/select_tickets')
def select_tickets():
    return render_template('select_tickets.html')

@app.route('/calculate_price', methods=['POST'])
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

    return render_template('some_template.html', time_slot=readable_time_slot, tickets=tickets, total_price=total_price,)

@app.route('/select_easter')
def select_easter():
    return render_template('select_easter.html')

@app.route('/verify_transaction', methods=['POST'])
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

@app.route('/receipt/<order_id>')
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
        new_booking = Booking(time_slot=convert_time_slot(time_slot), tickets=tickets, order_id=order_id, amount_paid=amount, currency=currency, status=status, name=name, email=email, phone=phone)
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
        sender = app.config['MAIL_USERNAME']
        recipients = [email, sender]
        msg = Message(subject, sender=sender, recipients=recipients, html=html_content)
        mail.send(msg)
        return render_template('receipt.html', order_id=order_id, name=name, email=email, time_slot=convert_time_slot(time_slot), tickets=tickets, amount=amount, currency=currency, status=status, phone=phone)
    else:
        return "Verification failed or order not completed", 400

@app.route('/waiver/<order_id>', methods=['GET', 'POST'])
def sign_waiver(order_id):
    if request.method == 'POST':
        signature = request.form.get('signature')
        new_waiver = Waiver(order_id=order_id, signature=signature, signed_date=datetime.utcnow())
        db.session.add(new_waiver)
        db.session.commit()
        subject = f"New Waiver Submitted: {order_id}"
        sender = app.config['MAIL_USERNAME']
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

@app.route('/thank_you')
def thank_you_page():
    return render_template('thank_you.html')

@app.route('/get_events')
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

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_slot = db.Column(db.DateTime(50), nullable=False)
    tickets = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.String(120), unique=True, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)

    def __init__(self, time_slot, tickets, order_id, amount_paid, currency, status, name, email, phone):
        self.time_slot = time_slot
        self.tickets = tickets
        self.order_id = order_id
        self.amount_paid = amount_paid
        self.currency = currency
        self.status = status
        self.name = name
        self.email = email
        self.phone = phone

    def serialize(self):
        return {
            'id': self.id,
            'start': self.time_slot,
            'tickets': self.tickets,
            'order_id': self.order_id,
            'amount_paid': self.amount_paid,
            'currency': self.currency,
            'status': self.status,
            'title': self.name,
            'email': self.email,
            'phone': self.phone
        }

class Waiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(120), unique=True, nullable=False)
    signature = db.Column(db.String(500), nullable=False)
    signed_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, order_id, signature, signed_date):
        self.order_id = order_id
        self.signature = signature
        self.signed_date = signed_date

def convert_time_slot(time_slot_code):
    event = Event.query.filter_by(id=time_slot_code).first()
    if event:
        return f'{event.title} - {event.start.isoformat()}'
    return 'Unknown Time Slot'

def get_paypal_access_token():
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, headers=headers, data=data, auth=(os.getenv('PAYPAL_CLIENT_ID'), os.getenv('PAYPAL_CLIENT_SECRET')))
    if response.status_code != 200:
        app.logger.error(f"Failed to get PayPal access token: {response.text}")
        return None
    return response.json().get('access_token')

def verify_order_with_paypal(order_id, access_token):
    url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}"
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
