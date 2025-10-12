-- Production Database Migration Script
-- Run this on your production database to migrate to new schema

BEGIN;

-- Create new tables
CREATE TABLE IF NOT EXISTS customer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    amount_paid FLOAT NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_date TIMESTAMP DEFAULT NOW(),
    paypal_order_id VARCHAR(120),
    crypto_currency VARCHAR(10),
    crypto_address VARCHAR(200),
    transaction_hash VARCHAR(200)
);

-- Backup existing booking data before migration
CREATE TABLE IF NOT EXISTS booking_backup AS SELECT * FROM booking;

-- Step 1: Create customers from existing booking data
INSERT INTO customer (name, email, phone, created_at)
SELECT DISTINCT 
    COALESCE(booking.name, 'Unknown') as name,
    COALESCE(booking.email, 'unknown@email.com') as email, 
    booking.phone,
    NOW() as created_at
FROM booking 
WHERE booking.name IS NOT NULL OR booking.email IS NOT NULL
ON CONFLICT DO NOTHING;

-- Step 2: Add new columns to booking table
ALTER TABLE booking ADD COLUMN IF NOT EXISTS customer_id INTEGER;
ALTER TABLE booking ADD COLUMN IF NOT EXISTS booking_date TIMESTAMP DEFAULT NOW();
ALTER TABLE booking ADD COLUMN IF NOT EXISTS checked_in BOOLEAN DEFAULT FALSE;
ALTER TABLE booking ADD COLUMN IF NOT EXISTS checkin_time TIMESTAMP;
ALTER TABLE booking ADD COLUMN IF NOT EXISTS event_id INTEGER;

-- Step 3: Link bookings to customers
UPDATE booking SET customer_id = (
    SELECT c.id FROM customer c 
    WHERE (c.email = booking.email AND booking.email IS NOT NULL)
    OR (c.name = booking.name AND booking.name IS NOT NULL AND booking.email IS NULL)
    ORDER BY c.id LIMIT 1
) WHERE customer_id IS NULL;

-- Step 4: Set booking_date from existing time_slot if available
UPDATE booking SET booking_date = COALESCE(time_slot, NOW()) WHERE booking_date IS NULL;

-- Step 5: Create payment records from existing booking data
INSERT INTO payment (booking_id, amount_paid, currency, status, payment_method, payment_date, paypal_order_id)
SELECT 
    booking.id as booking_id,
    COALESCE(booking.amount_paid, 0) as amount_paid,
    COALESCE(booking.currency, 'USD') as currency,
    CASE 
        WHEN booking.status = 'completed' THEN 'COMPLETED'
        WHEN booking.status = 'confirmed' THEN 'COMPLETED'
        WHEN booking.status ILIKE '%complete%' THEN 'COMPLETED'
        ELSE COALESCE(booking.status, 'pending')
    END as status,
    'paypal' as payment_method,
    COALESCE(booking.booking_date, NOW()) as payment_date,
    NULL as paypal_order_id
FROM booking 
WHERE NOT EXISTS (SELECT 1 FROM payment WHERE payment.booking_id = booking.id);

-- Step 6: Add missing columns to event table
ALTER TABLE event ADD COLUMN IF NOT EXISTS max_capacity INTEGER NOT NULL DEFAULT 50;
ALTER TABLE event ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Step 7: Create default user if none exists
INSERT INTO "user" (username, password) 
SELECT 'admin', 'petunia'
WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'admin');

-- Step 8: Link events to default user
UPDATE event SET user_id = (SELECT id FROM "user" WHERE username = 'admin' LIMIT 1) 
WHERE user_id IS NULL;

-- Step 9: Update waiver table to use customer relationship
ALTER TABLE waiver ADD COLUMN IF NOT EXISTS customer_id INTEGER;

-- Link waivers to customers based on order_id
UPDATE waiver SET customer_id = (
    SELECT b.customer_id 
    FROM booking b 
    WHERE b.order_id = waiver.order_id 
    LIMIT 1
) WHERE customer_id IS NULL;

-- Step 10: Add foreign key constraints (only if columns exist and are populated)
DO $$
BEGIN
    -- Add customer constraint if column exists and is populated
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'booking' AND column_name = 'customer_id') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_booking_customer') THEN
            ALTER TABLE booking ADD CONSTRAINT fk_booking_customer 
                FOREIGN KEY (customer_id) REFERENCES customer(id);
        END IF;
    END IF;
    
    -- Add payment constraint
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_payment_booking') THEN
        ALTER TABLE payment ADD CONSTRAINT fk_payment_booking 
            FOREIGN KEY (booking_id) REFERENCES booking(id);
    END IF;
    
    -- Add event user constraint if user_id exists
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'user_id') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_event_user') THEN
            ALTER TABLE event ADD CONSTRAINT fk_event_user 
                FOREIGN KEY (user_id) REFERENCES "user"(id);
        END IF;
    END IF;
    
    -- Add waiver customer constraint if customer_id exists and is populated  
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'waiver' AND column_name = 'customer_id') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_waiver_customer') THEN
            ALTER TABLE waiver ADD CONSTRAINT fk_waiver_customer 
                FOREIGN KEY (customer_id) REFERENCES customer(id);
        END IF;
    END IF;
END $$;

-- Step 11: Verification queries
DO $$
BEGIN
    RAISE NOTICE 'Migration Summary:';
    RAISE NOTICE 'Customers created: %', (SELECT COUNT(*) FROM customer);
    RAISE NOTICE 'Payments created: %', (SELECT COUNT(*) FROM payment);
    RAISE NOTICE 'Bookings with customers: %', (SELECT COUNT(*) FROM booking WHERE customer_id IS NOT NULL);
    RAISE NOTICE 'Events with users: %', (SELECT COUNT(*) FROM event WHERE user_id IS NOT NULL);
END $$;

-- Don't drop old columns yet - keep them for safety
-- After verifying everything works, you can manually run:
-- ALTER TABLE booking DROP COLUMN IF EXISTS name;
-- ALTER TABLE booking DROP COLUMN IF EXISTS email; 
-- ALTER TABLE booking DROP COLUMN IF EXISTS phone;
-- ALTER TABLE booking DROP COLUMN IF EXISTS amount_paid;
-- ALTER TABLE booking DROP COLUMN IF EXISTS currency;
-- ALTER TABLE booking DROP COLUMN IF EXISTS status;
-- ALTER TABLE booking DROP COLUMN IF EXISTS time_slot;

COMMIT;