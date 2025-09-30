"""
Pricing and capacity management logic
"""
from datetime import datetime, timedelta
from .extensions import db


class EventPricingService:
    """Service class for handling event pricing and capacity logic"""
    
    @staticmethod
    def is_private_event(event):
        """Check if event is a private event based on title"""
        private_titles = ["Private Experience", "Private Boo & Moo"]
        return event.title in private_titles
    
    @staticmethod
    def get_private_event_price(event):
        """Get pricing for private events"""
        if event.title == "Private Boo & Moo":
            return 350
        elif event.title == "Private Experience":
            return 250
        return None
    
    @staticmethod
    def validate_private_booking(event, tickets):

        now = datetime.utcnow()
        advance_requirement = now + timedelta(hours=24)
        
        if tickets > 10:
            return False, "Private Experiences are limited to groups of 10 or fewer. For larger groups, please contact us to arrange a special event."
        
        if event.start <= advance_requirement:
            return False, "Private Experiences must be booked at least 24 hours in advance."
            
        return True, None
    
    @staticmethod
    def get_current_bookings(event):
        from .models import Booking
        
        total = db.session.query(db.func.sum(Booking.tickets)).filter(
            Booking.time_slot == event.start,
            Booking.status == 'COMPLETED'
        ).scalar()
        return total or 0
    
    @staticmethod
    def check_capacity(event, requested_tickets):
        if EventPricingService.is_private_event(event):
            return True, None  # Private events don't use capacity system
            
        current_bookings = EventPricingService.get_current_bookings(event)
        available_spots = event.max_capacity - current_bookings
        
        # overage for cap logic
        overage_allowed = max(5, int(event.max_capacity * 0.1))
        max_total_capacity = event.max_capacity + overage_allowed
        
        # sold out?
        if available_spots <= 0:
            return False, f"Sorry, this event is sold out. Maximum capacity is {event.max_capacity}."
        
        # exceed max
        final_bookings = current_bookings + requested_tickets
        if final_bookings > max_total_capacity:
            return False, f"Sorry, your group of {requested_tickets} would exceed our safe capacity limit. We have {available_spots} spots remaining (capacity: {event.max_capacity})."
        
        return True, None
    
    @staticmethod
    def calculate_event_price(event, tickets):
        """Calculate total price for event booking"""
        # priv
        if EventPricingService.is_private_event(event):
            valid, error = EventPricingService.validate_private_booking(event, tickets)
            if not valid:
                return None, error
            
            price = EventPricingService.get_private_event_price(event)
            return price, None
        

        # Check capacity
        can_book, error = EventPricingService.check_capacity(event, tickets)
        if not can_book:
            return None, error
        
        # Calculate price
        total_price = tickets * event.price_per_ticket
        return total_price, None


class BookingService:

    
    @staticmethod
    def get_booking_summary(event, tickets, total_price):
       #booking summary
        readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
        readable_time_slot = f'{event.title} - {readable_start}'
        
        return {
            'time_slot': readable_time_slot,
            'event_title': event.title,
            'event_description': event.description,
            'tickets': tickets,
            'total_price': total_price
        }