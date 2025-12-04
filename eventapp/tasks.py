
from datetime import datetime, timedelta
from flask import current_app, Blueprint
from flask_mail import Message
from eventapp import db, mail
from eventapp.models import Booking, Event
from eventapp.views import generate_qr_code

tasks = Blueprint('tasks', __name__)

def send_reminder_email(booking):
    subject = "Booking Reminder - Upcoming Event at Howe Ranch"
    sender = current_app.config['MAIL_USERNAME']
    recipient = booking.customer.email if booking.customer else "unknown@email.com"
    time_slot = booking.event.start.strftime('%Y-%m-%d %H:%M:%S') if booking.event else "Unknown"
    name = booking.customer.name if booking.customer else "Unknown"
    
    # Generate proper QR code using your system
    qr_code_data = generate_qr_code(booking.order_id)

    # Email content
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>Hi {name},</p>

        <p>This is a friendly reminder that your visit to Howe Ranch is tomorrow at {time_slot}. We are looking forward to hosting you.</p>

        <h2 style="color: #2e6c80;">Thank You &amp; Important Visit Information</h2>
        <p>Thank you for purchasing passes to the Mini Moos experience at Howe Ranch! Our miniature Highland cows and their barn friends are excited to show you the magical place they call home:</p>
        <p><strong>22053 Highland St<br>Wildomar, CA 92595</strong></p>
        <p>To be compliant with our neighborhood's no impact policies and liability regulations, and ensure a safe and enjoyable experience for the animals and you, we must ask that you please confirm that you have reviewed the visit guidelines below, as posted on our website:</p>

        <h3 style="color: #d9534f; margin-top: 25px;">Arrival Guidelines - No Early Arrivals</h3>
        <ul style="padding-left:20px;">
          <li><strong>EARLY ARRIVALS STRICTLY PROHIBITED:</strong> Guests must not arrive before the event start time. Entry is strictly prohibited before your scheduled time slot due to farm liability management guidelines, which includes moving animals across the parking access area. Early arrivals disrupt operations, compromise safety while moving animals, and will not be accommodated. You will not miss anything by arriving after your scheduled time. We recommend Montage Brothers and Starbucks coffee houses down the street if you arrive in the area early.</li>
          <br>
          <li><strong>PRIVATE ROAD LAWS:</strong> Stopping or staging on the private farm road is strictly prohibited. Strict 15 MPH speed limit on the monitored, unpaved street leading to Howe Ranch as posted— speeding will result in loss of your pass(es).</li>
        </ul>

        <h3 style="color: #2e6c80; margin-top: 25px;">Animal Interactions &amp; Safety</h3>
        <ul style="padding-left:20px;">
          <li><strong>NO DOGS:</strong> For the safety of our animals and guests, our farm cannot accommodate dogs. Most of our animals are prey species, their reactions would make the encounter unsafe for all, and we have trained livestock guardians to protect from unknown canines on site.</li>
          <br>
          <li><strong>SAFETY:</strong> Sunscreen, hat, and closed-toed shoes. Important: Bring water for hydration.</li>
          <br>
          <li><strong>SUPERVISED ONLY:</strong> For your safety and the safety of our animals, please do not approach any animals until staff has reviewed safety guidelines with you and is present. Children must be supervised by your group at all time.</li>
        </ul>

        <p style="margin-top: 15px;">If you arrive and do not see a staff member immediately, please call or text <strong>(424) 219-4212</strong> and remain in the designated waiting area. We might be assisting other guests or preparing animals for your experience.</p>

        <h3 style="color: #2e6c80; margin-top: 25px;">Transferable Only — No Refunds or Reschedules</h3>
        <p>The moment your experience is booked, resources are reserved and your time slot is blocked from other visitors. Booked experiences are transferable to other guests in your network, but not refundable, and cannot be rescheduled. Because our team is fully dedicated to caring for the animals and hosting scheduled guests, requests for exceptions cannot be accommodated and will not receive a response. If you transfer your experience, we must receive the guest's name prior to arrival.</p>

        <p style="margin-top: 25px;">We're so excited to welcome you to the ranch and share the magic of our animals and their farm with you. Thank you for helping us keep our doors open by being a thoughtful steward of small farm experiences in our beautiful area.</p>
        <p style="margin-top: 15px;">When you arrive, turn left at the Parking Sign and show your QR Pass to the gatekeeper, who will direct you to the parking area. Have fun!</p>

        <!-- Receipt & QR Code Link -->
        <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #007bff; border-radius: 10px; background-color: #f8f9fa;">
          <h3 style="color: #007bff; margin-bottom: 15px;">📱 Check-in QR Code</h3>
          <p style="margin-bottom: 15px;"><strong>Access your QR code for instant check-in at the ranch!</strong></p>
          <a href="https://thehoweranchpayment.com/receipt/{booking.order_id}" style="display: inline-block; background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px;">
            View Receipt & QR Code
          </a>
          <p style="margin-top: 10px; font-size: 0.9rem; color: #6c757d;">
            Save this link or bookmark it for easy access on your phone
          </p>
          <p><strong>Order ID: {booking.order_id}</strong></p>
        </div>

        <p>We look forward to welcoming you and sharing the magic of our animals and their farm with you.</p>

        <p>Warmly,<br>Spencer Howe</p>
      </body>
    </html>
    """

    # Create email message
    msg = Message(subject, sender=sender, recipients=[recipient], html=html_content)

    # Send email
    try:
        mail.send(msg)
        print(f"Reminder email sent to {recipient}")
    except Exception as e:
        print(f"Failed to send reminder email to {recipient}: {str(e)}")


def send_personal_notification(booking):
    subject = "Private Tour Booking Notification"
    sender = current_app.config['MAIL_USERNAME']
    recipient = ["spencerahowe99@gmail.com", "bixihowe@gmail.com"]

    # Get latest payment for amount
    latest_payment = booking.payments[0] if booking.payments else None
    amount_paid = latest_payment.amount_paid if latest_payment else 0
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Private Tour Booking Alert</h2>
            <p>A booking has been made that appears to be a private tour:</p>
            <ul>
                <li><strong>Name:</strong> {booking.customer.name if booking.customer else "Unknown"}</li>
                <li><strong>Email:</strong> {booking.customer.email if booking.customer else "Unknown"}</li>
                <li><strong>Time Slot:</strong> {booking.event.start.strftime('%Y-%m-%d %H:%M:%S') if booking.event else "Unknown"}</li>
                <li><strong>Amount Paid:</strong> ${amount_paid}</li>
            </ul>
            <p>This is for your records only.</p>
        </body>
    </html>
    """

    msg = Message(subject, sender=sender, recipients=[recipient], html=html_content)

    try:
        mail.send(msg)
        print(f"Personal notification sent for private tour booking by {booking.customer.name if booking.customer else 'Unknown'}")
    except Exception as e:
        print(f"Failed to send personal notification: {str(e)}")

