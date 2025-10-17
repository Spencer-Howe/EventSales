#!/usr/bin/env python3
"""
send QRs to guest that booked with previous app for upcoming events
python resend_qr_codes.py --event_id 443
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from eventapp import create_app, db
from eventapp.models import Booking, Customer, Event
from flask_mail import Message
from eventapp.extensions import mail
from flask import url_for
import argparse

def resend_qr_codes_for_event(event_id):
    # Create app without scheduler to avoid issues
    from eventapp import create_app
    from eventapp.tasks import check_and_send_reminders, clear_old_bookings
    app = create_app(check_and_send_reminders=check_and_send_reminders, clear_old_bookings=clear_old_bookings)
    
    with app.app_context():
        # Get all bookings for this event
        bookings = db.session.query(Booking)\
            .join(Customer)\
            .filter(Booking.event_id == event_id)\
            .all()
        
        if not bookings:
            print(f"No bookings found for event {event_id}")
            return
        
        event = Event.query.get(event_id)
        print(f"Found {len(bookings)} bookings for '{event.title}'")
        
        sent_count = 0
        failed_count = 0
        
        for booking in bookings:
            try:
                # Create receipt URL
                receipt_url = url_for('views.show_receipt', order_id=booking.order_id, _external=True)
                
                # Prepare email details
                email_order_details = {
                    'order_id': booking.order_id,
                    'customer_name': booking.customer.name,
                    'customer_email': booking.customer.email,
                    'event_title': event.title,
                    'event_date': event.start.strftime('%B %d, %Y at %I:%M %p') if event.start else 'TBD',
                    'tickets': booking.tickets,
                    'receipt_url': receipt_url
                }
                
                # Create custom email content with check-in procedure update
                html_content = f"""
                <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
                    <h1 style="color: #2e6c80;">Important Check-In Update for Your Farm Visit</h1>
                    
                    <p>Hello {booking.customer.name},</p>
                    
                    <p>We hope you're excited for your upcoming visit to <strong>{event.title}</strong> on {email_order_details['event_date']}!</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0;">
                        <h3 style="color: #28a745; margin-top: 0;">📱 NEW CHECK-IN PROCEDURE</h3>
                        <p><strong>We've updated our check-in process!</strong> We now use a digital QR code scanning system for faster, more efficient entry to the ranch.</p>
                        <p>Please bring the QR code below on your phone or print it out - you'll need it for check-in verification at the gate.</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <h3>Your Digital Receipt & QR Code</h3>
                        <p>Order ID: <strong>{booking.order_id}</strong></p>
                        <p>Party Size: <strong>{booking.tickets} guests</strong></p>
                        
                        <a href="{receipt_url}" style="display: inline-block; background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0;">
                            📱 View Your QR Code Receipt
                        </a>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4 style="color: #856404; margin-top: 0;">📋 What to Bring:</h4>
                        <ul style="color: #856404;">
                            <li>Your QR code (on phone or printed)</li>
                            <li>Comfortable closed-toe shoes</li>
                            <li>Weather-appropriate clothing</li>
                            <li>Camera for photos with the Mini Moos!</li>
                        </ul>
                    </div>
                    
                    <p>When you arrive at Howe Ranch, simply show your QR code to our staff at the check-in station. They'll scan it to verify your booking and get you started on your farm adventure!</p>
                    
                    <p>We can't wait to see you and introduce you to our adorable Mini Moo babies! 🐄</p>
                    
                    <p>If you have any questions, please don't hesitate to reach out.</p>
                    
                    <p>See you soon!<br>
                    The Howe Ranch Team</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                    <p style="font-size: 12px; color: #6c757d;">
                        This email contains your digital receipt and QR code for entry to Howe Ranch. 
                        Please save this email or bookmark your QR code link for easy access on the day of your visit.
                    </p>
                </div>
                """
                subject = f"🐄 Updated Check-In Info & Your QR Code - {event.title}"
                
                # Send email using Flask-Mail
                msg = Message(
                    subject=subject,
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[booking.customer.email],
                    html=html_content
                )
                mail.send(msg)
                
                print(f"✓ Sent QR code to {booking.customer.email} (Order: {booking.order_id})")
                sent_count += 1
                
            except Exception as e:
                print(f"✗ Failed to send to {booking.customer.email}: {str(e)}")
                failed_count += 1
        
        print(f"\nSummary:")
        print(f"Successfully sent: {sent_count}")
        print(f"Failed: {failed_count}")
        print(f"Total processed: {len(bookings)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Resend QR codes for an event')
    parser.add_argument('--event_id', type=int, required=True, help='Event ID to resend QR codes for')
    args = parser.parse_args()
    
    resend_qr_codes_for_event(args.event_id)