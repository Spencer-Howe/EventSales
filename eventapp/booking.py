"""
Booking routes - clean and simple
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, current_app
from .models import Event
from .pricing import get_total_price, check_capacity, get_booking_summary

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/calculate_price', methods=['POST'])
def calculate_price():
    """Calculate price for event booking"""
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
        return render_template('checkout.html',
                             time_slot='Unknown Time Slot',
                             tickets=tickets,
                             total_price=0,
                             paypal_client_id=paypal_client_id,
                             event_title='Unknown Event',
                             event_description='No description available',
                             error_message='Event not found')

    # Check capacity first
    can_book, capacity_error = check_capacity(event, tickets)
    if not can_book:
        return render_template('checkout.html',
                             time_slot='Event Full',
                             tickets=tickets,
                             total_price=0,
                             paypal_client_id=paypal_client_id,
                             event_title=event.title,
                             event_description=event.description,
                             error_message=capacity_error)

    # Calculate price
    total_price = get_total_price(event, tickets)
    
    # Get booking summary
    booking_summary = get_booking_summary(event, tickets, total_price)

    # Render template with all data
    return render_template('checkout.html',
                          time_slot=booking_summary['time_slot'],
                          tickets=booking_summary['tickets'],
                          total_price=booking_summary['total_price'],
                          paypal_client_id=paypal_client_id,
                          event_title=booking_summary['event_title'],
                          event_description=booking_summary['event_description'],
                          error_message=None)