"""
Simple pricing logic - easy to extend
"""
from .extensions import db


def get_total_price(event, tickets):
    """Calculate total price for any event"""
    # Private events: flat $350 rate regardless of ticket count
    if event.is_private:
        return 350
    
    # Regular events: price per ticket
    return tickets * event.price_per_ticket


def check_capacity(event, tickets):
    """Check if booking fits capacity"""
    from .models import Booking, Payment
    from datetime import datetime, timedelta
    import pytz
    
    # Universal check: allow booking during event, prevent booking 6 hours after event starts
    pacific_tz = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pacific_tz).replace(tzinfo=None)  # Convert to naive datetime for comparison
    booking_cutoff = event.start + timedelta(hours=6) if event.start else None
    if booking_cutoff and now >= booking_cutoff:
        return False, f"This event has ended and is no longer available for booking."
    
    # Holiday Minis: count bookings instead of total tickets
    if "Holiday Minis" in event.title:
        if tickets > 10:
            return False, f"Holiday Minis accommodate up to 10 guests maximum per booking."
        
        # Count number of completed bookings (each booking = 1 slot)
        current_bookings_count = db.session.query(db.func.count(Booking.id)).join(Payment).filter(
            Booking.event_id == event.id,
            Payment.status == 'COMPLETED'
        ).scalar() or 0
        
        if current_bookings_count >= event.max_capacity:
            return False, f"Sorry, this Holiday Minis session has reached capacity."
        
        return True, None
    
    # Private events don't use capacity system but need 24hr notice and max 10 people
    if event.is_private:
        # Check guest count limit for private events
        if tickets > 10:
            return False, f"Private events accommodate up to 10 guests maximum. Please contact us for larger groups."
        
        # Check 24-hour advance booking requirement using Pacific time
        if event.start <= now + timedelta(hours=24):
            return False, f"Private events require at least 24 hours advance notice due to staffing."
        return True, None
    
    # For open farm days only: Limit to one family unit per booking
    if tickets > 7:
        return False, f"One family unit per booking, no large groups due to liability. If your immediate family is more than 7 please contact us for an exception."
    
    # Get current bookings for this event - same logic as admin query that works
    current_bookings = db.session.query(db.func.sum(Booking.tickets)).join(Payment).filter(
        Booking.event_id == event.id,
        Payment.status == 'COMPLETED'
    ).scalar() or 0
    
    # Simple check: if already at/over capacity, block new bookings
    if current_bookings >= event.max_capacity:
        return False, f"Sorry, this event has reached capacity, please check our other offerings."
    
    # Check if this booking would put us over capacity
    final_bookings = current_bookings + tickets
    if final_bookings > event.max_capacity:
        available_spots = event.max_capacity - current_bookings
        return False, f"Sorry, this event has reached capacity, please check our other offerings."
    
    return True, None


def get_booking_summary(event, tickets, total_price):
    """Format booking details for display"""
    readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
    readable_end = event.end.strftime("%I:%M %p")
    readable_time_slot = f'{readable_start} - {readable_end}'
    
    return {
        'time_slot': readable_time_slot,
        'event_title': event.title,
        'event_description': event.description,
        'tickets': tickets,
        'total_price': total_price
    }