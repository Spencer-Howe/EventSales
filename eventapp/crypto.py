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
    
    # Crypto payments need admin approval first - no immediate receipt
    # Receipt will be sent when admin confirms payment, which includes waiver link
    
    # Render pending confirmation page instead of redirecting to waiver
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
        'BTC': 'bc1qkttfrwweek9ajmcf772kz2yxt5wqnzxfa0x8d7', #btc address
        'LTC': 'LPxKrKd2ShrijTrq2xJdBMnqxQ62mn4Pci', #actual adress
        'XMR': '48w9R7gh5zyeyUCERtxgxfbpzouoL5KNkY9VE25v7mV8eMGZxAuE994M2j9LXEC84JigNWT2bLC3HT5mD5Ebn4hNKFi9E7f',
    }
    return addresses.get(crypto_currency, '')

def generate_receipt_html(booking):
    """Generate receipt HTML for crypto payment confirmation"""
    # Create waiver URL for the booking
    from flask import url_for
    waiver_url = url_for('views.sign_waiver', order_id=booking.order_id, _external=True)
    
    return f"""
    
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2e6c80;">Payment Receipt</h1>
            <p><strong>Name:</strong> {booking.name}</p>
            <p><strong>Email:</strong> {booking.email}</p>
            <p><strong>Phone Number:</strong> {booking.phone}</p>
            <p><strong>Order ID:</strong> {booking.order_id}</p>
            <p><strong>Total Amount:</strong> {booking.amount_paid}</p>
            <p><strong>Currency:</strong> {booking.currency}</p>
            <p><strong>Status:</strong> {booking.status}</p>
            <p><strong>Time Slot:</strong> {booking.time_slot}</p>
            <p><strong>Number of Tickets:</strong> {booking.tickets}</p>
            <p>Please review and sign the waiver if you did not already finish the registration after checkout 
                <a href="{waiver_url}" style="color: #1a73e8;">here</a>.
            </p>
            <hr style="margin: 30px 0;">
            <h2 style="color: #2e6c80;">Thank You & Important Visit Information</h2>
            <p>
                Thank you for purchasing passes to the <strong>Mini Moos experience</strong> at Howe Ranch! You're officially on our guest list—just identify yourself at the welcome table when you arrive. 
                Our event is held at:
            </p>
            <p>
                <strong>22053 Highland St<br>
                Wildomar, CA 92595</strong>
            </p>
            <p>
                To help us ensure a smooth, safe, and enjoyable experience for all our guests and animals, please take a moment to review the visit guidelines below:
            </p>
            <ul style="padding-left: 20px;">
                <li>
                    <strong>Arrival Time:</strong><br>
                    Please do <strong>not arrive earlier than your reserved time slot at {booking.time_slot}</strong>. Early arrivals are not permitted, as we are actively preparing the animals and property for your visit.<br><br>
                    Please <strong>do not stage on the private road</strong>, as this creates a safety and liability concern.
                </li>
                <br>
                <li>
                    <strong>Best Time to Arrive:</strong><br>
                    Animal interactions are available throughout your reserved window. Most guests find the sweet spot is arriving about 15–30 minutes after the start time to enjoy the full experience.
                </li>
                <br>
                <li>
                    <strong>Parking:</strong><br>
                    Enter through the red gate <strong>after your start time</strong> and take the left at the welcome sign.
                </li>
                <br>
                <li>
    			<strong>What to Bring:</strong><br>
    			Be sure to bring drinking water, wear closed-toed shoes, and dress comfortably for walking around the farm.
		        </li>

            </ul>
            <p>
                We're so excited to welcome you to the ranch and share the magic of our animals with you. Thank you for helping us keep the experience safe and enjoyable for all.
            </p>
            <p>Warmly,<br>Spencer Howe</p>
        </body>
    </html>


    """