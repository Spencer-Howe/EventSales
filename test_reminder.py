#!/usr/bin/env python3
"""
Quick test script for reminder email with map
"""
import sys
import os
sys.path.append('/home/ubuntu/Documents/EventSales/EventSales-task3')

from eventapp import create_app
from eventapp.models import Booking, Customer, Event
from eventapp.tasks import send_reminder_email

def test_reminder():
    app = create_app()
    
    with app.app_context():
        # Get the most recent booking
        booking = Booking.query.order_by(Booking.id.desc()).first()
        
        if booking:
            print(f"Testing reminder email for booking: {booking.order_id}")
            print(f"Customer: {booking.customer.name if booking.customer else 'Unknown'}")
            print(f"Event: {booking.event.title if booking.event else 'Unknown'}")
            print(f"Email: {booking.customer.email if booking.customer else 'Unknown'}")
            
            # Send test reminder
            send_reminder_email(booking)
            print("✅ Test reminder email sent!")
        else:
            print("❌ No bookings found in database")

if __name__ == "__main__":
    test_reminder()