def check_and_send_reminders(app):
    with app.app_context():
        now = datetime.utcnow()
        end_time = now + timedelta(hours=24)

        # Query bookings within the 24-hour window that haven't been sent a reminder
        # Join with Event to check event start times
        from eventapp.models import Event
        bookings = Booking.query.join(Event).filter(
            Event.start >= now,
            Event.start < end_time,
            Booking.reminder_sent == False  # Only unsent reminders
        ).all()

        processed_count = 0
        for booking in bookings:
            # Atomic update: only process if we can successfully mark as sent
            rows_updated = db.session.query(Booking).filter(
                Booking.id == booking.id,
                Booking.reminder_sent == False
            ).update({'reminder_sent': True})
            
            if rows_updated > 0:
                # We successfully claimed this booking, commit the flag update
                db.session.commit()
                
                # Now send the email
                send_reminder_email(booking)
                processed_count += 1

                # If this is a private tour (amount_paid == 250), send personal notification
                latest_payment = booking.payments[0] if booking.payments else None
                if latest_payment and latest_payment.amount_paid == 250:
                    send_personal_notification(booking)
            else:
                # Another process already claimed this booking
                print(f"Booking {booking.id} already processed by another instance")

        print(f"Checked and processed {processed_count} reminders for bookings between {now} and {end_time}")




# def clear_old_bookings(app):
#     # REMOVED - was deleting old events and breaking email recovery
#     # Now we filter frontend instead to hide old events from booking
#     pass




