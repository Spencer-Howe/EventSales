"""
Booking-related routes and logic
"""
from flask import Blueprint, request, render_template, session, current_app
from .models import Event
from .pricing import EventPricingService, BookingService

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/calculate_price', methods=['POST'])
def calculate_price():
    """Calculate price for event booking with capacity and pricing validation"""
    event_id = request.form['event_id']
    tickets_str = request.form.get('tickets')
    paypal_client_id = current_app.config['PAYPAL_CLIENT_ID']

    try:
        tickets = int(tickets_str)
    except (ValueError, TypeError):
        tickets = 0

    # Get event from db
    event = Event.query.filter_by(id=event_id).first()
    
    if not event:
        return render_template('some_template.html',
                             time_slot='Unknown Time Slot',
                             tickets=tickets,
                             total_price=0,
                             paypal_client_id=paypal_client_id,
                             event_title='Unknown Event',
                             event_description='No description available',
                             error_message='Event not found')

    # calc with service
    total_price, error_message = EventPricingService.calculate_event_price(event, tickets)
    
    # Get booking summary
    booking_summary = BookingService.get_booking_summary(event, tickets, total_price)
    
    # session
    if total_price is not None:
        session['event_id'] = event_id
        session['tickets'] = tickets

    # all data template
    return render_template('some_template.html',
                          time_slot=booking_summary['time_slot'],
                          tickets=booking_summary['tickets'],
                          total_price=booking_summary['total_price'],
                          paypal_client_id=paypal_client_id,
                          event_title=booking_summary['event_title'],
                          event_description=booking_summary['event_description'],
                          error_message=error_message)