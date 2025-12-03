
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
        <p>Thank you for purchasing passes to the Mini Moos experience at Howe Ranch. Our miniature Highland cows and their barn friends are excited to show you the magical place they call home:</p>
        <p><strong>22053 Highland St<br>Wildomar, CA 92595</strong></p>
        <p>To be compliant with our neighborhood's no impact policies and liability regulations, and ensure a safe and enjoyable experience for the animals and for you, please confirm you have reviewed the visit guidelines below:</p>

        <h2 style="color: #2e6c80;">Arrival Guidelines – No Early Arrivals</h2>
        <ul style="padding-left:20px;">
          <li>Early arrivals are strictly prohibited. Guests must not arrive before the scheduled time slot due to farm liability management (including moving animals across parking areas).</li>
          <li>You will not miss anything by arriving after your scheduled time.</li>
          <li>If you arrive in the area early: Montague Brothers Coffee and Starbucks are nearby.</li>
          <li>Stopping or staging on the private farm road is not permitted. 15 MPH speed limit is enforced.</li>
        </ul>

        <h2 style="color: #2e6c80;">Animal Interactions &amp; Safety</h2>
        <ul style="padding-left:20px;">
          <li>No dogs allowed on the ranch.</li>
          <li>Sunscreen, hat, and closed-toed shoes recommended. Please bring water.</li>
          <li>Do not approach any animals until staff has reviewed safety with your group and is present. Children must remain supervised by your group at all times.</li>
        </ul>

        <p>If you arrive and do not see a staff member immediately, please call or text <strong>(424) 219-4212</strong> and remain in the designated waiting area. We may be assisting another group or preparing animals.</p>

        <h2 style="color: #2e6c80;">Transferable Only — No Refunds or Reschedules</h2>
        <p>Once booked, resources are reserved and the time slot is blocked from other visitors. Experiences may be transferred to other guests in your network, but are not refundable and cannot be rescheduled. If you transfer your pass, please provide the new guest's name prior to arrival.</p>

        <p>When you arrive, turn left at the Parking sign and show your QR pass to the gatekeeper, who will direct you to parking.</p>

        <h2 style="color: #2e6c80;">QR Code</h2>
        <div style="text-align: center; margin: 20px 0;">
          <img src="{qr_code_data}" alt="QR Code" style="border: 1px solid #ddd; padding: 5px; width: 150px; height: 150px;">
          <br>
          <p><strong>Order ID: {booking.order_id}</strong> — showing on your phone is fine</p>
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




