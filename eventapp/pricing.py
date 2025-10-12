"""
Simple pricing logic - easy to extend
"""
from .extensions import db


def get_total_price(event, tickets):
    """Calculate total price for any event"""
    # Private events: flat rate regardless of ticket count
    if 'private boo' in event.title.lower() and 'moo' in event.title.lower():
        return 350
    if 'private experience' in event.title.lower():
        return 250
    
    # Regular events: price per ticket
    return tickets * event.price_per_ticket


def check_capacity(event, tickets):
    """Check if booking fits capacity"""
    from .models import Booking, Payment
    
    # Private events don't use capacity system
    if 'private' in event.title.lower():
        return True, None
    
    # Get current bookings for this event using new schema
    current_bookings = db.session.query(db.func.sum(Booking.tickets)).join(Payment).filter(
        Booking.event_id == event.id,
        Payment.status.in_(['COMPLETED', 'pending_crypto'])
    ).scalar() or 0
    
    # Open farm days: allow 10% overage buffer for flexibility
    overage_allowed = max(5, int(event.max_capacity * 0.1))
    max_total_capacity = event.max_capacity + overage_allowed
    available_spots = event.max_capacity - current_bookings
    
    # Check if sold out (no spots at base capacity)
    if available_spots <= 0:
        return False, f"Sorry, this event is sold out. Maximum capacity is {event.max_capacity}."
    
    # Check if this booking would exceed safe overage limit
    final_bookings = current_bookings + tickets
    if final_bookings > max_total_capacity:
        return False, f"Sorry, your group of {tickets} would exceed our safe capacity limit. We have {available_spots} spots remaining (capacity: {event.max_capacity})."
    
    return True, None


def get_booking_summary(event, tickets, total_price):
    """Format booking details for display"""
    readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
    readable_time_slot = f'{event.title} - {readable_start}'
    
    return {
        'time_slot': readable_time_slot,
        'event_title': event.title,
        'event_description': event.description,
        'tickets': tickets,
        'total_price': total_price
    }