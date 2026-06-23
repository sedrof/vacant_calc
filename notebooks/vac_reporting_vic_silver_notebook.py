from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Fabric notebook parameters
OUTPUT_DATABASE = "vacancy_reporting"
TARGET_STATE = "VIC"
CONFIG_TABLE = "cfg_vacancy_rule_parameters"
ACTIVE_CONFIG_TABLE = "dim_active_vacancy_rule_parameters"
BRACKET_MARKER_PATTERN = r"[\[\]\(\)<>]"
LOCAL_TIMEZONE = "Australia/Melbourne"

def qcol(name: str):
    return F.col(f"`{name}`")

def ensure_columns(df: DataFrame, expected_cols: list[str]) -> DataFrame:
    """
    Asserts column completeness to prevent schema drift from crashing downstream processes.
    Appends expected columns as Null if they do not exist in the source raw table.
    """
    result = df
    for col_name in expected_cols:
        if col_name not in result.columns:
            result = result.withColumn(col_name, F.lit(None).cast("string"))
    return result

def load_bronze_table(table_name: str, column_map: list[tuple[str, str]]):
    """
    Loads raw 1:1 Bronze data, asserts column completeness, and aliases to conformed names.
    """
    df = spark.table(f"{OUTPUT_DATABASE}.Bronze_TechOne_{table_name}")
    source_cols = [source for source, _ in column_map]
    df = ensure_columns(df, source_cols)
    return df.select(*[qcol(source).alias(alias) for source, alias in column_map])

def with_date(df, columns: list[str]):
    for column_name in columns:
        # Timezone Integrity Constraint: Cast date to local timezone Melbourne after assuring UTC timestamp safety
        df = df.withColumn(
            column_name,
            F.to_date(F.from_utc_timestamp(F.to_timestamp(F.col(column_name)), LOCAL_TIMEZONE))
        )
    return df

def with_raw_column_copies(df, columns: list[str]):
    for column_name in columns:
        df = df.withColumn(f"raw_{column_name}", F.col(column_name))
    return df

def shift_date_columns(df, columns: list[str], offset_days: int):
    if offset_days == 0:
        return df
    for column_name in columns:
        df = df.withColumn(
            column_name,
            F.when(F.col(column_name).isNotNull(), F.date_add(F.col(column_name), offset_days)),
        )
    return df

def parsed_text_date(column_name: str):
    cleaned = F.trim(F.col(column_name))
    return F.coalesce(
        F.to_date(cleaned),
        F.to_date(cleaned, "yyyy-MM-dd"),
        F.to_date(cleaned, "dd/MM/yyyy"),
        F.to_date(cleaned, "d/M/yyyy"),
        F.to_date(cleaned, "dd-MM-yyyy"),
        F.to_date(cleaned, "d-M-yyyy"),
    )

def write_silver_delta(df, table_name: str):
    (
        df.write.mode("overwrite")
        .format("delta")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{OUTPUT_DATABASE}.{table_name}")
    )
    print(f"Silver table {table_name} written successfully.")

# Ensure target database exists
spark.sql(f"CREATE DATABASE IF NOT EXISTS {OUTPUT_DATABASE}")

# Step 1: Graceful Degradation of Lookup Parameters
# Read raw rule parameters and degrade to standard defaults if configuration is missing.
rule_parameter_map = {
    "property_source_date_offset": 0,
    "tenancy_source_date_offset": 0,
    "void_source_date_offset": 0,
    "keys_source_date_offset": 0,
}

try:
    active_rule_parameters = (
        spark.table(f"{OUTPUT_DATABASE}.{ACTIVE_CONFIG_TABLE}")
    )
    rule_parameter_map = {
        row["rule_name"]: int(row["offset_days"])
        for row in active_rule_parameters.select("rule_name", "offset_days").collect()
    }
    print("Successfully loaded active rule parameters from Fabric config.")
except Exception:
    print("Warning: Active rules table missing or empty. Degrading gracefully to default offsets (0).")

PROPERTY_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("property_source_date_offset", 0)
TENANCY_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("tenancy_source_date_offset", 0)
VOID_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("void_source_date_offset", 0)
KEYS_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("keys_source_date_offset", 0)

