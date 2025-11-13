-- Insert missing PayPal booking for Damian Valle
-- Transaction ID: 51A22113PE246752F
-- Amount: $70.00 USD
-- Event ID: 676
-- Date: Nov 11, 2025 19:52:58 PST

-- Insert customer record
INSERT INTO customer (name, email, phone, created_at)
VALUES ('Damian Valle', 'dmv609@icloud.com', NULL, '2025-11-11 19:52:58')
ON DUPLICATE KEY UPDATE 
    name = VALUES(name),
    email = VALUES(email);

-- Get the customer ID (use this in the next queries)
SET @customer_id = (SELECT id FROM customer WHERE email = 'dmv609@icloud.com');

-- Insert booking record
INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id)
VALUES ('51A22113PE246752F', 1, '2025-11-11 19:52:58', FALSE, FALSE, NULL, @customer_id, 676);

-- Get the booking ID
SET @booking_id = (SELECT id FROM booking WHERE order_id = '51A22113PE246752F');

-- Insert payment record
INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
VALUES (70.00, 'USD', 'completed', 'paypal', '2025-11-11 19:52:58', '51A22113PE246752F', @booking_id);

-- Verify the insertion
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
WHERE b.order_id = '51A22113PE246752F';


 INSERT INTO customer (name, email, phone, created_at)
  VALUES ('Damian Valle', 'dmv609@icloud.com', NULL, '2025-11-11 19:52:58');

  INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id)
  VALUES ('51A22113PE246752F', 2, '2025-11-11 19:52:58', FALSE, FALSE, NULL, (SELECT id FROM customer WHERE email = 'dmv609@icloud.com'), 676);

  INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
  VALUES (70.00, 'USD', 'completed', 'paypal', '2025-11-11 19:52:58', '51A22113PE246752F', (SELECT id FROM booking WHERE order_id = '51A22113PE246752F'));

