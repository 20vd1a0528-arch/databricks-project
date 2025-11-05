-- assets/notebooks/transform_data.sql
CREATE OR REPLACE TABLE default.daily_sales AS
SELECT current_date() AS run_date;
