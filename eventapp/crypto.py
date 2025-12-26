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
    readable_end = event.end.strftime("%I:%M %p")
    readable_time_slot = f'{readable_start} - {readable_end}'
    
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
    
    # Store actual ticket count  
    stored_tickets = tickets
    
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
    
    # Redirect to pending page instead of receipt (payment not verified yet)
    return redirect(f'/crypto_pending/{order_id}')

@crypto_bp.route('/crypto_pending/<order_id>')
def crypto_pending(order_id):
    """Show pending page for unconfirmed crypto payments"""
    from .models import Booking
    
    booking = Booking.query.filter_by(order_id=order_id).first()
    if not booking:
        return "Booking not found", 404
    
    # Get payment details
    payment = None
    for p in booking.payments:
        if p.payment_method == 'crypto':
            payment = p
            break
    
    return render_template('crypto_pending.html',
                          order_id=order_id,
                          name=booking.customer.name if booking.customer else "Anonymous",
                          email=booking.customer.email if booking.customer else "No email provided",
                          crypto_currency=payment.crypto_currency if payment else "Unknown",
                          transaction_hash=payment.transaction_hash if payment else "Unknown")

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
        subject = 'Registration Confirmation - Howe Ranch'
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
    
    # Format time slot with start and end times
    if booking.event and booking.event.start and booking.event.end:
        start_formatted = booking.event.start.strftime("%B %d, %Y, %I:%M %p")
        end_formatted = booking.event.end.strftime("%I:%M %p")
        time_slot = f"{start_formatted} - {end_formatted}"
    else:
        time_slot = "TBD"
    
    return f"""
    
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1>Registration Confirmation</h1>
            <p><strong>Name:</strong> {booking.customer.name if booking.customer else "Unknown"}</p>
            <p><strong>Email:</strong> {booking.customer.email if booking.customer else "Unknown"}</p>
            <p><strong>Visit:</strong> {booking.event.title if booking.event else "Unknown Visit"}</p>
            <p>Order ID: {booking.order_id}</p>
            <p>Registration Fee: {latest_payment.amount_paid if latest_payment else 0}</p>
            <p>Currency: {latest_payment.currency if latest_payment else "USD"}</p>
            <p>Status: {latest_payment.status if latest_payment else "Unknown"}</p>
            <p>Time: {time_slot}</p>
            <p>Number of Guests: {booking.tickets}</p>
            <div style="margin-bottom: 20px;">
                <a href="{waiver_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Please Complete Registration</a>
            </div>
            
            <!-- QR Code for Check-in -->
            <div style="text-align: center; margin: 20px 0; border: 2px dashed #007bff; padding: 20px; border-radius: 10px; background-color: #f8f9fa;">
                <h3 style="color: #007bff; margin-bottom: 15px;">📱 Quick Check-In</h3>
                <p><strong>Show this QR code when you arrive for instant check-in!</strong></p>
                
                <!-- Mobile-friendly access options -->
                <div style="margin: 15px 0;">
                    <a href="{receipt_url}" 
                       style="margin: 5px; padding: 10px 20px; background-color: #28a745; border: none; color: white; text-decoration: none; border-radius: 5px; display: inline-block;">
                        📥 View QR Code
                    </a>
                </div>
                
                <p style="margin-top: 10px; font-size: 0.9rem; color: #6c757d;">
                    Or visit: {receipt_url}
                </p>
            </div>
            
            <hr>
            
            <h2 style="margin-top: 30px;">Thank You & Important Visit Information</h2>
            <p>Thank you for supporting our farm and booking your visit to the Mini Moos experience at Howe Ranch! Our miniature Highland cows and their barn friends are excited to show you the magical place they call home:</p>
            <p><strong>22053 Highland St<br>Wildomar, CA 92595</strong></p>
            <p>To be compliant with our neighborhood's no impact policies and liability regulations, and ensure a safe and enjoyable experience for the animals and you, we must ask that you please confirm that you have reviewed the visit guidelines below, as posted on our website:</p>

            <h3 style="color: #d9534f; margin-top: 25px;">Arrival Guidelines - No Early Arrivals</h3>
            <ul style="padding-left: 20px;">
                <li><strong>EARLY ARRIVALS STRICTLY PROHIBITED:</strong> Guests must not arrive before the visit start time. Entry is strictly prohibited before your scheduled time slot due to farm liability management guidelines, which includes moving animals across the parking access area. Early arrivals disrupt operations, compromise safety while moving animals, and will not be accommodated. You will not miss anything by arriving after your scheduled time. We recommend Montage Brothers and Starbucks coffee houses down the street if you arrive in the area early.</li>
                <br>
                <li><strong>PRIVATE ROAD LAWS:</strong> Stopping or staging on the private farm road is strictly prohibited. Strict 15 MPH speed limit on the monitored, unpaved street leading to Howe Ranch as posted— speeding will result in loss of your visit.</li>
            </ul>

            <h3 style="color: #2e6c80; margin-top: 25px;">Animal Interactions & Safety</h3>
            <ul style="padding-left: 20px;">
                <li><strong>NO DOGS:</strong> For the safety of our animals and guests, our farm cannot accommodate dogs. Most of our animals are prey species, their reactions would make the encounter unsafe for all, and we have trained livestock guardians to protect from unknown canines on site.</li>
                <br>
                <li><strong>SAFETY:</strong> Sunscreen, hat, and closed-toed shoes. Important: Bring water for hydration.</li>
                <br>
                <li><strong>SUPERVISED ONLY:</strong> For your safety and the safety of our animals, please do not approach any animals until staff has reviewed safety guidelines with you and is present. Children must be supervised by your group at all time.</li>
            </ul>
            <p style="margin-top: 15px;">If you arrive and do not see a staff member immediately, please call or text <strong>(424) 219-4212</strong> and remain in the designated waiting area. We might be assisting other guests or preparing animals for your experience.</p>

            <h3 style="color: #2e6c80; margin-top: 25px;">Transferable Only — No Refunds or Reschedules</h3>
            <p>The moment your experience is booked, resources are reserved and your time slot is blocked from other visitors. Booked experiences are transferable to other guests in your network, but not refundable, and cannot be rescheduled. Because our team is fully dedicated to caring for the animals and hosting scheduled guests, requests for exceptions cannot be accommodated and will not receive a response. If you transfer your experience, we must receive the guest's name prior to arrival.</p>

            <p style="margin-top: 25px;">We're so excited to welcome you to the ranch and share the magic of our animals and their farm with you. Thank you for supporting our family farm by being a thoughtful steward of small farm experiences in our beautiful area.</p>
            <p style="margin-top: 15px;">When you arrive, turn left at the Parking Sign and show your QR code to the gatekeeper, who will direct you to the parking area. Have fun!</p>

            <p>Warmly,<br>Spencer Howe</p>
        </body>
    </html>


    """