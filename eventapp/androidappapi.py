"""
Android App API endpoints
All API routes for the mobile Android application
"""

from datetime import datetime
import pytz
from flask import Blueprint, request, jsonify
from .extensions import db

# Create the blueprint
android_api = Blueprint('android_api', __name__, url_prefix='/api')


@android_api.route('/booking/<order_id>', methods=['GET'])
def get_booking_info(order_id):
    """Safe endpoint to get booking details without checking in"""
    from eventapp.models import Booking
    
    booking = Booking.query.filter_by(order_id=order_id).first()
    
    if not booking:
        return jsonify({"success": False, "reason": "Booking not found"}), 404
    
    # Get latest payment for status and amount
    latest_payment = booking.payments[0] if booking.payments else None
    
    return jsonify({
        "success": True,
        "order_id": booking.order_id,
        "name": booking.customer.name if booking.customer else "Unknown",
        "email": booking.customer.email if booking.customer else "Unknown",
        "tickets": booking.tickets,
        "event": booking.event.start.strftime("%B %d, %Y at %I:%M %p") if booking.event and booking.event.start else "Unknown",
        "event_timestamp": booking.event.start.isoformat() if booking.event and booking.event.start else None,
        "status": latest_payment.status if latest_payment else "Unknown",
        "amount_paid": latest_payment.amount_paid if latest_payment else 0,
        "currency": latest_payment.currency if latest_payment else "USD",
        "checked_in": booking.checked_in,
        "checkin_time": booking.checkin_time.isoformat() if booking.checkin_time else None
    })


@android_api.route('/admin/login', methods=['POST'])
def admin_api_login():
    """API endpoint for staff/admin login for mobile app"""
    print(f"Login request received from {request.remote_addr}")
    print(f"Request headers: {dict(request.headers)}")
    
    data = request.get_json()
    print(f"Request data: {data}")
    
    if not data:
        print("No JSON data received")
        return jsonify({"success": False, "reason": "No data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    print(f"Attempting login for username: {username}")
    
    from eventapp.models import User
    user = User.query.filter_by(username=username).first()
    print(f"User found: {user is not None}")
    
    if user:
        print(f"User password: {user.password}, provided password: {password}")
        print(f"Password match: {user.password == password}")
    
    if user and user.password == password:
        # Generate admin token (simple approach - in production use JWT)
        admin_token = f"admin_{user.username}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            "success": True,
            "token": admin_token,
            "staff_id": user.username,
            "name": user.username  # You might want to add a name field to User model
        })
    else:
        return jsonify({
            "success": False,
            "reason": "Invalid credentials"
        }), 401


