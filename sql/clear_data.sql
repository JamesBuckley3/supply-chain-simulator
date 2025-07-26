-- clear_data.sql
-- WARNING: This script will PERMANENTLY DELETE ALL DATA from the specified tables.
--          Use with extreme caution!
-- Purpose:
-- This script is intended for development and testing environments only.
-- It facilitates a complete reset of the database by clearing all records
-- from the core application tables.
-- Operation:
-- TRUNCATE TABLE: Quickly removes all rows from the specified tables.
--   - ORDER_ITEMS, ORDERS, INVENTORY, ITEMS, SUPPLIERS, CUSTOMERS: These are the tables
--     from which all data will be removed.
-- RESTART IDENTITY: Resets the sequence generators for SERIAL columns (like PRIMARY KEY IDs)
--   back to their starting value (usually 1). This ensures that new data inserted after
--   truncation will start with fresh IDs.
-- CASCADE: This is crucial. It automatically truncates all tables that have
--   foreign key references to the tables being truncated. For example, if you truncate
--   'ORDERS', 'CASCADE' will also truncate 'ORDER_ITEMS' because 'ORDER_ITEMS'
--   references 'ORDERS'. This helps maintain referential integrity during a full reset.
-- Usage:
-- - DO NOT run this script in any production or sensitive environment.
-- - Ideal for setting up a clean slate for new feature development,
--   running automated tests, or debugging on a local machine.
TRUNCATE TABLE ORDER_ITEMS,
ORDERS,
INVENTORY,
ITEMS,
SUPPLIERS,
CUSTOMERS RESTART IDENTITY CASCADE;

-- Confirmation Message (optional, depends on SQL client/environment):
-- SELECT 'All data cleared successfully and identities reset.' AS status;