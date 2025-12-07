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
        -- JAN 1, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-01-01 11:00:00'),
    (timestamp '2026-01-01 12:00:00'),
    (timestamp '2026-01-01 13:00:00'),
    (timestamp '2026-01-01 14:00:00'),
    (timestamp '2026-01-01 15:00:00'),
    (timestamp '2026-01-01 16:00:00'),
    (timestamp '2026-01-01 17:00:00'),
    (timestamp '2026-01-01 18:00:00'),

    -- JAN 2, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-01-02 11:00:00'),
    (timestamp '2026-01-02 12:00:00'),
    (timestamp '2026-01-02 13:00:00'),
    (timestamp '2026-01-02 14:00:00'),
    (timestamp '2026-01-02 15:00:00'),
    (timestamp '2026-01-02 16:00:00'),
    (timestamp '2026-01-02 17:00:00'),
    (timestamp '2026-01-02 18:00:00'),

    -- JAN 3, 2026 (SAT): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-03 11:00:00'),
    (timestamp '2026-01-03 12:00:00'),
    (timestamp '2026-01-03 13:00:00'),
    (timestamp '2026-01-03 16:00:00'),
    (timestamp '2026-01-03 17:00:00'),
    (timestamp '2026-01-03 18:00:00'),

    -- JAN 4, 2026 (SUN): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-04 11:00:00'),
    (timestamp '2026-01-04 12:00:00'),
    (timestamp '2026-01-04 13:00:00'),
    (timestamp '2026-01-04 16:00:00'),
    (timestamp '2026-01-04 17:00:00'),
    (timestamp '2026-01-04 18:00:00'),

    -- JAN 7, 2026 (WED): 11 AM–6 PM
    (timestamp '2026-01-07 11:00:00'),
    (timestamp '2026-01-07 12:00:00'),
    (timestamp '2026-01-07 13:00:00'),
    (timestamp '2026-01-07 14:00:00'),
    (timestamp '2026-01-07 15:00:00'),
    (timestamp '2026-01-07 16:00:00'),
    (timestamp '2026-01-07 17:00:00'),
    (timestamp '2026-01-07 18:00:00'),

    -- JAN 8, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-01-08 11:00:00'),
    (timestamp '2026-01-08 12:00:00'),
    (timestamp '2026-01-08 13:00:00'),
    (timestamp '2026-01-08 14:00:00'),
    (timestamp '2026-01-08 15:00:00'),
    (timestamp '2026-01-08 16:00:00'),
    (timestamp '2026-01-08 17:00:00'),
    (timestamp '2026-01-08 18:00:00'),

    -- JAN 9, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-01-09 11:00:00'),
    (timestamp '2026-01-09 12:00:00'),
    (timestamp '2026-01-09 13:00:00'),
    (timestamp '2026-01-09 14:00:00'),
    (timestamp '2026-01-09 15:00:00'),
    (timestamp '2026-01-09 16:00:00'),
    (timestamp '2026-01-09 17:00:00'),
    (timestamp '2026-01-09 18:00:00'),

 -- JAN 10, 2026 (SAT): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-10 11:00:00'),
    (timestamp '2026-01-10 12:00:00'),
    (timestamp '2026-01-10 13:00:00'),
    (timestamp '2026-01-10 16:00:00'),
    (timestamp '2026-01-10 17:00:00'),
    (timestamp '2026-01-10 18:00:00'),

    -- JAN 11, 2026 (SUN): 11 AM, 12 PM, 1 PM, 2 PM
    (timestamp '2026-01-11 11:00:00'),
    (timestamp '2026-01-11 12:00:00'),
    (timestamp '2026-01-11 13:00:00'),
    (timestamp '2026-01-11 14:00:00'),

    -- JAN 14, 2026 (WED): 11 AM–6 PM
    (timestamp '2026-01-14 11:00:00'),
    (timestamp '2026-01-14 12:00:00'),
    (timestamp '2026-01-14 13:00:00'),
    (timestamp '2026-01-14 14:00:00'),
    (timestamp '2026-01-14 15:00:00'),
    (timestamp '2026-01-14 16:00:00'),
    (timestamp '2026-01-14 17:00:00'),
    (timestamp '2026-01-14 18:00:00'),

    -- JAN 15, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-01-15 11:00:00'),
    (timestamp '2026-01-15 12:00:00'),
    (timestamp '2026-01-15 13:00:00'),
    (timestamp '2026-01-15 14:00:00'),
    (timestamp '2026-01-15 15:00:00'),
    (timestamp '2026-01-15 16:00:00'),
    (timestamp '2026-01-15 17:00:00'),
    (timestamp '2026-01-15 18:00:00'),

    -- JAN 16, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-01-16 11:00:00'),
    (timestamp '2026-01-16 12:00:00'),
    (timestamp '2026-01-16 13:00:00'),
    (timestamp '2026-01-16 14:00:00'),
    (timestamp '2026-01-16 15:00:00'),
    (timestamp '2026-01-16 16:00:00'),
    (timestamp '2026-01-16 17:00:00'),
    (timestamp '2026-01-16 18:00:00'),

    -- JAN 17, 2026 (SAT): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-17 11:00:00'),
    (timestamp '2026-01-17 12:00:00'),
    (timestamp '2026-01-17 13:00:00'),
    (timestamp '2026-01-17 16:00:00'),
    (timestamp '2026-01-17 17:00:00'),
    (timestamp '2026-01-17 18:00:00'),

    -- JAN 18, 2026 (SUN): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-18 11:00:00'),
    (timestamp '2026-01-18 12:00:00'),
    (timestamp '2026-01-18 13:00:00'),
    (timestamp '2026-01-18 16:00:00'),
    (timestamp '2026-01-18 17:00:00'),
    (timestamp '2026-01-18 18:00:00'),

    -- JAN 21, 2026 (WED): 11 AM–6 PM
    (timestamp '2026-01-21 11:00:00'),
    (timestamp '2026-01-21 12:00:00'),
    (timestamp '2026-01-21 13:00:00'),
    (timestamp '2026-01-21 14:00:00'),
    (timestamp '2026-01-21 15:00:00'),
    (timestamp '2026-01-21 16:00:00'),
    (timestamp '2026-01-21 17:00:00'),
    (timestamp '2026-01-21 18:00:00'),

    -- JAN 22, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-01-22 11:00:00'),
    (timestamp '2026-01-22 12:00:00'),
    (timestamp '2026-01-22 13:00:00'),
    (timestamp '2026-01-22 14:00:00'),
    (timestamp '2026-01-22 15:00:00'),
    (timestamp '2026-01-22 16:00:00'),
    (timestamp '2026-01-22 17:00:00'),
    (timestamp '2026-01-22 18:00:00'),

    -- JAN 23, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-01-23 11:00:00'),
    (timestamp '2026-01-23 12:00:00'),
    (timestamp '2026-01-23 13:00:00'),
    (timestamp '2026-01-23 14:00:00'),
    (timestamp '2026-01-23 15:00:00'),
    (timestamp '2026-01-23 16:00:00'),
    (timestamp '2026-01-23 17:00:00'),
    (timestamp '2026-01-23 18:00:00'),

    -- JAN 24, 2026 (SAT): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-24 11:00:00'),
    (timestamp '2026-01-24 12:00:00'),
    (timestamp '2026-01-24 13:00:00'),
    (timestamp '2026-01-24 16:00:00'),
    (timestamp '2026-01-24 17:00:00'),
    (timestamp '2026-01-24 18:00:00'),

    -- JAN 25, 2026 (SUN): 11 AM, 12 PM, 1 PM, 2 PM
    (timestamp '2026-01-25 11:00:00'),
    (timestamp '2026-01-25 12:00:00'),
    (timestamp '2026-01-25 13:00:00'),
    (timestamp '2026-01-25 14:00:00'),

    -- JAN 28, 2026 (WED): 11 AM–6 PM
    (timestamp '2026-01-28 11:00:00'),
    (timestamp '2026-01-28 12:00:00'),
    (timestamp '2026-01-28 13:00:00'),
    (timestamp '2026-01-28 14:00:00'),
    (timestamp '2026-01-28 15:00:00'),
    (timestamp '2026-01-28 16:00:00'),
    (timestamp '2026-01-28 17:00:00'),
    (timestamp '2026-01-28 18:00:00'),

    -- JAN 29, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-01-29 11:00:00'),
    (timestamp '2026-01-29 12:00:00'),
    (timestamp '2026-01-29 13:00:00'),
    (timestamp '2026-01-29 14:00:00'),
    (timestamp '2026-01-29 15:00:00'),
    (timestamp '2026-01-29 16:00:00'),
    (timestamp '2026-01-29 17:00:00'),
    (timestamp '2026-01-29 18:00:00'),

    -- JAN 30, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-01-30 11:00:00'),
    (timestamp '2026-01-30 12:00:00'),
    (timestamp '2026-01-30 13:00:00'),
    (timestamp '2026-01-30 14:00:00'),
    (timestamp '2026-01-30 15:00:00'),
    (timestamp '2026-01-30 16:00:00'),
    (timestamp '2026-01-30 17:00:00'),
    (timestamp '2026-01-30 18:00:00'),

    -- JAN 31, 2026 (SAT): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-01-31 11:00:00'),
    (timestamp '2026-01-31 12:00:00'),
    (timestamp '2026-01-31 13:00:00'),
    (timestamp '2026-01-31 16:00:00'),
    (timestamp '2026-01-31 17:00:00'),
    (timestamp '2026-01-31 18:00:00'),

    -- FEB 1, 2026 (SUN): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-02-01 11:00:00'),
    (timestamp '2026-02-01 12:00:00'),
    (timestamp '2026-02-01 13:00:00'),
    (timestamp '2026-02-01 16:00:00'),
    (timestamp '2026-02-01 17:00:00'),
    (timestamp '2026-02-01 18:00:00'),

    -- FEB 4, 2026 (WED): 11 AM–6 PM
    (timestamp '2026-02-04 11:00:00'),
    (timestamp '2026-02-04 12:00:00'),
    (timestamp '2026-02-04 13:00:00'),
    (timestamp '2026-02-04 14:00:00'),
    (timestamp '2026-02-04 15:00:00'),
    (timestamp '2026-02-04 16:00:00'),
    (timestamp '2026-02-04 17:00:00'),
    (timestamp '2026-02-04 18:00:00'),

    -- FEB 5, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-02-05 11:00:00'),
    (timestamp '2026-02-05 12:00:00'),
    (timestamp '2026-02-05 13:00:00'),
    (timestamp '2026-02-05 14:00:00'),
    (timestamp '2026-02-05 15:00:00'),
    (timestamp '2026-02-05 16:00:00'),
    (timestamp '2026-02-05 17:00:00'),
    (timestamp '2026-02-05 18:00:00'),

    -- FEB 6, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-02-06 11:00:00'),
    (timestamp '2026-02-06 12:00:00'),
    (timestamp '2026-02-06 13:00:00'),
    (timestamp '2026-02-06 14:00:00'),
    (timestamp '2026-02-06 15:00:00'),
    (timestamp '2026-02-06 16:00:00'),
    (timestamp '2026-02-06 17:00:00'),
    (timestamp '2026-02-06 18:00:00'),

    -- FEB 7, 2026 (SAT): 11 AM, 12 PM, 1 PM, 4 PM, 5 PM, 6 PM
    (timestamp '2026-02-07 11:00:00'),
    (timestamp '2026-02-07 12:00:00'),
    (timestamp '2026-02-07 13:00:00'),
    (timestamp '2026-02-07 16:00:00'),
    (timestamp '2026-02-07 17:00:00'),
    (timestamp '2026-02-07 18:00:00'),

    -- FEB 8, 2026 (SUN): 11 AM, 12 PM, 1 PM, 2 PM
    (timestamp '2026-02-08 11:00:00'),
    (timestamp '2026-02-08 12:00:00'),
    (timestamp '2026-02-08 13:00:00'),
    (timestamp '2026-02-08 14:00:00'),

    -- FEB 11, 2026 (WED): 11 AM–6 PM
    (timestamp '2026-02-11 11:00:00'),
    (timestamp '2026-02-11 12:00:00'),
    (timestamp '2026-02-11 13:00:00'),
    (timestamp '2026-02-11 14:00:00'),
    (timestamp '2026-02-11 15:00:00'),
    (timestamp '2026-02-11 16:00:00'),
    (timestamp '2026-02-11 17:00:00'),
    (timestamp '2026-02-11 18:00:00'),

    -- FEB 12, 2026 (THU): 11 AM–6 PM
    (timestamp '2026-02-12 11:00:00'),
    (timestamp '2026-02-12 12:00:00'),
    (timestamp '2026-02-12 13:00:00'),
    (timestamp '2026-02-12 14:00:00'),
    (timestamp '2026-02-12 15:00:00'),
    (timestamp '2026-02-12 16:00:00'),
    (timestamp '2026-02-12 17:00:00'),
    (timestamp '2026-02-12 18:00:00'),

    -- FEB 13, 2026 (FRI): 11 AM–6 PM
    (timestamp '2026-02-13 11:00:00'),
    (timestamp '2026-02-13 12:00:00'),
    (timestamp '2026-02-13 13:00:00'),
    (timestamp '2026-02-13 14:00:00'),
    (timestamp '2026-02-13 15:00:00'),
    (timestamp '2026-02-13 16:00:00'),
    (timestamp '2026-02-13 17:00:00'),
    (timestamp '2026-02-13 18:00:00'),

    -- FEB 14, 2026 (SAT): 11 AM, 12 PM, 1 PM, 2 PM
    (timestamp '2026-02-14 11:00:00'),
    (timestamp '2026-02-14 12:00:00'),
    (timestamp '2026-02-14 13:00:00'),
    (timestamp '2026-02-14 14:00:00')
) AS v(ts)
ON TRUE
WHERE e.id = 786;