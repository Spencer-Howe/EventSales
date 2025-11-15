import uuid
from flask import Blueprint, request, redirect, url_for, render_template, current_app, session
from flask_login import login_required
from flask_mail import Message
from .extensions import db, mail

crypto_bp = Blueprint('crypto', __name__)

@crypto_bp.route('/crypto_checkout')
def crypto_checkout():
    # Get parameters url
    event_id = request.args.get('event_id')
    tickets = request.args.get('tickets')
    
    if not event_id or not tickets:
        return redirect(url_for('views.home'))
    
    try:
        event_id = int(event_id)  # Convert event_id to integer
    except (ValueError, TypeError):
        return "Invalid event ID", 400
        
    try:
        tickets = int(tickets)
    except (ValueError, TypeError):
        tickets = 1
    
    # Get event details
    from .models import Event
    event = Event.query.get_or_404(event_id)
    
    # Calculate total price using unified pricing system
    from .pricing import get_total_price
    total_price = get_total_price(event, tickets)
    
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

@crypto_bp.route('/submit_crypto_payment', methods=['GET'])
def submit_crypto_payment():
    from .models import Booking, Customer, Payment
    
    # Get URL parameters
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    crypto_currency = request.args.get('crypto_currency')
    transaction_hash = request.args.get('transaction_hash')
    event_id = request.args.get('event_id')
    tickets = int(request.args.get('tickets'))
    total_price = float(request.args.get('total_price'))
    
    try:
        event_id = int(event_id)  # Convert event_id to integer
    except (ValueError, TypeError):
        return "Invalid event ID", 400
    
    # Get event details
    from .models import Event
    event = Event.query.get_or_404(event_id)
    
    # Create order ID
    order_id = f"CRYPTO_{uuid.uuid4().hex[:8].upper()}"
    
    # Find or create customer
    customer = Customer.query.filter_by(email=email).first() if email and email.strip() else None
    if not customer:
        customer = Customer(
            name=name or "Anonymous",
            email=email or "anonymous@crypto.booking",
            phone=phone
        )
        db.session.add(customer)
        db.session.flush()  # Get customer.id
    
    # Holiday Minis: force tickets to 1 regardless of guest count
    stored_tickets = 1 if "Holiday Minis" in event.title else tickets
    
    # Create booking
    new_booking = Booking(
        customer_id=customer.id,
        event_id=event.id,
        tickets=stored_tickets,
        order_id=order_id,
        reminder_sent=False
    )
    db.session.add(new_booking)
    db.session.flush()  # Get booking.id
    
    # Create payment record
    payment = Payment(
        booking_id=new_booking.id,
        amount_paid=total_price,
        currency='USD',
        status='pending_crypto',
        payment_method='crypto',
        crypto_currency=crypto_currency,
        crypto_address=get_crypto_address(crypto_currency),
        transaction_hash=transaction_hash
    )
    db.session.add(payment)
    db.session.commit()
    
    # Send notification email to admin for ALL crypto payments (need manual verification)
    try:
        if not email or email.strip() == "":
            subject = f'Anonymous Crypto Booking - {crypto_currency}'
            admin_email_body = f"""
Anonymous crypto booking received:

Order ID: {order_id}
Currency: {crypto_currency}
Amount: ${total_price}
Transaction Hash: {transaction_hash}
Event: {event.title}
Date: {event.start.strftime("%B %d, %Y, %I:%M %p")}
Guests: {tickets}

No contact info provided - customer will bring receipt page for entrance.
Review and confirm payment in crypto admin panel.
            """
        else:
            subject = f'Crypto Payment Pending Verification - {crypto_currency}'
            admin_email_body = f"""
Crypto payment received - requires verification:

Order ID: {order_id}
Customer: {name}
Email: {email}
Phone: {phone}
Currency: {crypto_currency}
Amount: ${total_price}
Transaction Hash: {transaction_hash}
Event: {event.title}
Date: {event.start.strftime("%B %d, %Y, %I:%M %p")}
Guests: {tickets}

Go to crypto admin panel to verify payment and send confirmation email to customer.
            """
        
        msg = Message(
            subject=subject,
            recipients=['howeranchservices@gmail.com'],
            body=admin_email_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
    except Exception as e:
        print(f"Admin notification email failed: {e}")
    
    # Redirect to receipt
    return redirect(f'/receipt/{order_id}')

@crypto_bp.route('/confirm_crypto_payment/<order_id>')
@login_required
def confirm_crypto_payment(order_id):
    from .models import Booking
    
    booking = Booking.query.filter_by(order_id=order_id).first()
    if not booking:
        return "Booking not found", 404
    
    # Update payment status to confirmed
    for payment in booking.payments:
        if payment.payment_method == 'crypto':
            payment.status = 'confirmed'
    
    # Mark private event as booked when crypto payment is confirmed
    if booking.event.is_private and "Holiday Minis" not in booking.event.title:
        booking.event.is_booked = True
    
    db.session.commit()
    
    # Send confirmation email
    try:
        subject = 'Payment Confirmed - Howe Ranch'
        html_content = generate_receipt_html(booking)
        
        recipient_email = booking.customer.email if booking.customer else None
        if recipient_email:
            msg = Message(
                subject=subject,
                recipients=[recipient_email, 'howeranchservices@gmail.com'],
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

def generate_qr_code_base64(order_id):
    """Generate QR code base64 for crypto emails"""
    from .views import generate_qr_code
    return generate_qr_code(order_id).split(',')[1]  # Remove data:image/png;base64, prefix

def generate_receipt_html(booking):
    """Generate receipt HTML for crypto payment confirmation"""
    # Create waiver and receipt URLs for the booking
    from flask import url_for
    waiver_url = url_for('views.sign_waiver', order_id=booking.order_id, _external=True)
    receipt_url = url_for('views.show_receipt', order_id=booking.order_id, _external=True)
    
    # Get latest payment details
    latest_payment = booking.payments[0] if booking.payments else None
    
    return f"""
    
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2e6c80;">Payment Receipt</h1>
            <p><strong>Name:</strong> {booking.customer.name if booking.customer else "Unknown"}</p>
            <p><strong>Email:</strong> {booking.customer.email if booking.customer else "Unknown"}</p>
            <p><strong>Phone Number:</strong> {booking.customer.phone if booking.customer else "Unknown"}</p>
            <p><strong>Order ID:</strong> {booking.order_id}</p>
            <p><strong>Total Amount:</strong> {latest_payment.amount_paid if latest_payment else 0}</p>
            <p><strong>Currency:</strong> {latest_payment.currency if latest_payment else "USD"}</p>
            <p><strong>Status:</strong> {latest_payment.status if latest_payment else "Unknown"}</p>
            <p><strong>Time Slot:</strong> {booking.event.start if booking.event else "Unknown"}</p>
            <p><strong>Number of Tickets:</strong> {booking.tickets}</p>
            <p>Please review and sign the waiver if you did not already finish the registration after checkout 
                <a href="{waiver_url}" style="color: #1a73e8;">here</a>.
            </p>
            
            <!-- Receipt & QR Code Link -->
            <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #007bff; border-radius: 10px; background-color: #f8f9fa;">
                <h3 style="color: #007bff; margin-bottom: 15px;">📱 Check-in QR Code</h3>
                <p style="margin-bottom: 15px;"><strong>Access your QR code for instant check-in at the ranch!</strong></p>
                <a href="{receipt_url}" style="display: inline-block; background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px;">
                    View Receipt & QR Code
                </a>
                <p style="margin-top: 10px; font-size: 0.9rem; color: #6c757d;">
                    Save this link or bookmark it for easy access on your phone
                </p>
            </div>
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
                    Please do <strong>not arrive earlier than your reserved time slot at {booking.event.start if booking.event else "Unknown"}</strong>. Early arrivals are not permitted, as we are actively preparing the animals and property for your visit.<br><br>
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