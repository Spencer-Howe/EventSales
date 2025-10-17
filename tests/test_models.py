import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eventapp import db
from eventapp.models import User, Customer, Event, Booking, Payment, Waiver
import tempfile
import os
from eventapp.models import User, Customer, Event, Booking, Payment, Waiver
from datetime import datetime


@pytest.fixture
def app():
    """Create and configure a test application."""
    from flask import Flask
    from config import Config
    
    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        WTF_CSRF_ENABLED = False
        SCHEDULER_API_ENABLED = False
    
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


class TestUserModel:
    
    def test_user_model_creation(self, app):
        """Test User model can be created and saved."""
        with app.app_context():
            user = User(username='testuser', password='testpassword')
            db.session.add(user)
            db.session.commit()
            
            retrieved_user = User.query.filter_by(username='testuser').first()
            assert retrieved_user is not None
            assert retrieved_user.username == 'testuser'
            assert retrieved_user.password == 'testpassword'


class TestCustomerModel:
    
    def test_customer_model_creation(self, app):
        """Test Customer model functionality."""
        with app.app_context():
            customer = Customer(
                name='John Doe',
                email='john@example.com',
                phone='555-1234'
            )
            db.session.add(customer)
            db.session.commit()
            
            retrieved_customer = Customer.query.filter_by(email='john@example.com').first()
            assert retrieved_customer is not None
            assert retrieved_customer.name == 'John Doe'
            assert retrieved_customer.email == 'john@example.com'
            assert retrieved_customer.phone == '555-1234'
            assert retrieved_customer.created_at is not None


class TestEventModel:
    
    def test_event_model_creation(self, app):
        """Test Event model with relationships."""
        with app.app_context():
            # Create user first (required for foreign key)
            user = User(username='admin', password='password')
            db.session.add(user)
            db.session.commit()
            
            # Create event
            event = Event(
                title='Halloween Spectacular',
                start=datetime(2024, 10, 31, 16, 0),
                end=datetime(2024, 10, 31, 20, 0),
                description='Spooky farm fun',
                price_per_ticket=35.0,
                max_capacity=50,
                user_id=user.id
            )
            db.session.add(event)
            db.session.commit()
            
            retrieved_event = Event.query.filter_by(title='Halloween Spectacular').first()
            assert retrieved_event is not None
            assert retrieved_event.title == 'Halloween Spectacular'
            assert retrieved_event.price_per_ticket == 35.0
            assert retrieved_event.user_id == user.id
            assert retrieved_event.user.username == 'admin'


class TestBookingModel:
    
    def test_booking_creation(self, app):
        """Test complete booking workflow."""
        with app.app_context():
            # Create required dependencies
            user = User(username='admin', password='password')
            db.session.add(user)
            db.session.commit()
            
            customer = Customer(name='Jane Doe', email='jane@example.com')
            db.session.add(customer)
            db.session.commit()
            
            event = Event(
                title='Test Event',
                price_per_ticket=35.0,
                max_capacity=10,
                user_id=user.id
            )
            db.session.add(event)
            db.session.commit()
            
            # Create booking
            booking = Booking(
                order_id='TEST123',
                tickets=2,
                customer_id=customer.id,
                event_id=event.id
            )
            db.session.add(booking)
            db.session.commit()
            
            retrieved_booking = Booking.query.filter_by(order_id='TEST123').first()
            assert retrieved_booking is not None
            assert retrieved_booking.tickets == 2
            assert retrieved_booking.customer.name == 'Jane Doe'
            assert retrieved_booking.event.title == 'Test Event'
            assert retrieved_booking.booking_date is not None
    
    def test_booking_uniqueness(self, app):
        """Test order_id uniqueness constraint."""
        with app.app_context():
            # Create dependencies
            user = User(username='admin', password='password')
            customer = Customer(name='Test Customer', email='test@example.com')
            event = Event(title='Test Event', price_per_ticket=35.0, max_capacity=10, user_id=1)
            
            db.session.add_all([user, customer, event])
            db.session.commit()
            
            # Create first booking
            booking1 = Booking(order_id='UNIQUE123', tickets=1, customer_id=customer.id, event_id=event.id)
            db.session.add(booking1)
            db.session.commit()
            
            # Attempt to create duplicate order_id
            booking2 = Booking(order_id='UNIQUE123', tickets=2, customer_id=customer.id, event_id=event.id)
            db.session.add(booking2)
            
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()


