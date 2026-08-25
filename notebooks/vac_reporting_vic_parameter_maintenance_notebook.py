from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Fabric notebook parameters
OUTPUT_DATABASE = "vacancy_reporting"
CONFIG_TABLE = "cfg_vacancy_rule_parameters"

# Safe default: inspect only.
# Set to True only when you want to write changes.
EXECUTE_CHANGES = True

# Allowed values:
# - "view_active"
# - "apply_rule_updates"
ACTION = "apply_rule_updates"

# The updates you want to apply.
# Each entry becomes the new active row for that rule_name.
RULE_UPDATES = [
    {
        "rule_name": "property_source_date_offset",
        "offset_days": 0,
        "effective_from": "2020-04-08",
        "comment": "UTC timestamps are converted to Australia/Melbourne in Silver; no additional source-date shift is required.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "tenancy_source_date_offset",
        "offset_days": 0,
        "effective_from": "2020-04-08",
        "comment": "UTC timestamps are converted to Australia/Melbourne in Silver; no additional source-date shift is required.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "void_source_date_offset",
        "offset_days": 0,
        "effective_from": "2020-04-08",
        "comment": "UTC timestamps are converted to Australia/Melbourne in Silver; no additional source-date shift is required.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "keys_source_date_offset",
        "offset_days": 0,
        "effective_from": "2020-04-08",
        "comment": "UTC timestamps are converted to Australia/Melbourne in Silver; no additional source-date shift is required.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "tenancy_end_to_vacancy_start",
        "offset_days": 1,
        "effective_from": "2020-04-08",
        "comment": "Vacancy starts on the day after the corrected tenancy end date.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "next_tenancy_start_to_vacancy_end",
        "offset_days": -1,
        "effective_from": "2020-04-08",
        "comment": "Workbook boundary rule for inclusive vacancy end.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "property_start_to_vacancy_start",
        "offset_days": 0,
        "effective_from": "2020-04-08",
        "comment": "New-property vacancy starts on the corrected property start date.",
        "updated_by": "fabric_admin",
    },
    {
        "rule_name": "property_end_to_vacancy_end",
        "offset_days": 1,
        "effective_from": "2020-04-08",
        "comment": "Vacancy inclusive end boundary stops on the property end date (+1 day offset for exclusive computing).",
        "updated_by": "fabric_admin",
    },
]

config_table_fqn = f"{OUTPUT_DATABASE}.{CONFIG_TABLE}"

if not spark.catalog.tableExists(config_table_fqn):
    raise ValueError(
        f"Config table {config_table_fqn} does not exist. Run the conformed vacancy modular pipeline first."
    )

def load_config():
    return (
        spark.table(config_table_fqn)
        .withColumn("effective_from", F.to_date("effective_from"))
        .withColumn("updated_at", F.to_timestamp("updated_at"))
        .withColumn("is_active", F.col("is_active").cast("boolean"))
    )

def latest_active_rules(df):
    window = Window.partitionBy("rule_name").orderBy(
        F.col("effective_from").desc_nulls_last(),
        F.col("updated_at").desc_nulls_last(),
    )
    return (
        df.filter(F.coalesce(F.col("is_active"), F.lit(True)))
        .withColumn("rule_rank", F.row_number().over(window))
        .filter(F.col("rule_rank") == 1)
        .drop("rule_rank")
        .orderBy("rule_name")
    )

config_df = load_config()

print("Current active rule parameters")
display(latest_active_rules(config_df))

if ACTION == "view_active":
    pass
elif ACTION == "apply_rule_updates":
    if not EXECUTE_CHANGES:
        raise ValueError(
            "EXECUTE_CHANGES is False. Review the updates first, then set EXECUTE_CHANGES = True to write."
        )

    if not RULE_UPDATES:
        raise ValueError("RULE_UPDATES is empty.")

    updates_df = (
        spark.createDataFrame(RULE_UPDATES)
        .withColumn("effective_from", F.to_date("effective_from"))
        .withColumn("updated_at", F.current_timestamp())
        .withColumn("is_active", F.lit(True))
        .select(
            "rule_name",
            "offset_days",
            "is_active",
            "effective_from",
            "comment",
            "updated_by",
            "updated_at",
        )
    )

    updated_rule_names = [row["rule_name"] for row in updates_df.select("rule_name").collect()]

    remaining_df = config_df.filter(~F.col("rule_name").isin(updated_rule_names))
    deactivated_existing_df = (
        config_df.filter(F.col("rule_name").isin(updated_rule_names))
        .withColumn("is_active", F.lit(False))
    )

    new_config_df = remaining_df.unionByName(deactivated_existing_df).unionByName(updates_df)

    (
        new_config_df.write.mode("overwrite")
        .format("delta")
        .option("overwriteSchema", "true")
        .saveAsTable(config_table_fqn)
    )

    print("Updated active rule parameters successfully.")
    display(latest_active_rules(load_config()))
else:
    raise ValueError(f"Unsupported ACTION: {ACTION}")
