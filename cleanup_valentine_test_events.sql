-- Cleanup Script: Remove Valentine Magic Test Events
-- This script removes all Valentine Magic events with IDs 2001-2077
-- that were inserted for testing purposes.

-- Check how many events will be deleted before running the DELETE
SELECT 
    COUNT(*) as total_events_to_delete,
    MIN(id) as min_id,
    MAX(id) as max_id,
    MIN(start) as earliest_date,
    MAX(start) as latest_date
FROM event 
WHERE id >= 2001 AND id <= 2077;

-- Delete the test events
DELETE FROM event 
WHERE id >= 2001 AND id <= 2077;

-- Verify deletion
SELECT 
    COUNT(*) as remaining_events_in_range
FROM event 
WHERE id >= 2001 AND id <= 2077;

-- Reset the sequence if needed (optional - only if you want to reuse these IDs)
-- SELECT setval('event_id_seq', (SELECT COALESCE(MAX(id), 0) FROM event));