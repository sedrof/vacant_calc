from pyspark.sql import functions as F

# Fabric notebook parameters. Replace these values for your environment.
WAREHOUSE_PREFIX = "`Evolve-TechOne`.Shortcut.ev"
OUTPUT_DATABASE = "vacancy_reporting"

def ingest_bronze_table(table_name: str):
    """
    Ingests source data 1:1 exactly as it comes from the source database.
    No timezone shifts, no type conversions, and no field filtering to preserve raw history.
    """
    df = spark.table(f"{WAREHOUSE_PREFIX}.{table_name}")
    
    bronze_table_fqn = f"{OUTPUT_DATABASE}.Bronze_TechOne_{table_name}"
    (
        df.write.mode("overwrite")
        .format("delta")
        .option("overwriteSchema", "true")
        .saveAsTable(bronze_table_fqn)
    )
    print(f"Successfully ingested 1:1 raw table: {bronze_table_fqn}")

# Ensure target database exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {OUTPUT_DATABASE}")

# Ingest all in-scope source tables
ingest_bronze_table("Property")
ingest_bronze_table("Tenancy")
ingest_bronze_table("Void")
ingest_bronze_table("Keys")
