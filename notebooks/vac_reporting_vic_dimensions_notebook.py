from pyspark.sql import functions as F

# Fabric notebook parameters
OUTPUT_DATABASE = "vacancy_reporting"
TARGET_STATE = "VIC"

# Load conformed Silver property data
silver_properties = spark.table(f"{OUTPUT_DATABASE}.silver_techone_property")

# Conformed Gold Dimension: dim_property_vic
dim_property_vic = (
    silver_properties.withColumnRenamed("property_program", "property_source")
    .withColumnRenamed("property_program_code", "property_source_code")
    .withColumn("property_program", F.col("property_source"))
    .withColumn("property_program_code", F.col("property_source_code"))
    .withColumn("report_state", F.lit(TARGET_STATE))
    .select(
        "property_id",
        "property_number",
        "property_short_address",
        "is_standard_address",
        "suburb",
        "state",
        "postcode",
        "entity_code",
        "entity",
        "ownership_code",
        "ownership",
        "housing_program_code",
        "housing_program",
        "property_type_code",
        "property_type",
        "property_program_code",
        "property_program",
        "property_source_code",
        "property_source",
        "property_start_date",
        "property_end_date",
        "inactive_date",
        "current_stage",
        "current_stage_code",
        "active_code",
        "report_state",
    )
)

# Write conformed Gold dimension to database
(
    dim_property_vic.write.mode("overwrite")
    .format("delta")
    .option("overwriteSchema", "true")
    .saveAsTable(f"{OUTPUT_DATABASE}.dim_property_vic")
)
print("Gold conformed dimension dim_property_vic written successfully.")

# Replicate dim_date conformed calendar into the local report-specific database
print("Replicating shared calendar dim_date into local conformed schema...")
dim_date_raw = spark.table("`Evolve-TechOne`.Shortcut.dbo.dim_date")

(
    dim_date_raw.write.mode("overwrite")
    .format("delta")
    .option("overwriteSchema", "true")
    .saveAsTable(f"{OUTPUT_DATABASE}.dim_date")
)
print("Gold conformed dimension dim_date written successfully.")
