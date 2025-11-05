-- Insert Private Mini Moo events for December 2025 and January 2026
-- Based on event ID 645 but with scavenger hunt removed from description

INSERT INTO event (title, start, "end", description, price_per_ticket, private, is_private, is_booked, max_capacity, user_id)
SELECT e.title,
       v.ts AS start,
       v.ts + interval '1 hour' AS "end",
       '🐮 Immerse yourself in a one-of-a-kind farm adventure at Howe Ranch with our Private Mini Moo Experience, perfect for couples, families, and small groups (1–10 guests). Enjoy snuggles with our tiniest fluffy Highland calves, bottle feed our 3 special bottle babies, and connect with alpacas, playful mini goats, donkeys, and chickens. Explore the farm, capture beautiful photos with baby calves at scenic backdrops, and take home a special souvenir bag. Designed for intimate groups, this exclusive visit ensures a relaxed pace, magical animal moments, and plenty of farm fun. 🐄✨🐰' AS description,
       e.price_per_ticket,
       e.private,
       e.is_private,
       e.is_booked,
       e.max_capacity,
       e.user_id
FROM event e
JOIN (
  VALUES
    -- DEC 1, 2025: 11 AM, 4 PM, 5 PM, 6 PM, 7 PM
    (timestamp '2025-12-01 11:00:00'),
    (timestamp '2025-12-01 16:00:00'),
    (timestamp '2025-12-01 17:00:00'),
    (timestamp '2025-12-01 18:00:00'),
    (timestamp '2025-12-01 19:00:00'),

    -- DEC 2, 2025: 11 AM, 4 PM, 5 PM, 6 PM, 7 PM
    (timestamp '2025-12-02 11:00:00'),
    (timestamp '2025-12-02 16:00:00'),
    (timestamp '2025-12-02 17:00:00'),
    (timestamp '2025-12-02 18:00:00'),
    (timestamp '2025-12-02 19:00:00'),

    -- DEC 3, 2025: 11 AM, 4 PM, 5 PM, 6 PM, 7 PM
    (timestamp '2025-12-03 11:00:00'),
    (timestamp '2025-12-03 16:00:00'),
    (timestamp '2025-12-03 17:00:00'),
    (timestamp '2025-12-03 18:00:00'),
    (timestamp '2025-12-03 19:00:00'),

    -- DEC 4, 2025: 11 AM, 4 PM, 5 PM, 6 PM, 7 PM
    (timestamp '2025-12-04 11:00:00'),
    (timestamp '2025-12-04 16:00:00'),
    (timestamp '2025-12-04 17:00:00'),
    (timestamp '2025-12-04 18:00:00'),
    (timestamp '2025-12-04 19:00:00'),

    -- DEC 5, 2025: 11 AM, 4 PM, 5 PM, 6 PM, 7 PM
    (timestamp '2025-12-05 11:00:00'),
    (timestamp '2025-12-05 16:00:00'),
    (timestamp '2025-12-05 17:00:00'),
    (timestamp '2025-12-05 18:00:00'),
    (timestamp '2025-12-05 19:00:00'),

    -- DEC 6, 2025: 9 AM, 10 AM, 11 AM, 12 PM
    (timestamp '2025-12-06 09:00:00'),
    (timestamp '2025-12-06 10:00:00'),
    (timestamp '2025-12-06 11:00:00'),
    (timestamp '2025-12-06 12:00:00'),

    -- DEC 7, 2025: 10 AM, 11 AM, 7 PM
    (timestamp '2025-12-07 10:00:00'),
    (timestamp '2025-12-07 11:00:00'),
    (timestamp '2025-12-07 19:00:00'),

    -- DEC 8, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-08 11:00:00'),
    (timestamp '2025-12-08 12:00:00'),
    (timestamp '2025-12-08 13:00:00'),
    (timestamp '2025-12-08 14:00:00'),
    (timestamp '2025-12-08 15:00:00'),
    (timestamp '2025-12-08 16:00:00'),
    (timestamp '2025-12-08 18:00:00'),
    (timestamp '2025-12-08 19:00:00'),

    -- DEC 9, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-09 11:00:00'),
    (timestamp '2025-12-09 12:00:00'),
    (timestamp '2025-12-09 13:00:00'),
    (timestamp '2025-12-09 14:00:00'),
    (timestamp '2025-12-09 15:00:00'),
    (timestamp '2025-12-09 16:00:00'),
    (timestamp '2025-12-09 18:00:00'),
    (timestamp '2025-12-09 19:00:00'),

    -- DEC 10, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-10 11:00:00'),
    (timestamp '2025-12-10 12:00:00'),
    (timestamp '2025-12-10 13:00:00'),
    (timestamp '2025-12-10 14:00:00'),
    (timestamp '2025-12-10 15:00:00'),
    (timestamp '2025-12-10 16:00:00'),
    (timestamp '2025-12-10 18:00:00'),
    (timestamp '2025-12-10 19:00:00'),

    -- DEC 11, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-11 11:00:00'),
    (timestamp '2025-12-11 12:00:00'),
    (timestamp '2025-12-11 13:00:00'),
    (timestamp '2025-12-11 14:00:00'),
    (timestamp '2025-12-11 15:00:00'),
    (timestamp '2025-12-11 16:00:00'),
    (timestamp '2025-12-11 18:00:00'),
    (timestamp '2025-12-11 19:00:00'),

    -- DEC 12, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-12 11:00:00'),
    (timestamp '2025-12-12 12:00:00'),
    (timestamp '2025-12-12 13:00:00'),
    (timestamp '2025-12-12 14:00:00'),
    (timestamp '2025-12-12 15:00:00'),
    (timestamp '2025-12-12 16:00:00'),
    (timestamp '2025-12-12 18:00:00'),
    (timestamp '2025-12-12 19:00:00'),

    -- DEC 13, 2025: 9 AM, 10 AM
    (timestamp '2025-12-13 09:00:00'),
    (timestamp '2025-12-13 10:00:00'),

    -- DEC 14, 2025: 10 AM, 11 AM, 7 PM
    (timestamp '2025-12-14 10:00:00'),
    (timestamp '2025-12-14 11:00:00'),
    (timestamp '2025-12-14 19:00:00'),

    -- DEC 15, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-15 11:00:00'),
    (timestamp '2025-12-15 12:00:00'),
    (timestamp '2025-12-15 13:00:00'),
    (timestamp '2025-12-15 14:00:00'),
    (timestamp '2025-12-15 15:00:00'),
    (timestamp '2025-12-15 16:00:00'),
    (timestamp '2025-12-15 18:00:00'),
    (timestamp '2025-12-15 19:00:00'),

    -- DEC 16, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-16 11:00:00'),
    (timestamp '2025-12-16 12:00:00'),
    (timestamp '2025-12-16 13:00:00'),
    (timestamp '2025-12-16 14:00:00'),
    (timestamp '2025-12-16 15:00:00'),
    (timestamp '2025-12-16 16:00:00'),
    (timestamp '2025-12-16 18:00:00'),
    (timestamp '2025-12-16 19:00:00'),

    -- DEC 17, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-17 11:00:00'),
    (timestamp '2025-12-17 12:00:00'),
    (timestamp '2025-12-17 13:00:00'),
    (timestamp '2025-12-17 14:00:00'),
    (timestamp '2025-12-17 15:00:00'),
    (timestamp '2025-12-17 16:00:00'),
    (timestamp '2025-12-17 18:00:00'),
    (timestamp '2025-12-17 19:00:00'),

    -- DEC 18, 2025: 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-18 12:00:00'),
    (timestamp '2025-12-18 13:00:00'),
    (timestamp '2025-12-18 14:00:00'),
    (timestamp '2025-12-18 15:00:00'),
    (timestamp '2025-12-18 16:00:00'),
    (timestamp '2025-12-18 18:00:00'),
    (timestamp '2025-12-18 19:00:00'),

    -- DEC 19, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-19 11:00:00'),
    (timestamp '2025-12-19 12:00:00'),
    (timestamp '2025-12-19 13:00:00'),
    (timestamp '2025-12-19 14:00:00'),
    (timestamp '2025-12-19 15:00:00'),
    (timestamp '2025-12-19 16:00:00'),
    (timestamp '2025-12-19 18:00:00'),
    (timestamp '2025-12-19 19:00:00'),

    -- DEC 20, 2025: 9 AM, 10 AM, 11 AM
    (timestamp '2025-12-20 09:00:00'),
    (timestamp '2025-12-20 10:00:00'),
    (timestamp '2025-12-20 11:00:00'),

    -- DEC 21, 2025: 10 AM, 7 PM
    (timestamp '2025-12-21 10:00:00'),
    (timestamp '2025-12-21 19:00:00'),

    -- DEC 22, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-22 11:00:00'),
    (timestamp '2025-12-22 12:00:00'),
    (timestamp '2025-12-22 13:00:00'),
    (timestamp '2025-12-22 14:00:00'),
    (timestamp '2025-12-22 15:00:00'),
    (timestamp '2025-12-22 16:00:00'),
    (timestamp '2025-12-22 18:00:00'),
    (timestamp '2025-12-22 19:00:00'),

    -- DEC 23, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-23 11:00:00'),
    (timestamp '2025-12-23 12:00:00'),
    (timestamp '2025-12-23 13:00:00'),
    (timestamp '2025-12-23 14:00:00'),
    (timestamp '2025-12-23 15:00:00'),
    (timestamp '2025-12-23 16:00:00'),
    (timestamp '2025-12-23 18:00:00'),
    (timestamp '2025-12-23 19:00:00'),

    -- DEC 24, 2025: 12 PM, 1 PM, 2 PM
    (timestamp '2025-12-24 12:00:00'),
    (timestamp '2025-12-24 13:00:00'),
    (timestamp '2025-12-24 14:00:00'),

    -- DEC 26, 2025: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2025-12-26 11:00:00'),
    (timestamp '2025-12-26 12:00:00'),
    (timestamp '2025-12-26 13:00:00'),
    (timestamp '2025-12-26 14:00:00'),
    (timestamp '2025-12-26 15:00:00'),
    (timestamp '2025-12-26 16:00:00'),
    (timestamp '2025-12-26 18:00:00'),
    (timestamp '2025-12-26 19:00:00'),

    -- DEC 27, 2025: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2025-12-27 10:00:00'),
    (timestamp '2025-12-27 11:00:00'),
    (timestamp '2025-12-27 12:00:00'),
    (timestamp '2025-12-27 13:00:00'),
    (timestamp '2025-12-27 14:00:00'),
    (timestamp '2025-12-27 15:00:00'),
    (timestamp '2025-12-27 16:00:00'),
    (timestamp '2025-12-27 17:00:00'),
    (timestamp '2025-12-27 18:00:00'),

    -- DEC 28, 2025: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2025-12-28 10:00:00'),
    (timestamp '2025-12-28 11:00:00'),
    (timestamp '2025-12-28 12:00:00'),
    (timestamp '2025-12-28 13:00:00'),
    (timestamp '2025-12-28 14:00:00'),
    (timestamp '2025-12-28 15:00:00'),
    (timestamp '2025-12-28 16:00:00'),
    (timestamp '2025-12-28 17:00:00'),
    (timestamp '2025-12-28 18:00:00'),

    -- DEC 30, 2025: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2025-12-30 10:00:00'),
    (timestamp '2025-12-30 11:00:00'),
    (timestamp '2025-12-30 12:00:00'),
    (timestamp '2025-12-30 13:00:00'),
    (timestamp '2025-12-30 14:00:00'),
    (timestamp '2025-12-30 15:00:00'),
    (timestamp '2025-12-30 16:00:00'),
    (timestamp '2025-12-30 17:00:00'),
    (timestamp '2025-12-30 18:00:00'),

    -- DEC 31, 2025: 12 PM, 1 PM, 2 PM
    (timestamp '2025-12-31 12:00:00'),
    (timestamp '2025-12-31 13:00:00'),
    (timestamp '2025-12-31 14:00:00'),

    -- JAN 1, 2026: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-01 10:00:00'),
    (timestamp '2026-01-01 11:00:00'),
    (timestamp '2026-01-01 12:00:00'),
    (timestamp '2026-01-01 13:00:00'),
    (timestamp '2026-01-01 14:00:00'),
    (timestamp '2026-01-01 15:00:00'),
    (timestamp '2026-01-01 16:00:00'),
    (timestamp '2026-01-01 17:00:00'),
    (timestamp '2026-01-01 18:00:00'),

    -- JAN 2, 2026: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-02 10:00:00'),
    (timestamp '2026-01-02 11:00:00'),
    (timestamp '2026-01-02 12:00:00'),
    (timestamp '2026-01-02 13:00:00'),
    (timestamp '2026-01-02 14:00:00'),
    (timestamp '2026-01-02 15:00:00'),
    (timestamp '2026-01-02 16:00:00'),
    (timestamp '2026-01-02 17:00:00'),
    (timestamp '2026-01-02 18:00:00'),

    -- JAN 3, 2026: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-03 10:00:00'),
    (timestamp '2026-01-03 11:00:00'),
    (timestamp '2026-01-03 12:00:00'),
    (timestamp '2026-01-03 13:00:00'),
    (timestamp '2026-01-03 14:00:00'),
    (timestamp '2026-01-03 15:00:00'),
    (timestamp '2026-01-03 16:00:00'),
    (timestamp '2026-01-03 17:00:00'),
    (timestamp '2026-01-03 18:00:00'),

    -- JAN 4, 2026: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-04 10:00:00'),
    (timestamp '2026-01-04 11:00:00'),
    (timestamp '2026-01-04 12:00:00'),
    (timestamp '2026-01-04 13:00:00'),
    (timestamp '2026-01-04 14:00:00'),
    (timestamp '2026-01-04 15:00:00'),
    (timestamp '2026-01-04 16:00:00'),
    (timestamp '2026-01-04 17:00:00'),
    (timestamp '2026-01-04 18:00:00'),

    -- JAN 5, 2026: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2026-01-05 11:00:00'),
    (timestamp '2026-01-05 12:00:00'),
    (timestamp '2026-01-05 13:00:00'),
    (timestamp '2026-01-05 14:00:00'),
    (timestamp '2026-01-05 15:00:00'),
    (timestamp '2026-01-05 16:00:00'),
    (timestamp '2026-01-05 18:00:00'),
    (timestamp '2026-01-05 19:00:00'),

    -- JAN 6, 2026: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2026-01-06 11:00:00'),
    (timestamp '2026-01-06 12:00:00'),
    (timestamp '2026-01-06 13:00:00'),
    (timestamp '2026-01-06 14:00:00'),
    (timestamp '2026-01-06 15:00:00'),
    (timestamp '2026-01-06 16:00:00'),
    (timestamp '2026-01-06 18:00:00'),
    (timestamp '2026-01-06 19:00:00'),

    -- JAN 7, 2026: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2026-01-07 11:00:00'),
    (timestamp '2026-01-07 12:00:00'),
    (timestamp '2026-01-07 13:00:00'),
    (timestamp '2026-01-07 14:00:00'),
    (timestamp '2026-01-07 15:00:00'),
    (timestamp '2026-01-07 16:00:00'),
    (timestamp '2026-01-07 18:00:00'),
    (timestamp '2026-01-07 19:00:00'),

    -- JAN 8, 2026: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2026-01-08 11:00:00'),
    (timestamp '2026-01-08 12:00:00'),
    (timestamp '2026-01-08 13:00:00'),
    (timestamp '2026-01-08 14:00:00'),
    (timestamp '2026-01-08 15:00:00'),
    (timestamp '2026-01-08 16:00:00'),
    (timestamp '2026-01-08 18:00:00'),
    (timestamp '2026-01-08 19:00:00'),

    -- JAN 9, 2026: 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 6 PM, 7 PM
    (timestamp '2026-01-09 11:00:00'),
    (timestamp '2026-01-09 12:00:00'),
    (timestamp '2026-01-09 13:00:00'),
    (timestamp '2026-01-09 14:00:00'),
    (timestamp '2026-01-09 15:00:00'),
    (timestamp '2026-01-09 16:00:00'),
    (timestamp '2026-01-09 18:00:00'),
    (timestamp '2026-01-09 19:00:00')
) AS v(ts)
ON TRUE
WHERE e.id = 645;