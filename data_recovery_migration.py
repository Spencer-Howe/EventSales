"""
Data Recovery Migration Script
Run this to recover customer data from your live database backup
"""

from sqlalchemy import create_engine, text
import os

def recover_customer_data():
    """
    This script helps recover customer data by:
    1. Reading from your live database backup
    2. Creating Customer records from existing booking data
    3. Linking bookings to customers properly
    """
    
    # You'll need to provide your live database connection string
    LIVE_DB_URL = "postgresql://user:pass@host:port/live_db_name"
    
    # Connect to both databases
    live_engine = create_engine(LIVE_DB_URL)
    local_engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Extract unique customers from live booking table
    with live_engine.connect() as live_conn:
        # Get all unique customer data from live bookings
        customers_query = text("""
            SELECT DISTINCT name, email, phone 
            FROM booking 
            WHERE name IS NOT NULL AND email IS NOT NULL
        """)
        customers = live_conn.execute(customers_query).fetchall()
        
        # Get all booking data
        bookings_query = text("""
            SELECT * FROM booking
        """)
        bookings = live_conn.execute(bookings_query).fetchall()
    
    with local_engine.connect() as local_conn:
        # Insert customers
        for customer in customers:
            local_conn.execute(text("""
                INSERT INTO customer (name, email, phone, created_at)
                VALUES (:name, :email, :phone, NOW())
                ON CONFLICT (email) DO NOTHING
            """), {
                'name': customer.name,
                'email': customer.email, 
                'phone': customer.phone
            })
        
        # Update bookings with customer_id and event_id
        for booking in bookings:
            # Get customer_id
            customer_result = local_conn.execute(text("""
                SELECT id FROM customer WHERE email = :email
            """), {'email': booking.email}).fetchone()
            
            if customer_result:
                customer_id = customer_result.id
                
                # Find matching event by time_slot
                event_result = local_conn.execute(text("""
                    SELECT id FROM event WHERE start = :time_slot
                """), {'time_slot': booking.time_slot}).fetchone()
                
                event_id = event_result.id if event_result else None
                
                # Update booking
                local_conn.execute(text("""
                    UPDATE booking 
                    SET customer_id = :customer_id, event_id = :event_id
                    WHERE order_id = :order_id
                """), {
                    'customer_id': customer_id,
                    'event_id': event_id,
                    'order_id': booking.order_id
                })
                
                # Create payment record
                local_conn.execute(text("""
                    INSERT INTO payment (
                        booking_id, amount_paid, currency, status, 
                        payment_method, payment_date
                    )
                    SELECT id, :amount, :currency, :status, :method, :date
                    FROM booking WHERE order_id = :order_id
                """), {
                    'amount': booking.amount_paid,
                    'currency': booking.currency,
                    'status': booking.status,
                    'method': booking.payment_method,
                    'date': booking.booking_date or booking.time_slot,
                    'order_id': booking.order_id
                })
        
        local_conn.commit()

if __name__ == "__main__":
    recover_customer_data()
    print("Data recovery completed!")