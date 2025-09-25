import pytest
import json
from datetime import datetime, timedelta
from eventapp.models import Event, User
from eventapp import db


class TestRealPricingCalculation:
    """Test the actual pricing calculation endpoint with real scenarios"""
    
    def test_public_event_price_calculation_endpoint(self, client, app, test_user):
        """Test /calculate_price endpoint with public events"""
        with app.app_context():
            # Create a public event
            event = Event(
                title="Open Farm Day",
                start=datetime.utcnow() + timedelta(days=1),
                end=datetime.utcnow() + timedelta(days=1, hours=2),
                description="Public event",
                price_per_ticket=15.0,
                private=False,
                is_private=False,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            

            test_cases = [
                (1, 15.0),   # 1 ticket × $15 = $15
                (2, 30.0),   # 2 tickets × $15 = $30  
                (5, 75.0),   # 5 tickets × $15 = $75
                (10, 150.0), # 10 tickets × $15 = $150
            ]
            
            for tickets, expected_total in test_cases:
                response = client.post('/calculate_price', data={
                    'event_id': event.id,
                    'tickets': str(tickets)
                })
                
                assert response.status_code == 200
                # calculated price
                
    def test_private_experience_pricing_endpoint(self, client, app, test_user):
        """Test /calculate_price with Private Experience - should be $250 flat rate"""
        with app.app_context():
            # Create priv tour 24 hour ahead
            event = Event(
                title="Private Experience",
                start=datetime.utcnow() + timedelta(days=2),  # 48 hours ahead
                end=datetime.utcnow() + timedelta(days=2, hours=2),
                description="Private experience",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            # Test
            for group_size in [1, 3, 5, 8, 10]:
                response = client.post('/calculate_price', data={
                    'event_id': event.id,
                    'tickets': str(group_size)
                })
                
                assert response.status_code == 200
                # Should show $250 regardless of group size
                assert b'250' in response.data or b'$250' in response.data
                
    def test_private_boo_moo_pricing_endpoint(self, client, app, test_user):
        """Test /calculate_price with Private Boo & Moo - should be $350 flat rate"""
        with app.app_context():
            event = Event(
                title="Private Boo & Moo",
                start=datetime.utcnow() + timedelta(days=2),
                end=datetime.utcnow() + timedelta(days=2, hours=2),
                description="Private boo & moo",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            # Test that any group size ≤ 10 gets $350 flat rate
            for group_size in [1, 4, 7, 10]:
                response = client.post('/calculate_price', data={
                    'event_id': event.id,
                    'tickets': str(group_size)
                })
                
                assert response.status_code == 200
                # Should show $350 regardless of group size
                assert b'350' in response.data or b'$350' in response.data
                
    def test_private_event_too_soon_error(self, client, app, test_user):
        """Test that private events < 24 hours show error message"""
        with app.app_context():
            # test the 24 hours ahead
            event = Event(
                title="Private Experience",
                start=datetime.utcnow() + timedelta(hours=12),  # Only 12 hours ahead
                end=datetime.utcnow() + timedelta(hours=14),
                description="Too soon",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            response = client.post('/calculate_price', data={
                'event_id': event.id,
                'tickets': '5'
            })
            
            assert response.status_code == 200
            # errors
            assert b'must be booked at least 24 hours in advance' in response.data
            
    def test_private_event_group_too_large_error(self, client, app, test_user):
        """Test that private events > 10 people show error message"""
        with app.app_context():
            event = Event(
                title="Private Experience",
                start=datetime.utcnow() + timedelta(days=2),
                end=datetime.utcnow() + timedelta(days=2, hours=2),
                description="Group too large",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            # too big test
            response = client.post('/calculate_price', data={
                'event_id': event.id,
                'tickets': '15'  # Too much
            })
            
            assert response.status_code == 200
            # Should contain error message about group size limit
            assert b'limited to groups of 10 or fewer' in response.data


class TestCheckoutFlow:
    """Test the actual checkout process with real pricing"""
    
    def test_checkout_preserves_pricing(self, client, app, test_user):
        """Test that checkout page shows correct calculated prices"""
        with app.app_context():
            event = Event(
                title="Test Checkout Event",
                start=datetime.utcnow() + timedelta(days=1),
                end=datetime.utcnow() + timedelta(days=1, hours=2),
                description="Checkout test",
                price_per_ticket=25.0,
                private=False,
                is_private=False,
                is_booked=False,
                user_id=test_user.id
            )
            db.session.add(event)
            db.session.commit()
            
            # calc
            response = client.post('/calculate_price', data={
                'event_id': event.id,
                'tickets': '3'
            })
            assert response.status_code == 200
            
            # checkout
            response = client.get(f'/checkout?event_id={event.id}&tickets=3')
            assert response.status_code == 200
            
            # Should show correct total (3 × $25 = $75)
            assert b'75' in response.data or b'$75' in response.data


class TestEventAvailability:
    """Test which events show up in the public listing"""
    
    def test_get_events_excludes_private_events(self, client, app, test_user):
        """Test that /get_events only returns public events"""
        with app.app_context():
            #populate test db
            public_event = Event(
                title="Public Event",
                start=datetime.utcnow() + timedelta(days=1),
                end=datetime.utcnow() + timedelta(days=1, hours=2),
                description="Public",
                price_per_ticket=20.0,
                private=False,
                is_private=False,
                is_booked=False,
                user_id=test_user.id
            )
            
            private_event = Event(
                title="Private Event",
                start=datetime.utcnow() + timedelta(days=2),
                end=datetime.utcnow() + timedelta(days=2, hours=2),
                description="Private",
                price_per_ticket=0.0,
                private=True,
                is_private=True,
                is_booked=False,
                user_id=test_user.id
            )
            
            booked_event = Event(
                title="Booked Event",
                start=datetime.utcnow() + timedelta(days=3),
                end=datetime.utcnow() + timedelta(days=3, hours=2),
                description="Already booked",
                price_per_ticket=15.0,
                private=False,
                is_private=False,
                is_booked=True,  # booked
                user_id=test_user.id
            )
            
            db.session.add(public_event)
            db.session.add(private_event)
            db.session.add(booked_event)
            db.session.commit()
            
            # only unbooked back
            response = client.get('/get_events')
            assert response.status_code == 200
            
            events = json.loads(response.data)
            
            # 1 event
            assert len(events) == 1
            assert events[0]['title'] == 'Public Event'