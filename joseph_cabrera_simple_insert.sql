-- Insert booking for Joseph Cabrera
-- Email correction needed: original wrong email in reservation for 14th at 4pm
-- Transaction ID: 5YA42765034387726
-- Amount: $70.00 USD
-- Event ID: 681
-- Date: November 25, 2025 at 4:59:53 PM PST
-- Phone: 619-510-2611

-- Step 1: Insert customer record (skip if already exists)
INSERT INTO customer (name, email, phone, created_at)
SELECT 'Joseph Cabrera', 'jcabrera81600@gmail.com', '619-510-2611', '2025-11-25 21:59:53'
WHERE NOT EXISTS (
    SELECT 1 FROM customer WHERE phone = '619-510-2611'
);

-- Step 2: Insert booking record
INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id, receipt_sent)
VALUES (
    '5YA42765034387726',
    2,
    '2025-11-25 21:59:53', 
    FALSE, 
    FALSE, 
    NULL, 
    (SELECT id FROM customer WHERE phone = '619-510-2611'),
    681,
    TRUE
);

-- Step 3: Insert payment record
INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
VALUES (
    70.00,
    'USD', 
    'completed', 
    'paypal', 
    '2025-11-25 21:59:53',
    '5YA42765034387726',
    (SELECT id FROM booking WHERE order_id = '5YA42765034387726')
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
WHERE b.order_id = '5YA42765034387726';