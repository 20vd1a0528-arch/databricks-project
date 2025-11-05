-- assets/notebooks/transform_data.sql
CREATE OR REPLACE TABLE default.date_table AS
SELECT current_date() AS currunt_date;
