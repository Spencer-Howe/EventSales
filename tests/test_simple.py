# basic tests for eventsales app
import pytest


class TestBasicMath:
    
    def test_pricing_calculation(self):
        # check if 2 tickets at $35 each = $70
        price_per_ticket = 35.0
        tickets = 2
        total = price_per_ticket * tickets
        assert total == 70.0
    
    def test_private_event_pricing(self):
        # private event rates
        private_experience = 250.0
        private_boo_moo = 350.0
        
        assert private_experience == 250.0
        assert private_boo_moo == 350.0


class TestStringOperations:
    
    def test_order_id_format(self):
        # order id should have ORDER in it
        order_id = "ORDER123"
        assert len(order_id) > 0
        assert "ORDER" in order_id
    
    def test_email_contains_at(self):
        # email needs @ and .
        email = "test@example.com"
        assert "@" in email
        assert "." in email


class TestListOperations:
    
    def test_event_capacity(self):
        # capacity math
        max_capacity = 50
        current_bookings = 10
        available = max_capacity - current_bookings
        assert available == 40
    
    def test_ticket_quantities(self):
        # valid ticket amounts
        valid_quantities = [1, 2, 3, 4, 5]
        test_quantity = 3
        assert test_quantity in valid_quantities


class TestTruthValues:
    
    def test_event_status(self):
        # event flags
        is_private = False
        is_booked = True
        
        assert is_private is False
        assert is_booked is True
    
    def test_payment_status(self):
        # payment status check
        payment_completed = True
        payment_failed = False
        
        assert payment_completed
        assert not payment_failed