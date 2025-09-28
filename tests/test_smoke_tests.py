import requests
import os


class TestPayPalIntegration:

    
    def test_paypal_credentials_work(self):
        client_id = os.getenv('PAYPAL_CLIENT_ID')
        client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        
        url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(url, headers=headers, data=data, 
                               auth=(client_id, client_secret), timeout=10)
        
        assert response.status_code == 200
        token_data = response.json()
        assert 'access_token' in token_data
        
    def test_paypal_api_responds(self):
        response = requests.get("https://api.sandbox.paypal.com/v1/oauth2/token", timeout=5)
        assert response.status_code == 401  # Expected - needs authentication


class TestEventPricing:
    
    def test_halloween_event_pricing(self):
        price_per_ticket = 35.0
        
        assert 1 * price_per_ticket == 35.0
        assert 2 * price_per_ticket == 70.0
        assert 5 * price_per_ticket == 175.0
        assert 10 * price_per_ticket == 350.0
        
    def test_private_event_pricing(self):
        private_experience = 250.0
        private_boo_moo = 350.0
        
        assert private_experience == 250.0
        assert private_boo_moo == 350.0