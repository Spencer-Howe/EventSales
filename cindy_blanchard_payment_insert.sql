-- Insert missing PayPal booking for Cindy Blanchard
-- Transaction ID: 0FW33387LW522893T
-- Amount: $70.00 USD
-- Event ID: 638
-- Date: Nov 22, 2025
-- Tickets: 2

-- Insert customer record (PostgreSQL syntax)
INSERT INTO customer (name, email, phone, created_at)
VALUES ('Chasen Marshall', 'chasen.marshall@yahoo.com', 4242191779, '2025-11-08 00:00:00')
ON CONFLICT (email) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email;

-- Get the customer ID (PostgreSQL variable syntax)
SELECT id FROM customer WHERE email = 'chasen.marshall@yahoo.com' \gset customer_id

-- Insert booking record
INSERT INTO booking (order_id, tickets, booking_date, reminder_sent, checked_in, checkin_time, customer_id, event_id)
VALUES ('47305592FS357260J', 2, '2025-11-08 00:00:00', FALSE, FALSE, NULL, :customer_id, 678);

-- Get the booking ID
SELECT id FROM booking WHERE order_id = '47305592FS357260J' \gset booking_id

-- Insert payment record
INSERT INTO payment (amount_paid, currency, status, payment_method, payment_date, paypal_order_id, booking_id)
VALUES (70.00, 'USD', 'completed', 'paypal', '2025-11-22 00:00:00', '47305592FS357260J', :booking_id);

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
WHERE b.order_id = '47305592FS357260J';