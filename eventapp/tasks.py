
from datetime import datetime, timedelta
from flask import current_app, Blueprint, url_for
from flask_mail import Message
from eventapp import db, mail
from eventapp.models import Booking, Event
from eventapp.views import generate_qr_code

tasks = Blueprint('tasks', __name__)

def send_reminder_email(booking):
    subject = "Visit Reminder - Upcoming Farm Experience at Howe Ranch"
    sender = current_app.config['MAIL_USERNAME']
    recipient = booking.customer.email if booking.customer else "unknown@email.com"
    time_slot = booking.event.start.strftime('%Y-%m-%d %H:%M:%S') if booking.event else "Unknown"
    name = booking.customer.name if booking.customer else "Unknown"

    # Generate receipt URL instead of QR code
    receipt_url = f"https://thehoweranchpayment.com/receipt/{booking.order_id}"

    # Email content
    html_content = f"""
 <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <p>Hi {name},</p>

        <p>This is a friendly reminder that your visit to Howe Ranch is tomorrow at {time_slot}. We are looking forward to hosting you.</p>

<h2 style="color: #2e6c80;">Preparing for Your Visit &amp; Farm Policies</h2>
<p>
  Thank you for registering for a visit to Howe Ranch — we look forward to hosting you!
  Please review the following safety guidelines and farm policies carefully, and
  confirm that you have read and shared them with your group. These experiences
  are only possible with the full support and cooperation of our guests.
</p>

<h2 style="color: #2e6c80;">Arrival Guidelines – No Early Arrivals</h2>
<ul style="padding-left:20px;">
  <li>
    <strong>PRIVATE ROAD LAWS:</strong>
    Stopping or staging on the private farm road is prohibited. Strict <span style="color:#b30000; font-weight:bold;">15 MPH</span>
    speed limit on the monitored, unpaved street leading to Howe Ranch —
    speeding will result in <span style="color:#b30000; font-weight:bold;">loss of your visit</span>.
  </li>
  <li>
    <strong>EARLY ARRIVALS STRICTLY PROHIBITED:</strong>
    Guests must not arrive before the visit start time. Entry is strictly
    prohibited before your scheduled time slot. Early arrivals disrupt
    operations, compromise safety while moving animals, and will not be
    accommodated.
  </li>
  <li>
    Please arrive on time or after your start time. You will not miss anything
    by arriving after your scheduled time.
  </li>

  <li>
    <strong>ARRIVAL:</strong>
    Turn left at the WELCOME sign, pass through the gate, and follow signage.
  </li>
</ul>

<h2 style="color: #2e6c80;">Animal Interactions &amp; Safety</h2>
<ul style="padding-left:20px;">
  <li>
    <strong>NO DOGS:</strong>
    For the safety of our animals and guests, our farm cannot accommodate dogs.
    Most of our animals are prey species, their reactions would make the
    encounter unsafe for all, and we have trained livestock guardians to protect
    from unknown canines on site.
  </li>
  <li>
    <strong>SAFETY:</strong>
    Wear sunscreen, a hat, and closed-toed shoes. Important: Bring water for
    hydration.
  </li>
  <li>
    <strong>SUPERVISED ONLY:</strong>
    For your safety and the safety of our animals, please do not approach any
    animals until staff has reviewed safety guidelines with you and is present.
    Children must remain supervised by your group at all times.
  </li>
</ul>

<p>
  If you arrive and do not see a staff member immediately, please call or text
  Spencer Howe at <strong>(424) 219-4212</strong> and remain in the designated
  waiting area. We might be assisting other guests or preparing animals for your
  experience.
</p>

<h2 style="color: #2e6c80;">Transferable Only — No Refunds or Reschedules</h2>
<p>
  Experiences (open farm day passes/private experiences) are transferable, but
  not refundable, and cannot be rescheduled. As our focus is on animal care and
  our resources are perpetually at capacity, we are unable to accommodate
  changes — please do not call to request exceptions. If you transfer your
  experience, we must receive the guest’s name prior to arrival.
</p>

<h2 style="color: #2e6c80;">Location and Contact Information</h2>
<p>
  22053 Highland St<br>
  Wildomar, CA 92595
</p>

<!-- Route Map -->
<div style="text-align: center; margin: 20px 0; padding: 15px; border: 2px solid #2e6c80; border-radius: 8px; background-color: #f8f9fa;">
  <h3 style="color: #2e6c80; margin-bottom: 15px;">📍 Route to Ranch</h3>
  <img src="https://thehoweranchpayment.com/static/pic/arrivalnotice.jpg" 
       alt="Route map to Howe Ranch" 
       style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px;">
</div>

<p>
  If you have any questions or need assistance, please call or text
  <strong>(424) 219-4212</strong>.
</p>


        <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #007bff; border-radius: 10px; background-color: #f8f9fa;">
          <h3 style="color: #007bff; margin-bottom: 15px;">📱 Get Your QR Code</h3>
          <p style="margin-bottom: 15px;"><strong>Click here to access your QR code for check-in:</strong></p>
          <a href="{receipt_url}" style="display: inline-block; background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px;">
            View Receipt & QR Code
          </a>
          <p style="margin-top: 10px;"><strong>Order ID: {booking.order_id}</strong></p>
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




