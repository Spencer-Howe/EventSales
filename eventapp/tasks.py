
from datetime import datetime, timedelta
from flask import current_app, Blueprint
from flask_mail import Message
from eventapp import db, mail
from eventapp.models import Booking, Event

tasks = Blueprint('tasks', __name__)

def send_reminder_email(booking):
    subject = "Booking Reminder - Upcoming Event at Howe Ranch"
    sender = current_app.config['MAIL_USERNAME']
    recipient = booking.email
    time_slot = booking.time_slot.strftime('%Y-%m-%d %H:%M:%S')
    name = booking.name

    # Email content
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h1 style="color: #2e6c80;">Preparing for Your Visit &amp; Farm Policies</h1>

        <p>Hello {name},</p>

        <p>Thank you for booking a visit to Howe Ranch — we look forward to hosting you! Please review the following safety guidelines and farm policies carefully, and confirm that you have read and shared them with your group. These experiences are only possible with the full support and cooperation of our guests.</p>

        <h2 style="color: #2e6c80;">Arrival Guidelines - No Early Arrivals</h2>
        <ul style="padding-left:20px;">
          <li><strong>EARLY ARRIVALS STRICTLY PROHIBITED:</strong> Guests must not arrive before the event start time. Entry is strictly prohibited before your scheduled time slot at {time_slot}. Early arrivals disrupt operations, compromise safety while moving animals, and will not be accommodated. Please arrive on time or after start time. You will not miss anything by arriving after your scheduled time.</li>
          <br>
          <li><strong>PRIVATE ROAD LAWS:</strong> Stopping or staging on the private farm road is prohibited. Strict 15 MPH speed limit on the monitored, unpaved street leading to Howe Ranch — speeding will result in loss of your pass(es).</li>
          <br>
          <li><strong>ARRIVAL:</strong> Turn left at the WELCOME sign, pass through the gate, and follow signage.</li>
        </ul>

        <h2 style="color: #2e6c80;">Animal Interactions &amp; Safety</h2>
        <ul style="padding-left:20px;">
          <li><strong>NO DOGS:</strong> For the safety of our animals and guests, our farm cannot accommodate dogs. Most of our animals are prey species, their reactions would make the encounter unsafe for all, and we have trained livestock guardians to protect from unknown canines on site.</li>
          <br>
          <li><strong>SAFETY:</strong> Wear sunscreen, a hat, and closed-toed shoes. Important: Bring water for hydration.</li>
          <br>
          <li><strong>SUPERVISED ONLY:</strong> For your safety and the safety of our animals, please do not approach any animals until staff has reviewed safety guidelines with you and is present.</li>
        </ul>
        <p>If you arrive and do not see a staff member immediately, please call or text Spencer Howe at <strong>(424) 219-4212</strong> and remain in the designated waiting area. We might be assisting other guests or preparing animals for your experience.</p>

        <h2 style="color: #2e6c80;">Transferable Only — No Refunds or Reschedules</h2>
        <p>
          Experiences (open farm day passes/private experiences) are transferable, but not refundable, and cannot be rescheduled. As our focus is on animal care and our resources are perpetually at capacity, we are unable to accommodate changes — please do not call to request exceptions. If you transfer your experience, we must receive the guest’s name prior to arrival.
        </p>

        <h2 style="color: #2e6c80;">Location and Contact Information:</h2>
        <p>
          <strong>22053 Highland St<br>
          Wildomar, CA 92595</strong>
        </p>
        <p>If you have any questions or need assistance, please call or text <strong>(424) 219-4212</strong> or reply to this email.</p>

        <hr style="margin:30px 0;">
        <p>For additional details, please review our <a href="https://www.thehoweranch.com/_files/ugd/fca21d_8ac1fc676ea14f35bd0af74d441bbb4f.pdf" target="_blank">FAQ document here</a>.</p>

        <p>We look forward to welcoming you to Howe Ranch and sharing the magic of our animals with you.</p>
        <p>Warm regards,<br>Spencer Howe</p>
      </body>
    </html>
    """

    # Create email message
    msg = Message(subject, sender=sender, recipients=[recipient], html=html_content)

    # Send email
    try:
        mail.send(msg)
        print(f"Reminder email sent to {recipient}")
        # Update the booking to indicate the reminder was sent
        booking.reminder_sent = True
        db.session.commit()
    except Exception as e:
        print(f"Failed to send reminder email to {recipient}: {str(e)}")


def send_personal_notification(booking):
    subject = "Private Tour Booking Notification"
    sender = current_app.config['MAIL_USERNAME']
    recipient = ["spencerahowe99@gmail.com", "bixihowe@gmail.com"]

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Private Tour Booking Alert</h2>
            <p>A booking has been made that appears to be a private tour:</p>
            <ul>
                <li><strong>Name:</strong> {booking.name}</li>
                <li><strong>Email:</strong> {booking.email}</li>
                <li><strong>Time Slot:</strong> {booking.time_slot.strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>Amount Paid:</strong> ${booking.amount_paid}</li>
            </ul>
            <p>This is for your records only.</p>
        </body>
    </html>
    """

    msg = Message(subject, sender=sender, recipients=[recipient], html=html_content)

    try:
        mail.send(msg)
        print(f"Personal notification sent for private tour booking by {booking.name}")
    except Exception as e:
        print(f"Failed to send personal notification: {str(e)}")

def check_and_send_reminders(app):
    with app.app_context():
        now = datetime.utcnow()
        end_time = now + timedelta(hours=24)

        # Query bookings within the 24-hour window that haven't been sent a reminder
        bookings = Booking.query.filter(
            Booking.time_slot >= now,
            Booking.time_slot < end_time,
            Booking.reminder_sent == False  # Only unsent reminders
        ).all()

        for booking in bookings:
            send_reminder_email(booking)

            # If this is a private tour (amount_paid == 250), send personal notification
            if booking.amount_paid == 250:
                send_personal_notification(booking)

        print(f"Checked and processed reminders for bookings between {now} and {end_time}")




def clear_old_bookings(app):
    with app.app_context():
        now = datetime.utcnow()
        end_time = now - timedelta(hours=24)

        old_events = Event.query.filter(
            Event.end < end_time
        ).all()

        for event in old_events:
            db.session.delete(event)
        db.session.commit()




