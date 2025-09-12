-- This resets the database to a clean state,
-- recreates it, and reseeds it.
-- To run, 
-- ```psql -U postgres -d library_db```
-- then 
-- ```\i reset_db.sql``` from library_db

-- Avoid conflicts by dropping in the correct order
DROP TABLE IF EXISTS Loans CASCADE;
DROP TABLE IF EXISTS Books CASCADE;
DROP TABLE IF EXISTS Authors CASCADE;
DROP TABLE IF EXISTS Members CASCADE;
DROP TABLE IF EXISTS Staff CASCADE;

\echo 'All tables dropped successfully'

-- Recreate schema
\i schema/01_create_tables.sql
\echo 'Schema recreated'

-- Reseed data
\i seed/02_insert_seed_data.sql
\echo 'Seed data inserted'

-- Run operations
\echo 'Database reset, you can now run operational scripts'