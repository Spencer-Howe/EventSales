
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
    is_private = db.Column(db.Boolean, nullable=False, default=False)
    is_booked = db.Column(db.Boolean, nullable=False, default=False)

user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

user = db.relationship('User', backref=db.backref('events', lazy=True))

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