@android_api.route('/admin/checkin/<order_id>', methods=['POST'])
def admin_checkin_attendee(order_id):
    """Admin-only endpoint for checking in attendees"""
    from eventapp.models import Booking
    
    # Simple admin token check (you should implement proper auth)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "reason": "Admin authentication required"}), 401
    
    token = auth_header.replace('Bearer ', '')
    # For now, accept any token that looks like "admin_" followed by something
    # You should implement proper JWT tokens or session auth
    if not token.startswith('admin_'):
        return jsonify({"success": False, "reason": "Invalid admin token"}), 401
    
    booking = Booking.query.filter_by(order_id=order_id).first()
    
    if not booking:
        return jsonify({"success": False, "reason": "Booking not found"}), 404
    
    # Check if event is currently happening (only allow check-in during event)
    if booking.event:
        # Use local time (Pacific timezone) for comparison since events are stored in local time
        pacific_tz = pytz.timezone('America/Los_Angeles')
        now = datetime.now(pacific_tz).replace(tzinfo=None)  # Convert to naive datetime for comparison
        event = booking.event
        
        event_start = event.start
        event_end = event.end
        
        if now < event_start:
            return jsonify({
                "success": False, 
                "reason": "Check-in not yet available",
                "message": f"Check-in opens when event starts at {event_start.strftime('%I:%M %p')}"
            }), 400
        
        if now > event_end:
            return jsonify({
                "success": False, 
                "reason": "Check-in window closed",
                "message": f"Check-in closed when event ended at {event_end.strftime('%I:%M %p')}"
            }), 400
    
    if booking.checked_in:
        return jsonify({
            "success": False, 
            "reason": "Already checked in",
            "name": booking.customer.name if booking.customer else "Unknown",
            "checkin_time": booking.checkin_time.isoformat() if booking.checkin_time else None
        }), 400
    
    # Get request data for logging
    request_data = request.get_json() or {}
    staff_id = request_data.get('staff_id', 'unknown')
    location = request_data.get('location', 'entrance')
    
    # Mark as checked in with local time (Pacific/Los Angeles timezone)
    booking.checked_in = True
    pacific_tz = pytz.timezone('America/Los_Angeles')
    booking.checkin_time = datetime.now(pacific_tz).replace(tzinfo=None)  # Store as naive datetime in local time
    db.session.commit()
    
    return jsonify({
        "success": True,
        "name": booking.customer.name if booking.customer else "Unknown",
        "tickets": booking.tickets,
        "event": booking.event.start.strftime("%B %d, %Y at %I:%M %p") if booking.event and booking.event.start else "Unknown",
        "checkin_time": booking.checkin_time.isoformat(),
        "staff_id": staff_id,
        "location": location
    })


@android_api.route('/bookings', methods=['GET'])
def get_calendar_bookings():
    """Get bookings for admin calendar - returns flat structure for FullCalendar"""
    from eventapp.models import Booking
    from sqlalchemy import and_
    
    # Get date range parameters (optional for filtering)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    # Build query
    query = Booking.query
    
    # Apply date filters if provided
    if start_date and end_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            from eventapp.models import Event
            query = query.join(Event).filter(
                and_(Event.start >= start_dt, Event.start <= end_dt)
            )
        except ValueError:
            # If date parsing fails, continue without filtering
            pass
    
    bookings = query.all()
    
    # Return data in the format the calendar JavaScript expects
    calendar_events = []
    for b in bookings:
        if not b.event or not b.event.start:
            continue
            
        # Get payment info
        latest_payment = b.payments[0] if b.payments else None
        
        # Flatten the data structure for the calendar
        event_data = {
            'id': b.id,
            'title': b.event.title if b.event else 'Booking',
            'start': b.event.start.isoformat() if b.event and b.event.start else None,
            'end': b.event.end.isoformat() if b.event and b.event.end else None,
            'order_id': b.order_id,
            'tickets': b.tickets,
            # Flatten customer data to top level for backward compatibility
            'name': b.customer.name if b.customer else None,
            'email': b.customer.email if b.customer else None,
            'phone': b.customer.phone if b.customer else None,
            # Flatten payment data to top level for backward compatibility
            'amount_paid': latest_payment.amount_paid if latest_payment else 0,
            'currency': latest_payment.currency if latest_payment else 'USD',
            'status': latest_payment.status if latest_payment else 'unknown'
        }
        
        calendar_events.append(event_data)
    
    return jsonify(calendar_events)


@android_api.route('/bookings/detailed', methods=['GET'])
def get_all_bookings():
    """Get all bookings for admin interface - detailed nested structure"""
    from eventapp.models import Booking
    
    # Simple admin check - in production, use proper authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer admin_'):
        return jsonify({"success": False, "reason": "Admin authentication required"}), 401
    
    bookings = Booking.query.all()
    return jsonify({
        "success": True,
        "bookings": [{
            'id': b.id,
            'order_id': b.order_id,
            'tickets': b.tickets,
            'booking_date': b.booking_date.isoformat() if b.booking_date else None,
            'checked_in': b.checked_in,
            'checkin_time': b.checkin_time.isoformat() if b.checkin_time else None,
            'customer': {
                'name': b.customer.name if b.customer else None,
                'email': b.customer.email if b.customer else None,
                'phone': b.customer.phone if b.customer else None
            },
            'event': {
                'title': b.event.title if b.event else None,
                'start': b.event.start.isoformat() if b.event and b.event.start else None,
                'end': b.event.end.isoformat() if b.event and b.event.end else None
            },
            'payments': [{
                'amount_paid': p.amount_paid,
                'currency': p.currency,
                'status': p.status,
                'payment_method': p.payment_method,
                'payment_date': p.payment_date.isoformat() if p.payment_date else None
            } for p in b.payments]
        } for b in bookings]
    })


