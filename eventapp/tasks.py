
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from eventapp import db, mail
from eventapp.models import Booking



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
            <h1 style="color: #2e6c80;">Important Safety and Arrival Notice</h1>
            
            <p>Hello {name},</p>

            <p>Thank you for booking a visit to Howe Ranch. Whether you're joining us for A Open Farm Day or a private tour, please review the following safety guidelines carefully:</p>

            <h2 style="color: #2e6c80;">Arrival Guidelines - No Early Arrivals</h2>
            <p>
                Due to ongoing issues related to early arrivals, we are implementing stricter guidelines for all guest visits. 
                Entry is <strong>strictly prohibited before your scheduled time slot at {time_slot}.</strong>
            </p>
            <p>
                Please <strong>do not arrive early</strong> or stage on the private road leading to the farm, as this disrupts our neighbors and compromises the safety of our staff and animals.
            </p>

            <h3 style="color: #2e6c80;">Why It’s Important:</h3>
            <ul style="padding-left: 20px;">
                <li><strong>Safety:</strong> Animals are being moved, and staff members are preparing for your arrival. We cannot accommodate early guests on the property, and the road is not a waiting area.</li>
                <br>
                <li><strong>Respect for Neighbors:</strong> Our farm is located on a private road. Please refrain from idling, parking, or gathering before the start time to maintain good relations with our neighbors.</li>
                <br>
                <li><strong>Stay On Schedule:</strong> Whether you're here for a private tour or Open Farm Day, our experiences are thoughtfully scheduled and you will not miss a thing by arriving on time or even after the scheduled start time.</li>
            </ul>

<h2 style="color: #2e6c80;">Animal Interactions & Safety</h2>
            <p>
                For your safety and the safety of our animals, <strong>please do not enter any animal pens or approach any animals until staff has reviewed safety guidelines with you and is present.</strong>
            </p>
            <p>
                If you arrive and do not see a staff member immediately, <strong>please call or text Spencer Howe at (424) 219-4212</strong> and remain in the designated waiting area. We might be assisting other guests or preparing animals for your experience.
            </p>

          <h3 style="color: #2e6c80;">Arrival Confirmation:</h3>
            <p>
                To help us ensure a safe and smooth experience for all guests, please <strong>reply to this email to confirm that you have read and understood the safety notice above.</strong>
            </p>

            <h2 style="color: #2e6c80;">What to Bring:</h2>
            <ul style="padding-left: 20px;">
                <li><strong>Closed-Toed Shoes:</strong> Required for safety in animal areas.</li>
                <li><strong>Drinking Water:</strong> Stay hydrated, as we do not provide beverages on-site.</li>
                <li><strong>Sunscreen and Hats:</strong> Protect yourself from the sun while interacting with the animals.</li>
            </ul>

            <h2 style="color: #2e6c80;">Location and Contact Information:</h2>
            <p>
                <strong>22053 Highland St<br>
                Wildomar, CA 92595</strong>
            </p>
            <p>
                If you have any questions or need assistance, please call or text Spencer Howe at 
                <strong>(424) 219-4212</strong> or reply to this email.
            </p>

            <hr style="margin: 30px 0;">
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


def check_and_send_reminders():
    now = datetime.utcnow()
    start_time = now + timedelta(hours=24)
    end_time = start_time + timedelta(hours=24)

    # Query bookings within the 24-hour window that haven't been sent a reminder
    bookings = Booking.query.filter(
        Booking.time_slot >= start_time,
        Booking.time_slot < end_time,
        Booking.reminder_sent == False  # Only unsent reminders
    ).all()

    for booking in bookings:
        send_reminder_email(booking)

    print(f"Checked and processed reminders for bookings between {start_time} and {end_time}")








