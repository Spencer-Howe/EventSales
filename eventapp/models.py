
from eventapp import db
from flask_login import UserMixin



#user model
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
    private = db.Column(db.Boolean, nullable=False, default=False)
    is_private = db.Column(db.Boolean, nullable=True, default=False)
    is_booked = db.Column(db.Boolean, nullable=True, default=False)
    max_capacity = db.Column(db.Integer, nullable=False, default=50)
    event_type = db.Column(db.String(50), nullable=True, default='open_farm')
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('events', lazy=True))
    bookings = db.relationship('Booking', backref='event', lazy=True)

# Customer model - normalized customer data
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    waivers = db.relationship('Waiver', backref='customer', lazy=True)

# Booking model - links customer to event
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(120), unique=True, nullable=False)
    tickets = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.DateTime, default=db.func.now())
    reminder_sent = db.Column(db.Boolean, default=False)
    checked_in = db.Column(db.Boolean, default=False)
    checkin_time = db.Column(db.DateTime, nullable=True)
    receipt_sent = db.Column(db.Boolean, default=False, nullable=False)
    #. New DB column: photo_followup_sent (boolean, default false)
    photo_followup_sent = db.Column(db.Boolean, default=False, nullable=True)
    
    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    
    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy=True)

# Payment model - separate payment details
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_paid = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    status = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_date = db.Column(db.DateTime, default=db.func.now())
    
    # PayPal specific
    paypal_order_id = db.Column(db.String(120), nullable=True)
    
    # Crypto specific
    crypto_currency = db.Column(db.String(10), nullable=True)
    crypto_address = db.Column(db.String(200), nullable=True)
    transaction_hash = db.Column(db.String(200), nullable=True)
    
    # Foreign key
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)

# Waiver model - updated to use customer relationship
class Waiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(120), nullable=False)
    signature = db.Column(db.String(500), nullable=False)
    signed_date = db.Column(db.DateTime, nullable=False)
    
    # Foreign key
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)