# Column mapping templates
property_columns = [
    ("DataSet.PROPERTYID", "property_id"),
    ("DataSet.PROPERTYNUMBER", "property_number"),
    ("DataSet.PROPERTYSHORTADDRESS", "property_short_address"),
    ("DataSet.SUBURB", "suburb"),
    ("DataSet.STATE", "state"),
    ("DataSet.POSTCODE", "postcode"),
    ("DataSet.ENTITY", "entity_code"),
    ("DataSet.ENTITYD", "entity"),
    ("DataSet.OWNERSHIP", "ownership_code"),
    ("DataSet.OWNERSHIPD", "ownership"),
    ("DataSet.HOUSINGPROGRAM", "housing_program_code"),
    ("DataSet.HOUSINGPROGRAMD", "housing_program"),
    ("DataSet.PROPERTYTYPE", "property_type_code"),
    ("DataSet.PROPERTYTYPED", "property_type"),
    ("DataSet.PROPERTYPROGRAM", "property_program_code"),
    ("DataSet.PROPERTYPROGRAMD", "property_program"),
    ("DataSet.PROPERTYSTARTDATE", "property_start_date"),
    ("DataSet.STARTDATE", "record_start_date"),
    ("DataSet.TERMINATIONDATE", "property_end_date"),
    ("DataSet.INACTIVEDATE", "inactive_date"),
    ("DataSet.CURRENTSTAGE", "current_stage"),
    ("DataSet.CURRENTSTAGECODE", "current_stage_code"),
    ("DataSet.ACTIVECODE", "active_code"),
]

tenancy_columns = [
    ("DataSet.TENANCYID", "tenancy_id"),
    ("DataSet.TENANCYREFERENCE", "tenancy_reference"),
    ("DataSet.PROPID", "property_id"),
    ("DataSet.TENANCYSTARTDATE", "tenancy_start_date"),
    ("DataSet.TENANCYENDDATE", "tenancy_end_date"),
    ("DataSet.ENDOFTENANCYREASON", "tenancy_end_reason_code"),
    ("DataSet.ENDOFTENANCYREASONDES", "tenancy_end_reason"),
    ("DataSet.CURRENTSTAGE", "current_stage"),
    ("DataSet.CURRENTSTAGECODE", "current_stage_code"),
    ("DataSet.ACTIVECODE", "active_code"),
    ("DataSet.INACTIVEDATE", "inactive_date"),
]

void_columns = [
    ("DataSet.VOID_ID", "void_id"),
    ("DataSet.PROP_ID", "property_id"),
    ("DataSet.VOID_REFERENCE", "void_reference"),
    ("DataSet.VOID_FROM_DATE", "void_start_date"),
    ("DataSet.VOID_TO_DATE", "void_end_date"),
    ("DataSet.VOID_REASON", "void_reason_code"),
    ("DataSet.VOID_REASON_D", "void_reason"),
    ("DataSet.PROPERTY_CONDITION", "property_condition_code"),
    ("DataSet.PROPERTY_CONDITION_D", "property_condition"),
    ("DataSet.KEY_REGISTER_ENG_ID", "key_register_engagement_id"),
    ("DataSet.OTHER_VACANCY_TYPE_REASON", "other_vacancy_type_reason"),
    ("DataSet.OTHER_VACANCY_FROM_DATE", "other_start_date"),
    ("DataSet.OTHER_VACANCY_TO_DATE", "other_end_date"),
    ("DataSet.OTHER_VAC_FROM_DATE_TXT", "other_start_date_text"),
    ("DataSet.OTHER_VAC_TO_DATE_TXT", "other_end_date_text"),
    ("DataSet.VOID_TYPE", "void_type"),
]

keys_columns = [
    ("DataSet.KEY_ID", "key_id"),
    ("DataSet.PARENT_ENGAGEMENT_ID", "parent_engagement_id"),
    ("DataSet.KEY_REFERENCE", "key_reference"),
    ("DataSet.DATE_RECEIVED_FROM_TENANT", "date_received_from_tenant"),
    ("DataSet.OUTGOING_INSPECTION_DATE", "outgoing_inspection_date"),
    ("DataSet.CONTRACTOR_NOTIFIED_DATE", "contractor_notified_date"),
    ("DataSet.TO_LOCKBOX_ONSITE", "to_lockbox_onsite"),
    ("DataSet.CONTRACTOR_COLLECT_K_DATE", "contractor_collect_key_date"),
    ("DataSet.CONTRACTOR_NAME_COMMENTS", "contractor_name_comments"),
    ("DataSet.CONTRACTOR_RETURN_K_DATE", "contractor_return_key_date"),
    ("DataSet.NEW_ACTIVATED_PROPERTY", "new_activated_property"),
    ("DataSet.VACANCY_EXEMPTIONS_C", "vacancy_exemptions_code"),
    ("DataSet.VACANCY_EXEMPTIONS_DESC", "vacancy_exemptions_desc"),
    ("DataSet.PROPERTY_CONDITION", "property_condition_code"),
    ("DataSet.PROPERTY_CONDITION_D", "property_condition"),
]

