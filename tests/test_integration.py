import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from eventapp.models import Event, Booking, User
from eventapp import db


class TestBookingFlow:
    """Integration tests for the complete booking flow"""
    
    def test_complete_booking_flow(self, client, app, test_user):
        """Test the complete flow from event selection to booking confirmation"""
        with app.app_context():
            # Create a future event
            event = Event(
                title="Integration Test Event",
                start=datetime.utcnow() + timedelta(days=1),
                end=datetime.utcnow() + timedelta(days=1, hours=2),
                description="Test event for integration",
                price_per_ticket=30.0,
                private=False,
                is_private=False,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            # Step 1: Get available events
            response = client.get('/get_events')
            assert response.status_code == 200
            events = json.loads(response.data)
            assert len(events) == 1
            
            # Step 2: Calculate price
            response = client.post('/calculate_price', data={
                'event_id': event.id,
                'tickets': '2'
            })
            assert response.status_code == 200
            
            # Step 3: Go to checkout
            response = client.get(f'/checkout?event_id={event.id}&tickets=2')
            assert response.status_code == 200

    @patch('eventapp.views.get_paypal_access_token')
    @patch('eventapp.views.verify_order_with_paypal')
    @patch('eventapp.views.mail.send')
    def test_payment_to_booking_creation(self, mock_mail, mock_verify, mock_token, client, app, test_event):
        """Test payment verification creates booking and sends emails"""
        with app.app_context():
            # Mock PayPal responses
            mock_token.return_value = "fake_token"
            mock_verify.return_value = (True, {
                'status': 'COMPLETED',
                'payer': {
                    'name': {'given_name': 'Jane', 'surname': 'Smith'},
                    'email_address': 'jane@example.com'
                },
                'purchase_units': [{
                    'amount': {'value': '50.00', 'currency_code': 'USD'}
                }]
            })
            
            # Set session data (simulating checkout)
            with client.session_transaction() as sess:
                sess['event_id'] = test_event.id
                sess['tickets'] = 2
                sess['phone'] = '555-1234'
            
            # Verify transaction
            response = client.post('/verify_transaction', 
                json={'orderID': 'INTEGRATION-TEST-123', 'phone': '555-1234'})
            assert response.status_code == 200
            
            # Get receipt (creates booking)
            response = client.get('/receipt/INTEGRATION-TEST-123')
            assert response.status_code == 200
            
            # Verify booking was created
            booking = Booking.query.filter_by(order_id='INTEGRATION-TEST-123').first()
            assert booking is not None
            assert booking.tickets == 2
            assert booking.name == "Jane Smith"
            assert booking.email == "jane@example.com"
            
            # mock email
            mock_mail.assert_called()


class TestAdminFlow:
    """Integration tests for admin functionality"""
    
    def test_admin_login_and_event_management(self, client, test_user):
        """Test admin can login and access admin functions"""
        # Login as admin
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        assert response.status_code == 302
        

        
    def test_booking_detail_access(self, client, test_user, test_booking):
        """Test admin can access booking details"""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Access booking detail
        response = client.get(f'/admin/booking/{test_booking.id}')
        assert response.status_code == 200


class TestPrivateEventFlow:
    """Integration tests for private event booking"""
    
    def test_private_event_pricing_flow(self, client, app, test_user):
        """Test private event has different pricing logic"""
        with app.app_context():
            # Create private event
            private_event = Event(
                title="Private Boo & Moo",
                start=datetime.utcnow() + timedelta(days=2),
                end=datetime.utcnow() + timedelta(days=2, hours=2),
                description="Private event test",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(private_event)
            db.session.commit()
            
            # Test pricing for private event (should be flat rate)
            response = client.post('/calculate_price', data={
                'event_id': private_event.id,
                'tickets': '8'  # Under 10 limit
            })
            assert response.status_code == 200
            
            # Test over capacity
            response = client.post('/calculate_price', data={
                'event_id': private_event.id,
                'tickets': '12'  # Over 10 limit
            })
            assert response.status_code == 200


class TestErrorHandling:
    """Integration tests for error conditions"""
    
    def test_invalid_event_id(self, client):
        """Test handling of invalid event ID"""
        response = client.get('/checkout?event_id=99999&tickets=2')
        assert response.status_code == 404
        
    def test_invalid_booking_id(self, client, test_user):
        """Test handling of invalid booking ID"""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        response = client.get('/admin/booking/99999')
        assert response.status_code == 404
        
    @patch('eventapp.views.get_paypal_access_token')
    def test_paypal_failure_handling(self, mock_token, client):
        """Test handling of PayPal API failures"""
        mock_token.return_value = None
        
        response = client.post('/verify_transaction', 
            json={'orderID': 'TEST-FAIL-123', 'phone': '555-1234'})
        assert response.status_code == 500