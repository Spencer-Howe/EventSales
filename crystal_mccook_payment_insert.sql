-- Insert Pay-by-Hay booking for Crystal McCook  
-- Pay-by-Hay Program (No PayPal transaction)
-- Event ID: 683
-- Date: Dec 21, 2025
-- Tickets: 5
-- Special Note: Daughter has severe cinnamon allergy

-- Step 1: Insert customer record (skip if already exists)
INSERT INTO customer (name, email, phone, created_at)
SELECT 'Crystal McCook', 'mccookcj@gmail.com', '9092611171', '2025-12-04 15:15:00'
WHERE NOT EXISTS (
    SELECT 1 FROM customer WHERE email = 'mccookcj@gmail.com'
);

-- Step 2: Insert booking record
INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id, receipt_sent)
VALUES (
    'HAY683MCCOOK2025',
    5,
    '2025-12-21 15:00:00', 
    FALSE, 
    FALSE, 
    NULL, 
    (SELECT id FROM customer WHERE email = 'mccookcj@gmail.com'),
    683,
    FALSE
);

-- Step 3: Insert payment record
INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
VALUES (
    0.00,
    'USD', 
    'completed', 
    'pay-by-hay', 
    '2025-12-04 15:15:00',
    'HAY683MCCOOK2025',
    (SELECT id FROM booking WHERE order_id = 'HAY683MCCOOK2025')
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
WHERE b.order_id = 'HAY683MCCOOK2025';