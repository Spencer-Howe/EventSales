-- Insert Venue Tour event for December 23, 2025
-- Venue Tour for February 21 - 35 Guests
-- Price: $150, Private: true, Is_booked: false

INSERT INTO event (
    title, 
    start, 
    "end", 
    description, 
    price_per_ticket, 
    private, 
    is_private, 
    is_booked, 
    max_capacity, 
    user_id
)
VALUES (
    'Venue Tour for February 21 - 35 Guests',
    timestamp '2025-12-23 17:00:00',
    timestamp '2025-12-23 18:00:00',
    'Private venue tour for February 21 event planning. Experience our beautiful ranch facility and explore options for hosting your special event with up to 35 guests. Tour includes facility walkthrough, amenities overview, and event planning consultation.',
    150.00,
    true,
    true,
    false,
    35,
    1
);

-- Verify the insertion
SELECT 
    id,
    title,
    start,
    "end",
    price_per_ticket,
    private,
    is_private,
    is_booked,
    max_capacity
FROM event 
WHERE title = 'Venue Tour for February 21 - 35 Guests'
ORDER BY id DESC 
LIMIT 1;