-- assets/notebooks/transform_data.sql
CREATE OR REPLACE TABLE default.daily_sales AS
SELECT
  current_date() AS run_date,
  SUM(amount) AS total_sales
FROM default.sales
WHERE date = current_date();
