-- Insert booking for Daniel Dayon
-- Transaction ID: 6F32752922145734A
-- Amount: $140.00 USD
-- Event ID: 684
-- Date: December 6, 2025 at 6:01:22 PM PST
-- Email: dayon7@gmail.com
-- Tickets: 4

-- Step 1: Insert customer record (skip if already exists)
INSERT INTO customer (name, email, phone, created_at)
SELECT 'David Cabrera', 'davidc6077@gmail.com', NULL, '2025-12-06 18:01:22'
WHERE NOT EXISTS (
    SELECT 1 FROM customer WHERE email = 'davidc6077@gmail.com'
);

-- Step 2: Insert booking record
INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id, receipt_sent)
VALUES (
    '24X51052V4126361V',
    2,
    '2025-12-06 18:01:22', 
    FALSE, 
    FALSE, 
    NULL, 
    (SELECT id FROM customer WHERE email = 'davidc6077@gmail.com'),
    684,
    TRUE
);

-- Step 3: Insert payment record
INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
VALUES (
    70.00,
    'USD', 
    'completed', 
    'paypal', 
    '2025-12-06 18:01:22',
    '24X51052V4126361V',
    (SELECT id FROM booking WHERE order_id = '24X51052V4126361V')
);

-- Step 4: Verify the insertion
SELECT 
    c.name,
    c.email,
    c.phone,
    b.order_id,
    b.tickets,
    b.booking_date,
    b.event_id,
    p.amount_paid,
    p.currency,
    p.payment_method,
    p.paypal_order_id
FROM customer c
JOIN booking b ON c.id = b.customer_id
JOIN payment p ON b.id = p.booking_id
WHERE b.order_id = '24X51052V4126361V';