"""
Event Type System - Clean polymorphic approach for different event types
"""
from .extensions import db
from datetime import datetime, timedelta


class EventType:
    """Base event type with default behavior"""
    
    def get_price(self, event, tickets):
        """Default pricing: tickets * price_per_ticket"""
        return tickets * event.price_per_ticket
    
    def check_capacity(self, event, tickets):
        """Default capacity checking for regular events"""
        from .models import Booking, Payment
        
        # For open farm days: Limit to one family unit per booking
        if tickets > 7:
            return False, "One family unit per booking, no large groups due to liability. If your immediate family is more than 7 please contact us for an exception."
        
        # Get current bookings - count total tickets
        current_bookings = db.session.query(db.func.sum(Booking.tickets)).join(Payment).filter(
            Booking.event_id == event.id,
            Payment.status == 'COMPLETED'
        ).scalar() or 0
        
        # Check if already at capacity
        if current_bookings >= event.max_capacity:
            return False, "Sorry, this event has reached capacity, please check our other offerings."
        
        # Check if this booking would put us over capacity
        final_bookings = current_bookings + tickets
        if final_bookings > event.max_capacity:
            return False, "Sorry, this event has reached capacity, please check our other offerings."
        
        return True, None
    
    def process_tickets(self, tickets):
        """Process ticket count - default is no change"""
        return tickets


class PrivateEventType(EventType):
    """Private event type with flat rate pricing"""
    
    def get_price(self, event, tickets):
        """Private events: flat $350 rate regardless of ticket count"""
        return 350
    
    def check_capacity(self, event, tickets):
        """Private events: 24hr notice required, max 10 guests"""
        # Check guest count limit
        if tickets > 10:
            return False, "Private events accommodate up to 10 guests maximum. Please contact us for larger groups."
        
        # Check 24-hour advance booking requirement
        import pytz
        pacific_tz = pytz.timezone('America/Los_Angeles')
        now = datetime.now(pacific_tz).replace(tzinfo=None)
        if event.start <= now + timedelta(hours=24):
            return False, "Private events require at least 24 hours advance notice due to staffing."
        
        return True, None


class HolidayMinisEventType(EventType):
    """Holiday Minis event type - flat rate, special capacity handling"""
    
    def get_price(self, event, tickets):
        """Holiday Minis: flat $350 rate regardless of ticket count"""
        return 350
    
    def check_capacity(self, event, tickets):
        """Holiday Minis: each booking = 1 slot, max 10 guests per booking"""
        from .models import Booking, Payment
        
        # Max 10 guests per booking
        if tickets > 10:
            return False, "Holiday Minis accommodate up to 10 guests maximum per booking."
        
        # Count number of completed bookings (each booking = 1 slot)
        current_bookings_count = db.session.query(db.func.count(Booking.id)).join(Payment).filter(
            Booking.event_id == event.id,
            Payment.status == 'COMPLETED'
        ).scalar() or 0
        
        if current_bookings_count >= event.max_capacity:
            return False, "Sorry, this Holiday Minis session has reached capacity."
        
        return True, None
    
    def process_tickets(self, tickets):
        """Holiday Minis: always store as 1 ticket regardless of guest count"""
        return 1


def get_event_type(event):
    """Factory function to determine event type"""
    if "Holiday Minis" in event.title:
        return HolidayMinisEventType()
    elif event.is_private:
        return PrivateEventType()
    else:
        return EventType()