# Step 2: Build silver_techone_property
silver_properties = (
    load_bronze_table("Property", property_columns)
    .transform(
        lambda df: with_date(
            df,
            [
                "property_start_date",
                "record_start_date",
                "property_end_date",
                "inactive_date",
            ],
        )
    )
    .transform(
        lambda df: with_raw_column_copies(
            df,
            [
                "property_start_date",
                "record_start_date",
                "property_end_date",
                "inactive_date",
            ],
        )
    )
    .transform(
        lambda df: shift_date_columns(
            df,
            [
                "property_start_date",
                "record_start_date",
                "property_end_date",
                "inactive_date",
            ],
            PROPERTY_SOURCE_DATE_OFFSET_DAYS,
        )
    )
    .withColumn(
        "property_start_date",
        F.coalesce(F.col("property_start_date"), F.col("record_start_date")),
    )
    .withColumn(
        "raw_effective_property_start_date",
        F.coalesce(F.col("raw_property_start_date"), F.col("raw_record_start_date")),
    )
    .withColumn("property_id", F.col("property_id").cast("string"))
    .withColumn(
        "is_standard_address",
        F.when(
            F.col("property_short_address").isNotNull(),
            ~F.col("property_short_address").rlike(BRACKET_MARKER_PATTERN),
        ).otherwise(F.lit(False)),
    )
    .filter(F.upper(F.col("state")) == TARGET_STATE)
    .dropDuplicates(["property_id"])
)
write_silver_delta(silver_properties, "silver_techone_property")

