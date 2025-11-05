# Databricks notebook source
# MAGIC %md
# MAGIC # Create Table Using Python/Spark
# MAGIC This notebook creates a table using Python/Spark DataFrames

# COMMAND ----------

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Spark DataFrames").getOrCreate()

# Create sample data
data = ([1, "alen", 10000], [2, "bob", 20000], [3, "charlie", 30000])
df = spark.createDataFrame(data, ["id", "name", "salary"])

# Display the DataFrame
df.display()

# Create or replace table
df.write.mode("overwrite").saveAsTable("default.employees")

print("Table 'default.employee_salary' created successfully!")

# COMMAND ----------

# Verify table was created