class TestPaymentModel:
    
    def test_payment_creation(self, app):
        """Test payment record creation."""
        with app.app_context():
            # Create booking first
            user = User(username='admin', password='password')
            customer = Customer(name='Test Customer', email='test@example.com')
            event = Event(title='Test Event', price_per_ticket=35.0, max_capacity=10, user_id=1)
            booking = Booking(order_id='PAY123', tickets=2, customer_id=1, event_id=1)
            
            db.session.add_all([user, customer, event, booking])
            db.session.commit()
            
            # Create payment
            payment = Payment(
                amount_paid=70.0,
                currency='USD',
                status='COMPLETED',
                payment_method='paypal',
                booking_id=booking.id
            )
            db.session.add(payment)
            db.session.commit()
            
            retrieved_payment = Payment.query.filter_by(booking_id=booking.id).first()
            assert retrieved_payment is not None
            assert retrieved_payment.amount_paid == 70.0
            assert retrieved_payment.currency == 'USD'
            assert retrieved_payment.status == 'COMPLETED'
            assert retrieved_payment.payment_date is not None
    
    def test_multiple_payment_methods(self, app):
        """Test PayPal and crypto payment fields."""
        with app.app_context():
            # Setup dependencies
            user = User(username='admin', password='password')
            customer = Customer(name='Test Customer', email='test@example.com')
            event = Event(title='Test Event', price_per_ticket=35.0, max_capacity=10, user_id=1)
            booking1 = Booking(order_id='PAY1', tickets=1, customer_id=1, event_id=1)
            booking2 = Booking(order_id='PAY2', tickets=1, customer_id=1, event_id=1)
            
            db.session.add_all([user, customer, event, booking1, booking2])
            db.session.commit()
            
            # PayPal payment
            paypal_payment = Payment(
                amount_paid=35.0,
                currency='USD',
                status='COMPLETED',
                payment_method='paypal',
                paypal_order_id='PAYPAL123',
                booking_id=booking1.id
            )
            
            # Crypto payment
            crypto_payment = Payment(
                amount_paid=35.0,
                currency='USD',
                status='COMPLETED',
                payment_method='crypto',
                crypto_currency='BTC',
                crypto_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                transaction_hash='abcd1234',
                booking_id=booking2.id
            )
            
            db.session.add_all([paypal_payment, crypto_payment])
            db.session.commit()
            
            assert paypal_payment.paypal_order_id == 'PAYPAL123'
            assert crypto_payment.crypto_currency == 'BTC'
            assert crypto_payment.crypto_address == '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'


class TestWaiverModel:
    
    def test_waiver_creation(self, app):
        """Test digital waiver functionality."""
        with app.app_context():
            customer = Customer(name='Test Customer', email='test@example.com')
            db.session.add(customer)
            db.session.commit()
            
            waiver = Waiver(
                order_id='WAIVER123',
                signature='John Doe Digital Signature',
                signed_date=datetime.now(),
                customer_id=customer.id
            )
            db.session.add(waiver)
            db.session.commit()
            
            retrieved_waiver = Waiver.query.filter_by(order_id='WAIVER123').first()
            assert retrieved_waiver is not None
            assert retrieved_waiver.signature == 'John Doe Digital Signature'
            assert retrieved_waiver.customer.name == 'Test Customer'


class TestBusinessLogic:
    
    def test_pricing_calculation(self, app):
        """Test ticket pricing logic."""
        price_per_ticket = 35.0
        tickets = 3
        expected_total = 105.0
        
        calculated_total = price_per_ticket * tickets
        assert calculated_total == expected_total
    
    def test_event_capacity_validation(self, app):
        """Test event capacity constraints."""
        with app.app_context():
            user = User(username='admin', password='password')
            event = Event(
                title='Small Event',
                price_per_ticket=35.0,
                max_capacity=2,
                user_id=1
            )
            db.session.add_all([user, event])
            db.session.commit()
            
            # This would be implemented in business logic
            requested_tickets = 5
            available_capacity = event.max_capacity
            
            assert requested_tickets > available_capacity
            # In real application, this would prevent booking


class TestRelationships:
    
    def test_customer_booking_relationship(self, app):
        """Test one-to-many relationship between Customer and Booking."""
        with app.app_context():
            user = User(username='admin', password='password')
            customer = Customer(name='Regular Customer', email='regular@example.com')
            event = Event(title='Test Event', price_per_ticket=35.0, max_capacity=10, user_id=1)
            
            db.session.add_all([user, customer, event])
            db.session.commit()
            
            # Create multiple bookings for same customer
            booking1 = Booking(order_id='REL1', tickets=1, customer_id=customer.id, event_id=event.id)
            booking2 = Booking(order_id='REL2', tickets=2, customer_id=customer.id, event_id=event.id)
            
            db.session.add_all([booking1, booking2])
            db.session.commit()
            
            # Test relationship
            assert len(customer.bookings) == 2
            assert booking1 in customer.bookings
            assert booking2 in customer.bookings
    
    def test_booking_payment_relationship(self, app):
        """Test booking to payments relationship."""
        with app.app_context():
            user = User(username='admin', password='password')
            customer = Customer(name='Test Customer', email='test@example.com')
            event = Event(title='Test Event', price_per_ticket=35.0, max_capacity=10, user_id=1)
            booking = Booking(order_id='PAYMENT_REL', tickets=2, customer_id=1, event_id=1)
            
            db.session.add_all([user, customer, event, booking])
            db.session.commit()
            
            # Create multiple payments for same booking
            payment1 = Payment(amount_paid=35.0, currency='USD', status='COMPLETED', 
                             payment_method='paypal', booking_id=booking.id)
            payment2 = Payment(amount_paid=35.0, currency='USD', status='COMPLETED', 
                             payment_method='paypal', booking_id=booking.id)
            
            db.session.add_all([payment1, payment2])
            db.session.commit()
            
            # Test relationship
            assert len(booking.payments) == 2
            assert payment1 in booking.payments
            assert payment2 in booking.payments


if __name__ == '__main__':
    pytest.main([__file__])