-- Create employees table using SQL
CREATE OR REPLACE TABLE default.employees AS
SELECT 1 AS id, 'alen' AS name, 10000 AS salary
UNION ALL
SELECT 2 AS id, 'bob' AS name, 20000 AS salary
UNION ALL
SELECT 3 AS id, 'charlie' AS name, 30000 AS salary
UNION ALL
SELECT 4 AS id, 'ell' AS name, 50000 AS salary;