# Step 3: Build silver_techone_tenancy
silver_tenancies = (
    load_bronze_table("Tenancy", tenancy_columns)
    .transform(
        lambda df: with_date(
            df,
            [
                "tenancy_start_date",
                "tenancy_end_date",
                "inactive_date",
            ],
        )
    )
    .transform(
        lambda df: with_raw_column_copies(
            df,
            [
                "tenancy_start_date",
                "tenancy_end_date",
                "inactive_date",
            ],
        )
    )
    .transform(
        lambda df: shift_date_columns(
            df,
            [
                "tenancy_start_date",
                "tenancy_end_date",
                "inactive_date",
            ],
            TENANCY_SOURCE_DATE_OFFSET_DAYS,
        )
    )
    .withColumn("tenancy_id", F.col("tenancy_id").cast("string"))
    .withColumn("property_id", F.col("property_id").cast("string"))
    .filter(F.col("property_id").isNotNull())
    
    # Exclude Allocation Cancelled Tenancy rows from calculations
    .withColumn(
        "is_excluded_from_vacancy_logic",
        F.when(
            (F.upper(F.trim(F.coalesce(F.col("current_stage"), F.lit("")))) == F.lit("ALLOCATION CANCELLED"))
            | (F.upper(F.trim(F.coalesce(F.col("current_stage_code"), F.lit("")))) == F.lit("AL_CAN")),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )
)
write_silver_delta(silver_tenancies, "silver_techone_tenancy")

# Step 4: Build silver_techone_void
# Temporary calculation variables for exclusive boundaries in silver
as_at_date_val = None
snapshot_end_exclusive = F.date_add(F.current_date(), 1)

silver_voids = (
    load_bronze_table("Void", void_columns)
    .transform(
        lambda df: with_date(
            df,
            [
                "void_start_date",
                "void_end_date",
                "other_start_date",
                "other_end_date",
            ],
        )
    )
    .transform(
        lambda df: with_raw_column_copies(
            df,
            [
                "void_start_date",
                "void_end_date",
                "other_start_date",
                "other_end_date",
            ],
        )
    )
    .transform(
        lambda df: shift_date_columns(
            df,
            [
                "void_start_date",
                "void_end_date",
            ],
            VOID_SOURCE_DATE_OFFSET_DAYS,
        )
    )
    .withColumn("parsed_other_start_date_text", parsed_text_date("other_start_date_text"))
    .withColumn("parsed_other_end_date_text", parsed_text_date("other_end_date_text"))
    .withColumn(
        "adjusted_other_start_date_from_field",
        F.when(
            F.col("other_start_date").isNotNull(),
            F.date_add(F.col("other_start_date"), VOID_SOURCE_DATE_OFFSET_DAYS),
        ),
    )
    .withColumn(
        "adjusted_other_end_date_from_field",
        F.when(
            F.col("other_end_date").isNotNull(),
            F.date_add(F.col("other_end_date"), VOID_SOURCE_DATE_OFFSET_DAYS),
        ),
    )
    .withColumn(
        "other_start_date_source",
        F.when(F.col("parsed_other_start_date_text").isNotNull(), F.lit("OTHER_VAC_FROM_DATE_TXT"))
        .when(F.col("adjusted_other_start_date_from_field").isNotNull(), F.lit("OTHER_VACANCY_FROM_DATE")),
    )
    .withColumn(
        "other_end_date_source",
        F.when(F.col("parsed_other_end_date_text").isNotNull(), F.lit("OTHER_VAC_TO_DATE_TXT"))
        .when(F.col("adjusted_other_end_date_from_field").isNotNull(), F.lit("OTHER_VACANCY_TO_DATE")),
    )
    .withColumn(
        "other_start_date",
        F.coalesce(F.col("parsed_other_start_date_text"), F.col("adjusted_other_start_date_from_field")),
    )
    .withColumn(
        "other_end_date",
        F.coalesce(F.col("parsed_other_end_date_text"), F.col("adjusted_other_end_date_from_field")),
    )
    .withColumn("void_id", F.col("void_id").cast("string"))
    .withColumn("property_id", F.col("property_id").cast("string"))
    .withColumn(
        "key_register_engagement_id",
        F.col("key_register_engagement_id").cast("string"),
    )
    .filter(F.col("property_id").isNotNull())
    .withColumn(
        "void_end_exclusive",
        F.coalesce(F.date_add(F.col("void_end_date"), 1), snapshot_end_exclusive),
    )
    .withColumn(
        "other_end_exclusive",
        F.when(F.col("other_end_date").isNotNull(), F.date_add(F.col("other_end_date"), 1)),
    )
    .withColumn(
        "has_other_vacancy_range",
        F.col("other_start_date").isNotNull() & F.col("other_end_exclusive").isNotNull(),
    )
    .withColumn(
        "other_vacancy_outside_void_flag",
        F.when(
            F.col("has_other_vacancy_range")
            & (
                (F.col("other_start_date") < F.col("void_start_date"))
                | (F.col("other_end_exclusive") > F.col("void_end_exclusive"))
            ),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )
    .withColumn(
        "other_effective_start_date",
        F.when(
            F.col("has_other_vacancy_range"),
            F.greatest(F.col("other_start_date"), F.col("void_start_date")),
        ),
    )
    .withColumn(
        "other_effective_end_exclusive",
        F.when(
            F.col("has_other_vacancy_range"),
            F.least(F.col("other_end_exclusive"), F.col("void_end_exclusive")),
        ),
    )
    .withColumn("other_effective_end_date", F.date_sub(F.col("other_effective_end_exclusive"), 1))
)
write_silver_delta(silver_voids, "silver_techone_void")

# Step 5: Build silver_techone_keys
silver_keys = (
    load_bronze_table("Keys", keys_columns)
    .transform(
        lambda df: with_date(
            df,
            [
                "date_received_from_tenant",
                "outgoing_inspection_date",
                "contractor_notified_date",
                "contractor_collect_key_date",
                "contractor_return_key_date",
            ],
        )
    )
    .transform(
        lambda df: with_raw_column_copies(
            df,
            [
                "date_received_from_tenant",
                "outgoing_inspection_date",
                "contractor_notified_date",
                "contractor_collect_key_date",
                "contractor_return_key_date",
            ],
        )
    )
    .transform(
        lambda df: shift_date_columns(
            df,
            [
                "date_received_from_tenant",
                "outgoing_inspection_date",
                "contractor_notified_date",
                "contractor_collect_key_date",
                "contractor_return_key_date",
            ],
            KEYS_SOURCE_DATE_OFFSET_DAYS,
        )
    )
    .withColumn("key_id", F.col("key_id").cast("string"))
    .withColumn("parent_engagement_id", F.col("parent_engagement_id").cast("string"))
    .withColumn("property_id", F.col("parent_engagement_id"))
    .withColumn(
        "raw_key_anchor_date",
        F.coalesce(
            F.col("raw_date_received_from_tenant"),
            F.col("raw_outgoing_inspection_date"),
            F.col("raw_contractor_notified_date"),
            F.col("raw_contractor_collect_key_date"),
            F.col("raw_contractor_return_key_date"),
        ),
    )
    .withColumn(
        "key_anchor_date",
        F.coalesce(
            F.col("date_received_from_tenant"),
            F.col("outgoing_inspection_date"),
            F.col("contractor_notified_date"),
            F.col("contractor_collect_key_date"),
            F.col("contractor_return_key_date"),
        ),
    )
    .filter(F.col("property_id").isNotNull())
)
write_silver_delta(silver_keys, "silver_techone_keys")
