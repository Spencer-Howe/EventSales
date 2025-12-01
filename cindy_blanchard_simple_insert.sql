-- Insert missing PayPal booking for Chasen Marshall
-- Transaction ID: 47305592FS357260J
-- Amount: $70.00 USD
-- Event ID: 638
-- Date: Nov 22, 2025
-- Tickets: 2

-- Step 1: Insert customer record (skip if already exists)
INSERT INTO customer (name, email, phone, created_at)
SELECT 'Chasen Marshall', 'chasen.marshall@yahoo.com', 4242191779, '2025-11-22 00:00:00'
WHERE NOT EXISTS (
    SELECT 1 FROM customer WHERE email = 'chasen.marshall@yahoo.com'
);

-- Step 2: Insert booking record
INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id)
VALUES (
    '47305592FS357260J',
    2, 
    '2025-11-22 00:00:00', 
    FALSE, 
    FALSE, 
    NULL, 
    (SELECT id FROM customer WHERE email = 'chasen.marshall@yahoo.com'),
    638
);

-- Step 3: Insert payment record
INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
VALUES (
    70.00, 
    'USD', 
    'completed', 
    'paypal', 
    '2025-11-22 00:00:00', 
    '47305592FS357260J',
    (SELECT id FROM booking WHERE order_id = '47305592FS357260J')
);

-- Step 4: Verify the insertion
SELECT 
    c.name,
    c.email,
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
WHERE b.order_id = '47305592FS357260J';