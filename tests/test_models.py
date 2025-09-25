import pytest
from datetime import datetime, timedelta
from eventapp.models import User, Event, Booking, Waiver
from eventapp import db


class TestUserModel:
    def test_user_creation(self, app, test_user):
        assert test_user.username == "testuser"
        assert test_user.password == "testpass"
        assert test_user.id is not None

    def test_user_events_relationship(self, app, test_user, test_event):
        assert test_event in test_user.events


class TestEventModel:
    def test_event_creation(self, app, test_event):
        assert test_event.title == "Test Event"
        assert test_event.price_per_ticket == 25.0
        assert test_event.private == False
        assert test_event.is_booked == False

    def test_event_future_date(self, app, test_event):
        assert test_event.start > datetime.utcnow()

    def test_private_event_pricing(self, app, test_user):
        with app.app_context():
            private_event = Event(
                title="Private Experience",
                start=datetime.utcnow() + timedelta(days=2),
                end=datetime.utcnow() + timedelta(days=2, hours=2),
                description="Private test",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(private_event)
            db.session.commit()
            
            assert private_event.title == "Private Experience"
            assert private_event.is_private == True


class TestBookingModel:
    def test_booking_creation(self, app, test_booking):
        assert test_booking.tickets == 2
        assert test_booking.amount_paid == 50.0
        assert test_booking.status == "COMPLETED"
        assert test_booking.name == "Test Customer"
        assert test_booking.reminder_sent == False

    def test_booking_serialize(self, app, test_booking):
        serialized = test_booking.serialize()
        assert serialized['tickets'] == 2
        assert serialized['amount_paid'] == 50.0
        assert serialized['status'] == "COMPLETED"
        assert serialized['title'] == "Test Customer"


class TestWaiverModel:
    def test_waiver_creation(self, app):
        with app.app_context():
            waiver = Waiver(
                order_id="TEST-WAIVER-123",
                signature="Test Signature",
                signed_date=datetime.utcnow()
            )
            db.session.add(waiver)
            db.session.commit()
            
            assert waiver.order_id == "TEST-WAIVER-123"
            assert waiver.signature == "Test Signature"
            assert waiver.signed_date is not None