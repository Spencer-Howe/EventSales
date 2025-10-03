import uuid
from flask import Blueprint, request, redirect, url_for, render_template, current_app, session
from flask_login import login_required
from flask_mail import Message
from .extensions import db, mail

crypto_bp = Blueprint('crypto', __name__)

@crypto_bp.route('/crypto_checkout')
def crypto_checkout():
    # Get parameters from session (set in checkout route)
    event_id = session.get('event_id')
    tickets = session.get('tickets')
    
    if not event_id or not tickets:
        return redirect(url_for('views.home'))
    
    try:
        tickets = int(tickets)
    except (ValueError, TypeError):
        tickets = 1
    
    # Get event details
    from .models import Event
    event = Event.query.get_or_404(event_id)
    
    # Calculate total price
    total_price = tickets * event.price_per_ticket
    
    # Format event details
    readable_start = event.start.strftime("%B %d, %Y, %I:%M %p")
    readable_time_slot = f'{event.title} - {readable_start}'
    
    return render_template('crypto_checkout.html',
                          event_id=event.id,
                          event_title=event.title,
                          event_description=event.description,
                          time_slot=readable_time_slot,
                          tickets=tickets,
                          total_price=total_price)

@crypto_bp.route('/submit_crypto_payment', methods=['POST'])
def submit_crypto_payment():
    from .models import Booking
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    crypto_currency = request.form.get('crypto_currency')
    transaction_hash = request.form.get('transaction_hash')
    event_id = request.form.get('event_id')
    tickets = int(request.form.get('tickets'))
    total_price = float(request.form.get('total_price'))
    
    # Get event details
    from .models import Event
    event = Event.query.get_or_404(event_id)
    
    # Create order ID
    order_id = f"CRYPTO_{uuid.uuid4().hex[:8].upper()}"
    
    # Create booking with pending status
    new_booking = Booking(
        time_slot=event.start,
        tickets=tickets,
        order_id=order_id,
        amount_paid=total_price,
        currency='USD',
        status='pending_crypto',
        name=name,
        email=email,
        phone=phone,
        reminder_sent=False,
        payment_method='crypto',
        crypto_currency=crypto_currency,
        crypto_address=get_crypto_address(crypto_currency),
        transaction_hash=transaction_hash
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    # Render pending confirmation page
    return render_template('crypto_pending.html',
                          order_id=order_id,
                          name=name,
                          email=email,
                          crypto_currency=crypto_currency,
                          transaction_hash=transaction_hash,
                          total_price=total_price)

@crypto_bp.route('/confirm_crypto_payment/<order_id>')
@login_required
def confirm_crypto_payment(order_id):
    from .models import Booking
    
    booking = Booking.query.filter_by(order_id=order_id).first()
    if not booking:
        return "Booking not found", 404
    
    # Update booking status to confirmed
    booking.status = 'confirmed'
    db.session.commit()
    
    # Send confirmation email
    try:
        subject = 'Payment Confirmed - Howe Ranch'
        html_content = generate_receipt_html(booking)
        
        msg = Message(
            subject=subject,
            recipients=[booking.email],
            html=html_content,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
    except Exception as e:
        print(f"Email sending failed: {e}")
    
    return redirect('/admin/cryptoadmin/')

def get_crypto_address(crypto_currency):
    """Get the appropriate crypto address for the currency"""
    addresses = {
        'BTC': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        'ETH': '0x742d35Cc6634C0532925a3b8D6b9DfA0DfA0DfA1',
        'USDC': '0x742d35Cc6634C0532925a3b8D6b9DfA0DfA0DfA1',
        'USDT': '0x742d35Cc6634C0532925a3b8D6b9DfA0DfA0DfA1'
    }
    return addresses.get(crypto_currency, '')

def generate_receipt_html(booking):
    """Generate receipt HTML for crypto payment confirmation"""
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2e6c80;">Payment Confirmed - Mini Moos Experience</h1>
            <p><strong>Name:</strong> {booking.name}</p>
            <p><strong>Email:</strong> {booking.email}</p>
            <p><strong>Phone:</strong> {booking.phone}</p>
            <p><strong>Order ID:</strong> {booking.order_id}</p>
            <p><strong>Amount:</strong> ${booking.amount_paid:.2f} {booking.currency}</p>
            <p><strong>Time Slot:</strong> {booking.time_slot.strftime('%B %d, %Y at %I:%M %p') if booking.time_slot else 'N/A'}</p>
            <p><strong>Tickets:</strong> {booking.tickets}</p>
            
            <hr style="margin: 30px 0;">
            <h2 style="color: #2e6c80;">Visit Information</h2>
            <p><strong>Location:</strong><br>
            22053 Highland St<br>
            Wildomar, CA 92595</p>
            
            <p>Please arrive at your scheduled time. Bring water, wear closed-toe shoes, and dress comfortably.</p>
            
            <p>We're excited to welcome you to Howe Ranch!</p>
            <p>Warmly,<br>Spencer Howe</p>
        </body>
    </html>
    """