"""Data preserving migration - populate customer and payment tables

Revision ID: 939a008e70d6
Revises: 326197f37b67
Create Date: 2025-10-09 01:57:13.427546

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '939a008e70d6'
down_revision = '326197f37b67'
branch_labels = None
depends_on = None


def upgrade():
    # Import what we need
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    
    # Get database connection
    connection = op.get_bind()
    
    # Create customers from existing booking data (only if customer table is empty)
    customer_count = connection.execute(text("SELECT COUNT(*) FROM customer")).scalar()
    
    if customer_count == 0:
        print("Migrating customer data from booking table...")
        
        # Insert unique customers from booking table
        connection.execute(text("""
            INSERT INTO customer (name, email, phone, created_at)
            SELECT DISTINCT 
                COALESCE(name, 'Unknown') as name,
                COALESCE(email, 'unknown@email.com') as email, 
                phone,
                NOW() as created_at
            FROM booking 
            WHERE name IS NOT NULL OR email IS NOT NULL
            ON CONFLICT DO NOTHING
        """))
        
        print("Customer data migrated successfully!")
    
    # Update booking foreign keys if they're NULL
    booking_updates_needed = connection.execute(text("""
        SELECT COUNT(*) FROM booking WHERE customer_id IS NULL OR event_id IS NULL
    """)).scalar()
    
    if booking_updates_needed > 0:
        print(f"Updating {booking_updates_needed} booking records...")
        
        # Update customer_id in bookings based on email match
        connection.execute(text("""
            UPDATE booking 
            SET customer_id = c.id
            FROM customer c
            WHERE booking.email = c.email 
            AND booking.customer_id IS NULL
        """))
        
        # Update event_id in bookings based on time_slot match
        connection.execute(text("""
            UPDATE booking 
            SET event_id = e.id
            FROM event e
            WHERE booking.time_slot = e.start 
            AND booking.event_id IS NULL
        """))
        
        print("Booking foreign keys updated!")
    
    # Create payment records if payment table is empty
    payment_count = connection.execute(text("SELECT COUNT(*) FROM payment")).scalar()
    
    if payment_count == 0:
        print("Creating payment records from booking data...")
        
        # Insert payment records for each booking
        connection.execute(text("""
            INSERT INTO payment (
                booking_id, amount_paid, currency, status, 
                payment_method, payment_date, paypal_order_id,
                crypto_currency, crypto_address, transaction_hash
            )
            SELECT 
                b.id as booking_id,
                COALESCE(b.amount_paid, 0) as amount_paid,
                COALESCE(b.currency, 'USD') as currency,
                COALESCE(b.status, 'completed') as status,
                COALESCE(b.payment_method, 'paypal') as payment_method,
                COALESCE(b.booking_date, NOW()) as payment_date,
                CASE WHEN b.payment_method = 'paypal' THEN b.order_id ELSE NULL END as paypal_order_id,
                b.crypto_currency,
                b.crypto_address,
                b.transaction_hash
            FROM booking b
            WHERE b.id NOT IN (SELECT DISTINCT booking_id FROM payment WHERE booking_id IS NOT NULL)
        """))
        
        print("Payment records created successfully!")
    
    print("Data migration completed! All existing data has been preserved.")


def downgrade():
    # This downgrade removes the migrated data but preserves the original booking columns
    from sqlalchemy import text
    connection = op.get_bind()
    
    print("Downgrading: Clearing customer and payment data...")
    connection.execute(text("DELETE FROM payment"))
    connection.execute(text("DELETE FROM customer"))
    connection.execute(text("UPDATE booking SET customer_id = NULL, event_id = NULL"))
    print("Downgrade completed.")
