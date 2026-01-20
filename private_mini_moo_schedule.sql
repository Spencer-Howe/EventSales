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

    -- FEB 18, 2026 (TUE): 10 AM–7 PM
    (timestamp '2026-02-18 10:00:00'),
    (timestamp '2026-02-18 11:00:00'),
    (timestamp '2026-02-18 12:00:00'),
    (timestamp '2026-02-18 13:00:00'),
    (timestamp '2026-02-18 14:00:00'),
    (timestamp '2026-02-18 15:00:00'),
    (timestamp '2026-02-18 16:00:00'),
    (timestamp '2026-02-18 17:00:00'),
    (timestamp '2026-02-18 18:00:00'),
    (timestamp '2026-02-18 19:00:00'),

    -- FEB 19, 2026 (WED): 10 AM–7 PM
    (timestamp '2026-02-19 10:00:00'),
    (timestamp '2026-02-19 11:00:00'),
    (timestamp '2026-02-19 12:00:00'),
    (timestamp '2026-02-19 13:00:00'),
    (timestamp '2026-02-19 14:00:00'),
    (timestamp '2026-02-19 15:00:00'),
    (timestamp '2026-02-19 16:00:00'),
    (timestamp '2026-02-19 17:00:00'),
    (timestamp '2026-02-19 18:00:00'),
    (timestamp '2026-02-19 19:00:00'),

    -- FEB 20, 2026 (THU): 10 AM–7 PM
    (timestamp '2026-02-20 10:00:00'),
    (timestamp '2026-02-20 11:00:00'),
    (timestamp '2026-02-20 12:00:00'),
    (timestamp '2026-02-20 13:00:00'),
    (timestamp '2026-02-20 14:00:00'),
    (timestamp '2026-02-20 15:00:00'),
    (timestamp '2026-02-20 16:00:00'),
    (timestamp '2026-02-20 17:00:00'),
    (timestamp '2026-02-20 18:00:00'),
    (timestamp '2026-02-20 19:00:00'),

    -- FEB 21, 2026 (FRI): 10 AM–1 PM
    (timestamp '2026-02-21 10:00:00'),
    (timestamp '2026-02-21 11:00:00'),
    (timestamp '2026-02-21 12:00:00'),
    (timestamp '2026-02-21 13:00:00'),

    -- FEB 22, 2026 (SAT): 10 AM–1 PM
    (timestamp '2026-02-22 10:00:00'),
    (timestamp '2026-02-22 11:00:00'),
    (timestamp '2026-02-22 12:00:00'),
    (timestamp '2026-02-22 13:00:00'),

    -- FEB 25, 2026 (TUE): 10 AM–7 PM
    (timestamp '2026-02-25 10:00:00'),
    (timestamp '2026-02-25 11:00:00'),
    (timestamp '2026-02-25 12:00:00'),
    (timestamp '2026-02-25 13:00:00'),
    (timestamp '2026-02-25 14:00:00'),
    (timestamp '2026-02-25 15:00:00'),
    (timestamp '2026-02-25 16:00:00'),
    (timestamp '2026-02-25 17:00:00'),
    (timestamp '2026-02-25 18:00:00'),
    (timestamp '2026-02-25 19:00:00'),

    -- FEB 26, 2026 (WED): 10 AM–7 PM
    (timestamp '2026-02-26 10:00:00'),
    (timestamp '2026-02-26 11:00:00'),
    (timestamp '2026-02-26 12:00:00'),
    (timestamp '2026-02-26 13:00:00'),
    (timestamp '2026-02-26 14:00:00'),
    (timestamp '2026-02-26 15:00:00'),
    (timestamp '2026-02-26 16:00:00'),
    (timestamp '2026-02-26 17:00:00'),
    (timestamp '2026-02-26 18:00:00'),
    (timestamp '2026-02-26 19:00:00'),

    -- FEB 27, 2026 (THU): 10 AM–7 PM
    (timestamp '2026-02-27 10:00:00'),
    (timestamp '2026-02-27 11:00:00'),
    (timestamp '2026-02-27 12:00:00'),
    (timestamp '2026-02-27 13:00:00'),
    (timestamp '2026-02-27 14:00:00'),
    (timestamp '2026-02-27 15:00:00'),
    (timestamp '2026-02-27 16:00:00'),
    (timestamp '2026-02-27 17:00:00'),
    (timestamp '2026-02-27 18:00:00'),
    (timestamp '2026-02-27 19:00:00'),

    -- FEB 28, 2026 (FRI): 10 AM–1 PM
    (timestamp '2026-02-28 10:00:00'),
    (timestamp '2026-02-28 11:00:00'),
    (timestamp '2026-02-28 12:00:00'),
    (timestamp '2026-02-28 13:00:00'),

    -- MAR 1, 2026 (SAT): 10 AM–1 PM
    (timestamp '2026-03-01 10:00:00'),
    (timestamp '2026-03-01 11:00:00'),
    (timestamp '2026-03-01 12:00:00'),
    (timestamp '2026-03-01 13:00:00'),

    -- MAR 4, 2026 (TUE): 10 AM–7 PM
    (timestamp '2026-03-04 10:00:00'),
    (timestamp '2026-03-04 11:00:00'),
    (timestamp '2026-03-04 12:00:00'),
    (timestamp '2026-03-04 13:00:00'),
    (timestamp '2026-03-04 14:00:00'),
    (timestamp '2026-03-04 15:00:00'),
    (timestamp '2026-03-04 16:00:00'),
    (timestamp '2026-03-04 17:00:00'),
    (timestamp '2026-03-04 18:00:00'),
    (timestamp '2026-03-04 19:00:00'),

    -- MAR 5, 2026 (WED): 10 AM–7 PM
    (timestamp '2026-03-05 10:00:00'),
    (timestamp '2026-03-05 11:00:00'),
    (timestamp '2026-03-05 12:00:00'),
    (timestamp '2026-03-05 13:00:00'),
    (timestamp '2026-03-05 14:00:00'),
    (timestamp '2026-03-05 15:00:00'),
    (timestamp '2026-03-05 16:00:00'),
    (timestamp '2026-03-05 17:00:00'),
    (timestamp '2026-03-05 18:00:00'),
    (timestamp '2026-03-05 19:00:00'),

    -- MAR 6, 2026 (THU): 10 AM–7 PM
    (timestamp '2026-03-06 10:00:00'),
    (timestamp '2026-03-06 11:00:00'),
    (timestamp '2026-03-06 12:00:00'),
    (timestamp '2026-03-06 13:00:00'),
    (timestamp '2026-03-06 14:00:00'),
    (timestamp '2026-03-06 15:00:00'),
    (timestamp '2026-03-06 16:00:00'),
    (timestamp '2026-03-06 17:00:00'),
    (timestamp '2026-03-06 18:00:00'),
    (timestamp '2026-03-06 19:00:00'),

    -- MAR 7, 2026 (FRI): 10 AM–1 PM
    (timestamp '2026-03-07 10:00:00'),
    (timestamp '2026-03-07 11:00:00'),
    (timestamp '2026-03-07 12:00:00'),
    (timestamp '2026-03-07 13:00:00'),

    -- MAR 8, 2026 (SAT): 10 AM–1 PM
    (timestamp '2026-03-08 10:00:00'),
    (timestamp '2026-03-08 11:00:00'),
    (timestamp '2026-03-08 12:00:00'),
    (timestamp '2026-03-08 13:00:00'),

    -- MAR 11, 2026 (TUE): 10 AM–7 PM
    (timestamp '2026-03-11 10:00:00'),
    (timestamp '2026-03-11 11:00:00'),
    (timestamp '2026-03-11 12:00:00'),
    (timestamp '2026-03-11 13:00:00'),
    (timestamp '2026-03-11 14:00:00'),
    (timestamp '2026-03-11 15:00:00'),
    (timestamp '2026-03-11 16:00:00'),
    (timestamp '2026-03-11 17:00:00'),
    (timestamp '2026-03-11 18:00:00'),
    (timestamp '2026-03-11 19:00:00'),

    -- MAR 12, 2026 (WED): 10 AM–7 PM
    (timestamp '2026-03-12 10:00:00'),
    (timestamp '2026-03-12 11:00:00'),
    (timestamp '2026-03-12 12:00:00'),
    (timestamp '2026-03-12 13:00:00'),
    (timestamp '2026-03-12 14:00:00'),
    (timestamp '2026-03-12 15:00:00'),
    (timestamp '2026-03-12 16:00:00'),
    (timestamp '2026-03-12 17:00:00'),
    (timestamp '2026-03-12 18:00:00'),
    (timestamp '2026-03-12 19:00:00'),

    -- MAR 13, 2026 (THU): 10 AM–7 PM
    (timestamp '2026-03-13 10:00:00'),
    (timestamp '2026-03-13 11:00:00'),
    (timestamp '2026-03-13 12:00:00'),
    (timestamp '2026-03-13 13:00:00'),
    (timestamp '2026-03-13 14:00:00'),
    (timestamp '2026-03-13 15:00:00'),
    (timestamp '2026-03-13 16:00:00'),
    (timestamp '2026-03-13 17:00:00'),
    (timestamp '2026-03-13 18:00:00'),
    (timestamp '2026-03-13 19:00:00'),

    -- MAR 14, 2026 (FRI): 10 AM–1 PM
    (timestamp '2026-03-14 10:00:00'),
    (timestamp '2026-03-14 11:00:00'),
    (timestamp '2026-03-14 12:00:00'),
    (timestamp '2026-03-14 13:00:00'),

    -- MAR 15, 2026 (SAT): 10 AM–1 PM
    (timestamp '2026-03-15 10:00:00'),
    (timestamp '2026-03-15 11:00:00'),
    (timestamp '2026-03-15 12:00:00'),
    (timestamp '2026-03-15 13:00:00'),

    -- MAR 18, 2026 (TUE): 10 AM–7 PM
    (timestamp '2026-03-18 10:00:00'),
    (timestamp '2026-03-18 11:00:00'),
    (timestamp '2026-03-18 12:00:00'),
    (timestamp '2026-03-18 13:00:00'),
    (timestamp '2026-03-18 14:00:00'),
    (timestamp '2026-03-18 15:00:00'),
    (timestamp '2026-03-18 16:00:00'),
    (timestamp '2026-03-18 17:00:00'),
    (timestamp '2026-03-18 18:00:00'),
    (timestamp '2026-03-18 19:00:00'),

    -- MAR 19, 2026 (WED): 10 AM–7 PM
    (timestamp '2026-03-19 10:00:00'),
    (timestamp '2026-03-19 11:00:00'),
    (timestamp '2026-03-19 12:00:00'),
    (timestamp '2026-03-19 13:00:00'),
    (timestamp '2026-03-19 14:00:00'),
    (timestamp '2026-03-19 15:00:00'),
    (timestamp '2026-03-19 16:00:00'),
    (timestamp '2026-03-19 17:00:00'),
    (timestamp '2026-03-19 18:00:00'),
    (timestamp '2026-03-19 19:00:00'),

    -- MAR 20, 2026 (THU): 10 AM–7 PM
    (timestamp '2026-03-20 10:00:00'),
    (timestamp '2026-03-20 11:00:00'),
    (timestamp '2026-03-20 12:00:00'),
    (timestamp '2026-03-20 13:00:00'),
    (timestamp '2026-03-20 14:00:00'),
    (timestamp '2026-03-20 15:00:00'),
    (timestamp '2026-03-20 16:00:00'),
    (timestamp '2026-03-20 17:00:00'),
    (timestamp '2026-03-20 18:00:00'),
    (timestamp '2026-03-20 19:00:00'),

    -- MAR 21, 2026 (FRI): 10 AM–1 PM
    (timestamp '2026-03-21 10:00:00'),
    (timestamp '2026-03-21 11:00:00'),
    (timestamp '2026-03-21 12:00:00'),
    (timestamp '2026-03-21 13:00:00'),

    -- MAR 22, 2026 (SAT): 10 AM–1 PM
    (timestamp '2026-03-22 10:00:00'),
    (timestamp '2026-03-22 11:00:00'),
    (timestamp '2026-03-22 12:00:00'),
    (timestamp '2026-03-22 13:00:00')
) AS v(ts)
ON TRUE
WHERE e.id = 786;