import pytest
import os
from eventapp import create_app, db
from eventapp.models import User, Event, Booking, Waiver
from datetime import datetime, timedelta


@pytest.fixture
def app():
    os.environ['FLASK_ENV'] = 'testing'
    # Mock the scheduler functions to avoid issues during testing
    def mock_reminder_func(app):
        pass
    
    def mock_clear_func(app):
        pass
    
    app = create_app(check_and_send_reminders=mock_reminder_func, clear_old_bookings=mock_clear_func)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-key",
        "WTF_CSRF_ENABLED": False,
        "MAIL_SUPPRESS_SEND": True,
        "PAYPAL_CLIENT_ID": "test-paypal-id",
        "PAYPAL_CLIENT_SECRET": "test-paypal-secret",
        "PAYPAL_API_BASE": "https://api.sandbox.paypal.com"
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username="testuser", password="testpass")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_event(app, test_user):
    with app.app_context():
        event = Event(
            title="Test Event",
            start=datetime.utcnow() + timedelta(days=1),
            end=datetime.utcnow() + timedelta(days=1, hours=2),
            description="Test event description",
            price_per_ticket=25.0,
            private=False,
            is_private=False,
            is_booked=False,
            user_id=test_user.id
        )
        db.session.add(event)
        db.session.commit()
        return event


@pytest.fixture
def test_booking(app, test_event):
    with app.app_context():
        booking = Booking(
            time_slot=test_event.start,
            tickets=2,
            order_id="TEST-ORDER-123",
            amount_paid=50.0,
            currency="USD",
            status="COMPLETED",
            name="Test Customer",
            email="test@example.com",
            phone="555-1234",
            reminder_sent=False
        )
        db.session.add(booking)
        db.session.commit()
        return booking