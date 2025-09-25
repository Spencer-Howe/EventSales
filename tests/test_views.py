import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from flask import url_for


class TestHomeRoutes:
    def test_home_page(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_get_events_api(self, client, test_event):
        response = client.get('/get_events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == 'Test Event'

    def test_bookings_api(self, client, test_booking):
        response = client.get('/api/bookings')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['tickets'] == 2


class TestAuthenticationRoutes:
    def test_login_page_get(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_success(self, client, test_user):
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        assert response.status_code == 302  # Redirect after successful login

    def test_login_failure(self, client):
        response = client.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        assert b'Invalid credentials' in response.data


class TestBookingRoutes:
    def test_checkout_page(self, client, test_event):
        response = client.get(f'/checkout?event_id={test_event.id}&tickets=2')
        assert response.status_code == 200

    def test_calculate_price_public_event(self, client, test_event):
        response = client.post('/calculate_price', data={
            'event_id': test_event.id,
            'tickets': '3'
        })
        assert response.status_code == 200

    def test_calculate_price_private_event(self, client, test_user, app):
        with app.app_context():
            from eventapp.models import Event
            from eventapp import db
            
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
            
            response = client.post('/calculate_price', data={
                'event_id': private_event.id,
                'tickets': '8'
            })
            assert response.status_code == 200


class TestWaiverRoutes:
    def test_waiver_form_get(self, client):
        response = client.get('/waiver/TEST-ORDER-123')
        assert response.status_code == 200

    def test_waiver_form_post(self, client, app):
        with patch('eventapp.views.mail.send') as mock_mail:
            response = client.post('/waiver/TEST-ORDER-123', data={
                'signature': 'Test Signature'
            })
            assert response.status_code == 302  # Redirect to thank you page
            mock_mail.assert_called_once()


class TestPayPalIntegration:
    @patch('eventapp.views.get_paypal_access_token')
    @patch('eventapp.views.verify_order_with_paypal')
    def test_verify_transaction_success(self, mock_verify, mock_token, client):
        mock_token.return_value = "fake_token"
        mock_verify.return_value = (True, {
            'status': 'COMPLETED',
            'payer': {
                'name': {'given_name': 'John', 'surname': 'Doe'},
                'email_address': 'john@example.com'
            },
            'purchase_units': [{
                'amount': {'value': '50.00', 'currency_code': 'USD'}
            }]
        })
        
        response = client.post('/verify_transaction', 
            json={'orderID': 'TEST-ORDER-123', 'phone': '555-1234'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['verified'] == True

    @patch('eventapp.views.get_paypal_access_token')
    def test_verify_transaction_no_token(self, mock_token, client):
        mock_token.return_value = None
        
        response = client.post('/verify_transaction', 
            json={'orderID': 'TEST-ORDER-123', 'phone': '555-1234'})
        assert response.status_code == 500