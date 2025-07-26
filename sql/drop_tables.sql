-- drop_tables.sql
-- WARNING: This script will PERMANENTLY DELETE ALL DATABASE TABLES and their data
--          for the specified application components. Use with extreme caution!
-- Purpose:
-- This script is primarily used in development and testing environments to
-- completely remove the existing database schema for the application.
-- It is typically run before re-creating the tables (e.g., using `create_tables.sql`)
-- to ensure a clean slate.
-- Operation:
-- DROP TABLE IF EXISTS: Attempts to remove the specified tables from the database.
--   - IF EXISTS: Prevents an error if the table does not already exist, making the script idempotent.
--   - ORDER_ITEMS, ORDERS, INVENTORY, ITEMS, SUPPLIERS, CUSTOMERS: These are the tables
--     that will be dropped.
-- CASCADE: This is crucial. It automatically drops all objects that depend on the tables
--   being dropped. For example, when 'ORDERS' is dropped, any foreign key constraints
--   in 'ORDER_ITEMS' that refer to 'ORDERS' will also be dropped automatically,
--   and then 'ORDER_ITEMS' itself (if it were not explicitly listed or if there were
--   other dependent objects like views or functions). In this specific case,
--   it ensures a clean removal of all related components.
-- Usage:
-- - DO NOT run this script in any production or sensitive environment.
-- - Ideal for a full database schema rebuild during development or for
--   resetting a testing environment to a pristine state.
-- - Often executed as the first step when initializing or refreshing a
--   development database alongside a `create_tables.sql` script.
DROP TABLE IF EXISTS ORDER_ITEMS,
ORDERS,
INVENTORY,
ITEMS,
SUPPLIERS,
CUSTOMERS CASCADE;