@android_api.route('/admin/events/checkin-stats', methods=['GET'])
def get_events_checkin_stats():
    """Get events with check-in statistics for admin"""
    from eventapp.models import Event, Booking
    from sqlalchemy import func
    
    # Simple admin check
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer admin_'):
        return jsonify({"success": False, "reason": "Admin authentication required"}), 401
    
    # Get events that have bookings
    events_with_stats = db.session.query(
        Event.id,
        Event.title,
        Event.start,
        Event.end,
        func.count(Booking.id).label('total_bookings'),
        func.sum(func.case([(Booking.checked_in == True, 1)], else_=0)).label('checked_in_count'),
        func.sum(Booking.tickets).label('total_tickets')
    ).join(Booking).group_by(Event.id).all()
    
    events_data = []
    for event_stat in events_with_stats:
        checked_in = event_stat.checked_in_count or 0
        remaining = event_stat.total_bookings - checked_in
        
        events_data.append({
            'event_id': event_stat.id,
            'title': event_stat.title,
            'start': event_stat.start.isoformat() if event_stat.start else None,
            'end': event_stat.end.isoformat() if event_stat.end else None,
            'total_bookings': event_stat.total_bookings,
            'total_tickets': event_stat.total_tickets or 0,
            'checked_in_count': checked_in,
            'remaining_count': remaining,
            'completion_percentage': round((checked_in / event_stat.total_bookings) * 100, 1) if event_stat.total_bookings > 0 else 0
        })
    
    return jsonify({
        "success": True,
        "events": events_data
    })


@android_api.route('/admin/events/<int:event_id>/bookings', methods=['GET'])
def get_event_bookings(event_id):
    """Get all bookings for a specific event with check-in status"""
    from eventapp.models import Event, Booking
    
    # Simple admin check
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer admin_'):
        return jsonify({"success": False, "reason": "Admin authentication required"}), 401
    
    event = Event.query.get_or_404(event_id)
    bookings = Booking.query.filter_by(event_id=event_id).all()
    
    bookings_data = []
    for booking in bookings:
        latest_payment = booking.payments[0] if booking.payments else None
        
        bookings_data.append({
            'booking_id': booking.id,
            'order_id': booking.order_id,
            'customer_name': booking.customer.name if booking.customer else "Unknown",
            'customer_email': booking.customer.email if booking.customer else "Unknown",
            'customer_phone': booking.customer.phone if booking.customer else None,
            'tickets': booking.tickets,
            'checked_in': booking.checked_in,
            'checkin_time': booking.checkin_time.isoformat() if booking.checkin_time else None,
            'booking_date': booking.booking_date.isoformat() if booking.booking_date else None,
            'amount_paid': latest_payment.amount_paid if latest_payment else 0,
            'currency': latest_payment.currency if latest_payment else 'USD',
            'status': latest_payment.status if latest_payment else 'unknown'
        })
    
    return jsonify({
        "success": True,
        "event": {
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat() if event.start else None,
            "end": event.end.isoformat() if event.end else None
        },
        "bookings": bookings_data,
        "summary": {
            "total_bookings": len(bookings),
            "checked_in": sum(1 for b in bookings if b.checked_in),
            "remaining": sum(1 for b in bookings if not b.checked_in),
            "total_tickets": sum(b.tickets for b in bookings)
        }
    })