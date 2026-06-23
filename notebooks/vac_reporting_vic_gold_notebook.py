from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Fabric notebook parameters. Replace these values for your environment.
OUTPUT_DATABASE = "vacancy_reporting"
TARGET_STATE = "VIC"
AS_AT_DATE = None  # Example: "2026-03-31". Leave as None to use today's date.
ACTIVE_CONFIG_TABLE = "dim_active_vacancy_rule_parameters"
EMPTY_DATE_ARRAY = F.expr("cast(array() as array<date>)")

def write_delta(df, table_name: str):
    (
        df.write.mode("overwrite")
        .format("delta")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{OUTPUT_DATABASE}.{table_name}")
    )
    print(f"Gold table {table_name} written successfully to lakehouse.")

# Step 1: Graceful Degradation of Parameter Lookup
# Load active parameters and fall back to standard defaults if Lookup table is missing.
rule_parameter_map = {
    "tenancy_end_to_vacancy_start": 1,
    "next_tenancy_start_to_vacancy_end": -1,
    "property_end_to_vacancy_end": 1,
    "property_start_to_vacancy_start": 0,
    "property_source_date_offset": 0,
    "tenancy_source_date_offset": 0,
    "void_source_date_offset": 0,
    "keys_source_date_offset": 0,
}

try:
    active_rule_parameters = spark.table(f"{OUTPUT_DATABASE}.{ACTIVE_CONFIG_TABLE}")
    rule_parameter_map.update({
        row["rule_name"]: int(row["offset_days"])
        for row in active_rule_parameters.select("rule_name", "offset_days").collect()
    })
    print("Successfully loaded active rule parameters for Gold logic.")
except Exception:
    print("Warning: Active rules table missing or empty. Gold pipeline falling back to default logic parameters.")

TENANCY_END_TO_VACANCY_START_OFFSET_DAYS = rule_parameter_map.get("tenancy_end_to_vacancy_start", 1)
NEXT_TENANCY_START_TO_VACANCY_END_OFFSET_DAYS = rule_parameter_map.get("next_tenancy_start_to_vacancy_end", -1)
PROPERTY_END_TO_VACANCY_END_OFFSET_DAYS = rule_parameter_map.get("property_end_to_vacancy_end", 1)
PROPERTY_START_TO_VACANCY_START_OFFSET_DAYS = rule_parameter_map.get("property_start_to_vacancy_start", 0)
PROPERTY_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("property_source_date_offset", 0)
TENANCY_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("tenancy_source_date_offset", 0)
VOID_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("void_source_date_offset", 0)
KEYS_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get("keys_source_date_offset", 0)

snapshot_end_exclusive = (
    F.date_add(F.current_date(), 1)
    if AS_AT_DATE is None
    else F.date_add(F.to_date(F.lit(AS_AT_DATE)), 1)
)

# Step 2: Load Silver conformed data and dimensions
dim_property_vic = spark.table(f"{OUTPUT_DATABASE}.dim_property_vic")
silver_properties = spark.table(f"{OUTPUT_DATABASE}.silver_techone_property")
silver_tenancies = spark.table(f"{OUTPUT_DATABASE}.silver_techone_tenancy")
silver_voids = spark.table(f"{OUTPUT_DATABASE}.silver_techone_void")
silver_keys = spark.table(f"{OUTPUT_DATABASE}.silver_techone_keys")

# Filter tenancies used for vacancy logic
tenancies_for_vacancy_logic = silver_tenancies.filter(F.col("is_excluded_from_vacancy_logic") == 0)

# Step 3: Compute vacancy intervals
tenancy_sequence_window = Window.partitionBy("property_id").orderBy(
    F.col("tenancy_start_date").asc_nulls_last(),
    F.col("tenancy_id"),
)

tenancy_rank_window = Window.partitionBy("property_id").orderBy(
    F.col("tenancy_start_date").asc_nulls_last(),
    F.col("tenancy_id"),
)

tenancies_ordered = (
    tenancies_for_vacancy_logic.withColumn(
        "next_tenancy_start_date",
        F.lead("tenancy_start_date").over(tenancy_sequence_window),
    )
    .withColumn(
        "next_tenancy_end_date",
        F.lead("tenancy_end_date").over(tenancy_sequence_window),
    )
    .withColumn(
        "next_tenancy_id",
        F.lead("tenancy_id").over(tenancy_sequence_window),
    )
    .withColumn(
        "next_tenancy_current_stage",
        F.lead("current_stage").over(tenancy_sequence_window),
    )
    .withColumn(
        "next_tenancy_current_stage_code",
        F.lead("current_stage_code").over(tenancy_sequence_window),
    )
    .withColumn("tenancy_rank", F.row_number().over(tenancy_rank_window))
)

first_tenancy = (
    tenancies_ordered.filter(F.col("tenancy_rank") == 1)
    .select(
        "property_id",
        F.col("tenancy_id").alias("first_tenancy_id"),
        F.col("tenancy_start_date").alias("first_tenancy_start_date"),
        F.col("tenancy_end_date").alias("first_tenancy_end_date"),
        F.col("current_stage").alias("first_tenancy_current_stage"),
        F.col("current_stage_code").alias("first_tenancy_current_stage_code"),
    )
)

ended_tenancy_vacancies = (
    tenancies_ordered.filter(F.col("tenancy_end_date").isNotNull())
    .join(silver_properties.select("property_id", "property_end_date").alias("p"), "property_id", "left")
    .select(
        "property_id",
        F.col("tenancy_id").alias("vacancy_start_tenancy_id"),
        F.col("tenancy_start_date").alias("vacancy_start_tenancy_start_date"),
        F.col("tenancy_end_date").alias("vacancy_start_tenancy_end_date"),
        F.col("current_stage").alias("vacancy_start_tenancy_current_stage"),
        F.col("current_stage_code").alias("vacancy_start_tenancy_current_stage_code"),
        F.col("next_tenancy_id").alias("vacancy_end_tenancy_id"),
        F.col("next_tenancy_start_date").alias("vacancy_end_tenancy_start_date"),
        F.col("next_tenancy_end_date").alias("vacancy_end_tenancy_end_date"),
        F.col("next_tenancy_current_stage").alias("vacancy_end_tenancy_current_stage"),
        F.col("next_tenancy_current_stage_code").alias("vacancy_end_tenancy_current_stage_code"),
        F.date_add(
            F.col("tenancy_end_date"),
            TENANCY_END_TO_VACANCY_START_OFFSET_DAYS,
        ).alias("vacancy_start_date"),
        F.when(
            F.col("next_tenancy_start_date").isNotNull(),
            F.date_add(
                F.col("next_tenancy_start_date"),
                NEXT_TENANCY_START_TO_VACANCY_END_OFFSET_DAYS + 1,
            ),
        )
        .otherwise(snapshot_end_exclusive)
        .alias("raw_vacancy_end_exclusive"),
        F.col("p.property_end_date"),
        F.col("tenancy_end_reason_code").alias("vacancy_reason_code"),
        F.col("tenancy_end_reason").alias("vacancy_reason"),
        F.lit("tenancy_end").alias("vacancy_origin"),
    )
    .withColumn(
        "vacancy_end_exclusive",
        F.when(
            F.col("property_end_date").isNotNull()
            & (F.date_add(F.col("property_end_date"), PROPERTY_END_TO_VACANCY_END_OFFSET_DAYS) < F.col("raw_vacancy_end_exclusive")),
            F.date_add(F.col("property_end_date"), PROPERTY_END_TO_VACANCY_END_OFFSET_DAYS)
        ).otherwise(F.col("raw_vacancy_end_exclusive"))
    )
    .drop("raw_vacancy_end_exclusive", "property_end_date")
    .filter(F.col("vacancy_start_date") < F.col("vacancy_end_exclusive"))
)

initial_property_vacancies = (
    silver_properties.alias("p")
    .join(first_tenancy.alias("t"), "property_id", "left")
    .select(
        F.col("property_id"),
        F.lit(None).cast("string").alias("vacancy_start_tenancy_id"),
        F.lit(None).cast("date").alias("vacancy_start_tenancy_start_date"),
        F.lit(None).cast("date").alias("vacancy_start_tenancy_end_date"),
        F.lit(None).cast("string").alias("vacancy_start_tenancy_current_stage"),
        F.lit(None).cast("string").alias("vacancy_start_tenancy_current_stage_code"),
        F.col("t.first_tenancy_id").alias("vacancy_end_tenancy_id"),
        F.col("t.first_tenancy_start_date").alias("vacancy_end_tenancy_start_date"),
        F.col("t.first_tenancy_end_date").alias("vacancy_end_tenancy_end_date"),
        F.col("t.first_tenancy_current_stage").alias("vacancy_end_tenancy_current_stage"),
        F.col("t.first_tenancy_current_stage_code").alias("vacancy_end_tenancy_current_stage_code"),
        F.date_add(
            F.col("p.property_start_date"),
            PROPERTY_START_TO_VACANCY_START_OFFSET_DAYS,
        ).alias("vacancy_start_date"),
        F.when(
            F.col("t.first_tenancy_start_date").isNotNull(),
            F.date_add(
                F.col("t.first_tenancy_start_date"),
                NEXT_TENANCY_START_TO_VACANCY_END_OFFSET_DAYS + 1,
            ),
        )
        .otherwise(snapshot_end_exclusive)
        .alias("raw_vacancy_end_exclusive"),
        F.col("p.property_end_date"),
        F.lit("NEW_PROPERTY").alias("vacancy_reason_code"),
        F.lit("Initial vacancy before first tenancy").alias("vacancy_reason"),
        F.lit("property_start").alias("vacancy_origin"),
    )
    .withColumn(
        "vacancy_end_exclusive",
        F.when(
            F.col("property_end_date").isNotNull()
            & (F.date_add(F.col("property_end_date"), PROPERTY_END_TO_VACANCY_END_OFFSET_DAYS) < F.col("raw_vacancy_end_exclusive")),
            F.date_add(F.col("property_end_date"), PROPERTY_END_TO_VACANCY_END_OFFSET_DAYS)
        ).otherwise(F.col("raw_vacancy_end_exclusive"))
    )
    .drop("raw_vacancy_end_exclusive", "property_end_date")
    .filter(F.col("vacancy_start_date").isNotNull())
    .filter(F.col("vacancy_start_date") < F.col("vacancy_end_exclusive"))
)

vacancy_intervals_base = ended_tenancy_vacancies.unionByName(initial_property_vacancies)

vacancy_intervals = (
    vacancy_intervals_base.join(dim_property_vic, "property_id", "inner")
    .withColumn(
        "vacancy_id",
        F.concat_ws(
            "_",
            F.col("property_id").cast("string"),
            F.date_format("vacancy_start_date", "dd/MM/yy"),
        ),
    )
    .withColumn(
        "full_vacancy_days",
        F.greatest(
            F.datediff(F.col("vacancy_end_exclusive"), F.col("vacancy_start_date")),
            F.lit(0),
        ),
    )
    .withColumn("vacancy_end_date", F.date_sub(F.col("vacancy_end_exclusive"), 1))
    .withColumn("is_open_vacancy", F.col("vacancy_end_tenancy_id").isNull())
    .withColumn(
        "vacancy_end_date_display",
        F.when(F.col("is_open_vacancy"), F.lit(None).cast("date")).otherwise(F.col("vacancy_end_date")),
    )
    .withColumn("report_state", F.lit(TARGET_STATE))
)

# Step 4: Build conformed Void intervals (Gold level)
void_intervals = silver_voids.join(dim_property_vic.select("property_id"), "property_id", "inner")

# Step 5: Build Audit Exceptions
tenancy_interval_exceptions = (
    tenancies_for_vacancy_logic.alias("t")
    .join(
        void_intervals.alias("d"),
        F.col("t.property_id") == F.col("d.property_id"),
        "inner",
    )
    .select(
        F.col("t.property_id").alias("property_id"),
        F.col("t.tenancy_id").alias("tenancy_id"),
        F.col("t.tenancy_reference").alias("tenancy_reference"),
        F.col("t.current_stage").alias("tenancy_current_stage"),
        F.col("t.current_stage_code").alias("tenancy_current_stage_code"),
        F.col("t.raw_tenancy_start_date").alias("raw_tenancy_start_date"),
        F.col("t.tenancy_start_date").alias("tenancy_start_date"),
        F.col("t.raw_tenancy_end_date").alias("raw_tenancy_end_date"),
        F.col("t.tenancy_end_date").alias("tenancy_end_date"),
        F.col("d.void_id").alias("void_id"),
        F.col("d.void_reference").alias("void_reference"),
        F.col("d.raw_void_start_date").alias("raw_void_start_date"),
        F.col("d.void_start_date").alias("void_start_date"),
        F.col("d.raw_void_end_date").alias("raw_void_end_date"),
        F.col("d.void_end_date").alias("void_end_date"),
        F.col("d.void_end_exclusive").alias("void_end_exclusive"),
    )
    .withColumn(
        "tenancy_end_exclusive",
        F.coalesce(F.date_add(F.col("tenancy_end_date"), 1), snapshot_end_exclusive),
    )
    .withColumn("overlap_start_date", F.greatest(F.col("tenancy_start_date"), F.col("void_start_date")))
    .withColumn("overlap_end_exclusive", F.least(F.col("tenancy_end_exclusive"), F.col("void_end_exclusive")))
    .filter(F.col("tenancy_start_date").isNotNull())
    .filter(F.col("void_start_date").isNotNull())
    .filter(F.col("overlap_start_date") < F.col("overlap_end_exclusive"))
    .join(
        silver_properties.select(
            "property_id",
            "property_number",
            "property_short_address",
            "entity",
            "ownership",
            "housing_program",
            "property_type",
            "property_program",
            "current_stage",
        ),
        "property_id",
        "left",
    )
    .withColumn(
        "exception_type",
        F.lit("TENANCY_OVERLAPS_VOID"),
    )
    .withColumn(
        "exception_severity",
        F.lit("Error"),
    )
    .withColumn(
        "overlap_end_date",
        F.date_sub(F.col("overlap_end_exclusive"), 1),
    )
    .withColumn(
        "overlap_days",
        F.datediff(F.col("overlap_end_exclusive"), F.col("overlap_start_date")),
    )
    .withColumn(
        "exception_summary",
        F.concat_ws(
            " ",
            F.lit("Tenancy"),
            F.col("tenancy_id"),
            F.lit("overlaps void"),
            F.col("void_id"),
            F.lit("for"),
            F.col("overlap_days").cast("string"),
            F.lit("day(s)."),
        ),
    )
    .withColumn(
        "exception_id",
        F.concat_ws(
            "-",
            F.lit("EXC"),
            F.col("property_id"),
            F.col("tenancy_id"),
            F.col("void_id"),
            F.date_format(F.col("overlap_start_date"), "yyyyMMdd"),
        ),
    )
    .select(
        "exception_id",
        "exception_type",
        "exception_severity",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_type",
        "property_program",
        "current_stage",
        "tenancy_id",
        "tenancy_reference",
        "tenancy_current_stage",
        "tenancy_current_stage_code",
        "raw_tenancy_start_date",
        "tenancy_start_date",
        "raw_tenancy_end_date",
        "tenancy_end_date",
        "void_id",
        "void_reference",
        "raw_void_start_date",
        "void_start_date",
        "raw_void_end_date",
        "void_end_date",
        "overlap_start_date",
        "overlap_end_date",
        "overlap_days",
        "exception_summary",
        F.lit(TARGET_STATE).alias("report_state"),
    )
)

other_vacancy_exceptions = (
    void_intervals.filter(F.col("other_vacancy_outside_void_flag") == 1)
    .join(
        silver_properties.select(
            "property_id",
            "property_number",
            "property_short_address",
            "entity",
            "ownership",
            "housing_program",
            "property_type",
            "property_program",
            "current_stage",
        ),
        "property_id",
        "left",
    )
    .withColumn("exception_type", F.lit("OTHER_VACANCY_OUTSIDE_VOID"))
    .withColumn("exception_severity", F.lit("Error"))
    .withColumn(
        "exception_summary",
        F.concat_ws(
            " ",
            F.lit("Other vacancy range"),
            F.date_format(F.col("other_start_date"), "yyyy-MM-dd"),
            F.lit("to"),
            F.date_format(F.col("other_end_date"), "yyyy-MM-dd"),
            F.lit("sits outside void"),
            F.col("void_id"),
            F.lit("range"),
            F.date_format(F.col("void_start_date"), "yyyy-MM-dd"),
            F.lit("to"),
            F.date_format(F.col("void_end_date"), "yyyy-MM-dd"),
            F.lit("."),
        ),
    )
    .withColumn(
        "exception_id",
        F.concat_ws(
            "-",
            F.lit("EXC"),
            F.col("property_id"),
            F.col("void_id"),
            F.lit("OTHER"),
            F.date_format(F.col("other_start_date"), "yyyyMMdd"),
        ),
    )
    .select(
        "exception_id",
        "exception_type",
        "exception_severity",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_type",
        "property_program",
        "current_stage",
        F.lit(None).cast("string").alias("tenancy_id"),
        F.lit(None).cast("string").alias("tenancy_reference"),
        F.lit(None).cast("string").alias("tenancy_current_stage"),
        F.lit(None).cast("string").alias("tenancy_current_stage_code"),
        F.lit(None).cast("date").alias("raw_tenancy_start_date"),
        F.lit(None).cast("date").alias("tenancy_start_date"),
        F.lit(None).cast("date").alias("raw_tenancy_end_date"),
        F.lit(None).cast("date").alias("tenancy_end_date"),
        "void_id",
        "void_reference",
        "raw_void_start_date",
        "void_start_date",
        "raw_void_end_date",
        "void_end_date",
        F.col("other_start_date").alias("overlap_start_date"),
        F.col("other_end_date").alias("overlap_end_date"),
        F.datediff(F.col("other_end_exclusive"), F.col("other_start_date")).alias("overlap_days"),
        "exception_summary",
        F.lit(TARGET_STATE).alias("report_state"),
    )
)

audit_exceptions_vic = tenancy_interval_exceptions.unionByName(other_vacancy_exceptions)

# Group exceptions by vacancy and property
vacancy_exception_summary = (
    vacancy_intervals.alias("v")
    .join(
        audit_exceptions_vic.alias("e"),
        (F.col("v.property_id") == F.col("e.property_id"))
        & (F.col("e.overlap_start_date") < F.col("v.vacancy_end_exclusive"))
        & (F.date_add(F.col("e.overlap_end_date"), 1) > F.col("v.vacancy_start_date")),
        "left",
    )
    .groupBy("v.vacancy_id")
    .agg(
        F.max(F.when(F.col("e.exception_id").isNotNull(), F.lit(1)).otherwise(F.lit(0))).alias("has_exception_flag"),
        F.countDistinct("e.exception_id").alias("exception_count"),
        F.concat_ws(", ", F.sort_array(F.collect_set("e.exception_type"))).alias("exception_types"),
    )
)

property_exception_summary = (
    audit_exceptions_vic.groupBy("property_id")
    .agg(
        F.lit(1).alias("property_has_exception_flag"),
        F.countDistinct("exception_id").alias("property_exception_count"),
        F.concat_ws(", ", F.sort_array(F.collect_set("exception_type"))).alias("property_exception_types"),
    )
)

# Step 6: Build vacancy void, other vacancy, and keys metrics
vacancy_void_summary = (
    vacancy_intervals.alias("v")
    .join(
        void_intervals.alias("d"),
        (F.col("v.property_id") == F.col("d.property_id"))
        & (F.col("d.void_start_date") < F.col("v.vacancy_end_exclusive"))
        & (F.col("d.void_end_exclusive") > F.col("v.vacancy_start_date")),
        "left",
    )
    .groupBy("v.vacancy_id")
    .agg(
        F.min("d.void_start_date").alias("overlap_void_start_date"),
        F.max("d.void_end_date").alias("overlap_void_end_date"),
        F.max("d.void_end_exclusive").alias("overlap_void_end_exclusive"),
        F.countDistinct("d.void_id").alias("overlap_void_record_count"),
    )
)

vacancy_void_window = Window.partitionBy(F.col("v.vacancy_id")).orderBy(
    F.col("d.void_start_date").asc_nulls_last(),
    F.col("d.void_end_exclusive").desc_nulls_last(),
    F.col("d.void_id").asc_nulls_last(),
)

vacancy_void_selected = (
    vacancy_intervals.alias("v")
    .join(
        void_intervals.alias("d"),
        (F.col("v.property_id") == F.col("d.property_id"))
        & (F.col("d.void_start_date") < F.col("v.vacancy_end_exclusive"))
        & (F.col("d.void_end_exclusive") > F.col("v.vacancy_start_date")),
        "left",
    )
    .withColumn("void_rank", F.row_number().over(vacancy_void_window))
    .filter(F.col("void_rank") == 1)
    .select(
        F.col("v.vacancy_id").alias("vacancy_id"),
        F.col("d.void_id").alias("void_id"),
        F.col("d.void_reference").alias("void_reference"),
        F.col("d.void_start_date").alias("void_start_date"),
        F.col("d.void_end_date").alias("void_end_date"),
        F.col("d.void_end_exclusive").alias("void_end_exclusive"),
        F.col("d.void_reason_code").alias("void_reason_code"),
        F.col("d.void_reason").alias("void_reason"),
        F.col("d.property_condition_code").alias("void_property_condition_code"),
        F.col("d.property_condition").alias("void_property_condition"),
    )
)

vacancy_other_summary = (
    vacancy_intervals.alias("v")
    .join(
        void_intervals.alias("d"),
        (F.col("v.property_id") == F.col("d.property_id"))
        & (F.col("d.other_effective_start_date") < F.col("d.other_effective_end_exclusive"))
        & (F.col("d.other_effective_start_date") < F.col("v.vacancy_end_exclusive"))
        & (F.col("d.other_effective_end_exclusive") > F.col("v.vacancy_start_date")),
        "left",
    )
    .groupBy("v.vacancy_id")
    .agg(
        F.min("d.other_effective_start_date").alias("other_start_date"),
        F.max("d.other_effective_end_date").alias("other_end_date"),
        F.countDistinct("d.void_id").alias("other_vacancy_record_count"),
        F.concat_ws(", ", F.sort_array(F.collect_set("d.other_vacancy_type_reason"))).alias("other_vacancy_type_reasons"),
        F.concat_ws(", ", F.sort_array(F.collect_set("d.void_type"))).alias("other_void_types"),
    )
)

def in_vacancy_period(date_column: str):
    return (
        F.col(date_column).isNotNull()
        & (F.col(date_column) >= F.col("v.vacancy_start_date"))
        & (F.col(date_column) < F.col("v.vacancy_end_exclusive"))
    )

vacancy_keys_candidates = (
    vacancy_intervals.alias("v")
    .join(silver_keys.alias("k"), F.col("v.property_id") == F.col("k.property_id"), "left")
    .withColumn(
        "key_match_in_vacancy",
        F.when(
            in_vacancy_period("k.date_received_from_tenant")
            | in_vacancy_period("k.outgoing_inspection_date")
            | in_vacancy_period("k.contractor_notified_date")
            | in_vacancy_period("k.contractor_collect_key_date")
            | in_vacancy_period("k.contractor_return_key_date"),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )
    .withColumn(
        "key_distance_days",
        F.when(
            F.col("k.key_anchor_date").isNotNull(),
            F.abs(F.datediff(F.col("k.key_anchor_date"), F.col("v.vacancy_start_date"))),
        ).otherwise(F.lit(999999)),
    )
)

vacancy_keys_window = Window.partitionBy(F.col("v.vacancy_id")).orderBy(
    F.col("key_match_in_vacancy").desc(),
    F.col("key_distance_days").asc(),
    F.col("k.key_anchor_date").desc_nulls_last(),
    F.col("k.key_id").desc_nulls_last(),
)

vacancy_keys_selected = (
    vacancy_keys_candidates.withColumn("key_rank", F.row_number().over(vacancy_keys_window))
    .filter(F.col("key_rank") == 1)
    .select(
        F.col("v.vacancy_id").alias("vacancy_id"),
        F.col("k.key_id").alias("key_id"),
        F.col("k.key_reference").alias("key_reference"),
        F.col("k.date_received_from_tenant").alias("key_date_received_from_tenant"),
        F.col("k.outgoing_inspection_date").alias("key_outgoing_inspection_date"),
        F.col("k.contractor_notified_date").alias("key_contractor_notified_date"),
        F.col("k.to_lockbox_onsite").alias("key_to_lockbox_onsite"),
        F.col("k.contractor_collect_key_date").alias("key_contractor_collect_key_date"),
        F.col("k.contractor_name_comments").alias("key_contractor_name_comments"),
        F.col("k.contractor_return_key_date").alias("key_contractor_return_key_date"),
        F.col("k.new_activated_property").alias("key_new_activated_property"),
        F.col("k.vacancy_exemptions_code").alias("key_vacancy_exemptions_code"),
        F.col("k.vacancy_exemptions_desc").alias("key_vacancy_exemptions_desc"),
        F.col("k.property_condition_code").alias("key_property_condition_code"),
        F.col("k.property_condition").alias("key_property_condition"),
        F.col("key_match_in_vacancy"),
        F.col("key_distance_days"),
    )
)

# Step 7: Build fact_vacancy_day_vic (Central Gold Fact table)
vacancy_days = (
    vacancy_intervals.select(
        "vacancy_id",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_type",
        "property_program",
        "property_source",
        "current_stage",
        "vacancy_origin",
        "vacancy_reason_code",
        "vacancy_reason",
        "vacancy_start_date",
        "vacancy_end_date",
        "vacancy_end_date_display",
        "vacancy_end_exclusive",
        "vacancy_start_tenancy_id",
        "vacancy_start_tenancy_start_date",
        "vacancy_start_tenancy_end_date",
        "vacancy_start_tenancy_current_stage",
        "vacancy_end_tenancy_id",
        "vacancy_end_tenancy_start_date",
        "vacancy_end_tenancy_end_date",
        "vacancy_end_tenancy_current_stage",
        "report_state",
    )
    .withColumn(
        "vacancy_date_array",
        F.when(
            F.col("vacancy_start_date")
            <= F.date_sub(F.col("vacancy_end_exclusive"), 1),
            F.sequence(
                F.col("vacancy_start_date"),
                F.date_sub(F.col("vacancy_end_exclusive"), 1),
                F.expr("interval 1 day"),
            )
        ).otherwise(EMPTY_DATE_ARRAY),
    )
    .withColumn("vacancy_date", F.explode("vacancy_date_array"))
    .drop("vacancy_date_array")
)

void_days = (
    void_intervals.select(
        "void_id",
        "property_id",
        "void_reference",
        "void_reason_code",
        "void_reason",
        "property_condition_code",
        "property_condition",
        "key_register_engagement_id",
        F.when(
            F.col("void_start_date")
            <= F.date_sub(F.col("void_end_exclusive"), 1),
            F.sequence(
                F.col("void_start_date"),
                F.date_sub(F.col("void_end_exclusive"), 1),
                F.expr("interval 1 day"),
            )
        )
        .otherwise(EMPTY_DATE_ARRAY)
        .alias("vacancy_date_array"),
    )
    .withColumn("vacancy_date", F.explode("vacancy_date_array"))
    .drop("vacancy_date_array")
    .dropDuplicates(["property_id", "vacancy_date", "void_id"])
    .withColumn(
        "void_day_rank",
        F.row_number().over(
            Window.partitionBy("property_id", "vacancy_date").orderBy(
                F.col("void_id").asc_nulls_last()
            )
        ),
    )
    .filter(F.col("void_day_rank") == 1)
    .drop("void_day_rank")
)

other_days = (
    void_intervals.select(
        "void_id",
        "property_id",
        "void_reference",
        "other_vacancy_type_reason",
        "void_type",
        F.when(
            F.col("other_effective_start_date")
            <= F.date_sub(F.col("other_effective_end_exclusive"), 1),
            F.sequence(
                F.col("other_effective_start_date"),
                F.date_sub(F.col("other_effective_end_exclusive"), 1),
                F.expr("interval 1 day"),
            )
        )
        .otherwise(EMPTY_DATE_ARRAY)
        .alias("vacancy_date_array"),
    )
    .withColumn("vacancy_date", F.explode("vacancy_date_array"))
    .drop("vacancy_date_array")
    .dropDuplicates(["property_id", "vacancy_date", "void_id"])
    .withColumn(
        "other_day_rank",
        F.row_number().over(
            Window.partitionBy("property_id", "vacancy_date").orderBy(
                F.col("void_id").asc_nulls_last()
            )
        ),
    )
    .filter(F.col("other_day_rank") == 1)
    .drop("other_day_rank")
)

vacancy_day_fact = (
    vacancy_days.alias("v")
    .join(void_days.alias("d"), ["property_id", "vacancy_date"], "left")
    .join(other_days.alias("o"), ["property_id", "vacancy_date"], "left")
    .withColumn("is_untenantable", F.col("d.void_id").isNotNull())
    .withColumn("is_other", F.col("o.void_id").isNotNull())
    .withColumn(
        "day_type",
        F.when(F.col("is_other"), F.lit("Other"))
        .when(F.col("is_untenantable"), F.lit("Untenantable"))
        .otherwise(F.lit("Tenantable")),
    )
    .withColumn("vacancy_day_count", F.lit(1))
    .withColumn(
        "tenantable_day_count",
        F.when(~F.col("is_untenantable") & ~F.col("is_other"), 1).otherwise(0),
    )
    .withColumn(
        "untenantable_day_count",
        F.when(F.col("is_untenantable") & ~F.col("is_other"), 1).otherwise(0),
    )
    .withColumn("other_day_count", F.when(F.col("is_other"), 1).otherwise(0))
    .select(
        "vacancy_id",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_type",
        "property_program",
        "property_source",
        "current_stage",
        "vacancy_origin",
        "vacancy_reason_code",
        "vacancy_reason",
        "vacancy_start_date",
        "vacancy_end_date",
        "vacancy_end_date_display",
        "vacancy_end_exclusive",
        "vacancy_start_tenancy_id",
        "vacancy_start_tenancy_start_date",
        "vacancy_start_tenancy_end_date",
        "vacancy_start_tenancy_current_stage",
        "vacancy_end_tenancy_id",
        "vacancy_end_tenancy_start_date",
        "vacancy_end_tenancy_end_date",
        "vacancy_end_tenancy_current_stage",
        "vacancy_date",
        "day_type",
        "vacancy_day_count",
        "tenantable_day_count",
        "untenantable_day_count",
        "other_day_count",
        F.col("d.void_id").alias("void_id"),
        F.col("d.void_reference").alias("void_reference"),
        F.col("d.void_reason_code").alias("void_reason_code"),
        F.col("d.void_reason").alias("void_reason"),
        F.col("d.property_condition_code").alias("void_property_condition_code"),
        F.col("d.property_condition").alias("void_property_condition"),
        F.col("d.key_register_engagement_id").alias("key_register_engagement_id"),
        F.col("o.void_id").alias("other_void_id"),
        F.col("o.void_reference").alias("other_void_reference"),
        F.col("o.other_vacancy_type_reason").alias("other_vacancy_type_reason"),
        F.col("o.void_type").alias("other_void_type"),
        "report_state",
    )
)

# Step 8: Build fact_vacancy_interval_vic (Central Gold Interval Fact table)
vacancy_day_metrics = (
    vacancy_day_fact.groupBy("vacancy_id")
    .agg(
        F.sum("vacancy_day_count").alias("full_vacancy_days_from_day_fact"),
        F.sum("tenantable_day_count").alias("full_tenantable_days"),
        F.sum("untenantable_day_count").alias("full_untenantable_days"),
        F.sum("other_day_count").alias("full_other_days"),
        F.sum("other_day_count").alias("other_days"),
        F.min("vacancy_date").alias("first_vacancy_date"),
        F.max("vacancy_date").alias("last_vacancy_date"),
        F.countDistinct("void_id").alias("void_record_count"),
    )
)

fact_vacancy_interval_vic = (
    vacancy_intervals.select(
        "vacancy_id",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_type",
        "property_program",
        "property_source",
        "current_stage",
        "vacancy_origin",
        "vacancy_reason_code",
        "vacancy_reason",
        "vacancy_start_date",
        "vacancy_end_date",
        "vacancy_end_date_display",
        "vacancy_end_exclusive",
        "vacancy_start_tenancy_id",
        "vacancy_start_tenancy_start_date",
        "vacancy_start_tenancy_end_date",
        "vacancy_start_tenancy_current_stage",
        "vacancy_end_tenancy_id",
        "vacancy_end_tenancy_start_date",
        "vacancy_end_tenancy_end_date",
        "vacancy_end_tenancy_current_stage",
        "is_open_vacancy",
        "report_state",
        "full_vacancy_days",
    )
    .join(vacancy_void_summary, "vacancy_id", "left")
    .join(vacancy_void_selected, "vacancy_id", "left")
    .join(vacancy_other_summary, "vacancy_id", "left")
    .join(vacancy_keys_selected, "vacancy_id", "left")
    .join(vacancy_exception_summary, "vacancy_id", "left")
    .join(property_exception_summary, "property_id", "left")
    .join(vacancy_day_metrics, "vacancy_id", "left")
    .withColumn(
        "full_vacancy_days",
        F.coalesce(F.col("full_vacancy_days_from_day_fact"), F.col("full_vacancy_days")),
    )
    .withColumn(
        "overlap_void_record_count",
        F.coalesce(F.col("overlap_void_record_count"), F.lit(0)),
    )
    .withColumn("full_tenantable_days", F.coalesce(F.col("full_tenantable_days"), F.lit(0)))
    .withColumn(
        "full_untenantable_days",
        F.coalesce(F.col("full_untenantable_days"), F.lit(0)),
    )
    .withColumn("full_other_days", F.coalesce(F.col("full_other_days"), F.lit(0)))
    .withColumn("other_days", F.coalesce(F.col("other_days"), F.lit(0)))
    .withColumn("other_vacancy_record_count", F.coalesce(F.col("other_vacancy_record_count"), F.lit(0)))
    .withColumn("void_record_count", F.coalesce(F.col("void_record_count"), F.lit(0)))
    .withColumn("has_exception_flag", F.coalesce(F.col("has_exception_flag"), F.lit(0)))
    .withColumn("exception_count", F.coalesce(F.col("exception_count"), F.lit(0)))
    .withColumn("property_has_exception_flag", F.coalesce(F.col("property_has_exception_flag"), F.lit(0)))
    .withColumn("property_exception_count", F.coalesce(F.col("property_exception_count"), F.lit(0)))
    .drop("full_vacancy_days_from_day_fact")
    .withColumn("meets_21_day_benchmark", F.col("full_vacancy_days") <= 21)
    .withColumn("meets_48_day_benchmark", F.col("full_vacancy_days") <= 48)
)

keys_staged_vic = (
    silver_keys.withColumn("report_state", F.lit(TARGET_STATE))
    .withColumn(
        "keys_mapping_note",
        F.lit(
            "Keys.PARENT_ENGAGEMENT_ID is confirmed as property_id. Vacancy output uses the closest matching keys row per vacancy based on property_id and key dates."
        ),
    )
)

# Step 9: Build deep-trace validation audits
audit_property_vic = (
    silver_properties.withColumn("report_state", F.lit(TARGET_STATE))
    .withColumn("source_date_offset_days", F.lit(PROPERTY_SOURCE_DATE_OFFSET_DAYS))
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
        "raw_property_start_date",
        "raw_record_start_date",
        "raw_effective_property_start_date",
        "property_start_date",
        "raw_property_end_date",
        "property_end_date",
        "raw_inactive_date",
        "inactive_date",
        "current_stage",
        "current_stage_code",
        "active_code",
        "source_date_offset_days",
        "report_state",
    )
)

audit_tenancy_vic = (
    silver_tenancies.join(
        silver_properties.select(
            "property_id",
            "property_type_code",
            "property_type",
            F.col("property_program_code").alias("property_program_code"),
            F.col("property_program").alias("property_program"),
            F.col("current_stage").alias("property_current_stage"),
            F.col("current_stage_code").alias("property_current_stage_code"),
        ),
        "property_id",
        "left",
    )
    .withColumn("report_state", F.lit(TARGET_STATE))
    .withColumn("source_date_offset_days", F.lit(TENANCY_SOURCE_DATE_OFFSET_DAYS))
    .select(
        "property_id",
        "property_type_code",
        "property_type",
        "property_program_code",
        "property_program",
        "property_current_stage",
        "property_current_stage_code",
        "tenancy_id",
        "tenancy_reference",
        "raw_tenancy_start_date",
        "tenancy_start_date",
        "raw_tenancy_end_date",
        "tenancy_end_date",
        "tenancy_end_reason_code",
        "tenancy_end_reason",
        "current_stage",
        "current_stage_code",
        "active_code",
        "raw_inactive_date",
        "inactive_date",
        "is_excluded_from_vacancy_logic",
        "source_date_offset_days",
        "report_state",
    )
)

audit_void_vic = (
    silver_voids.join(
        silver_properties.select(
            "property_id",
            "property_type_code",
            "property_type",
            F.col("property_program_code").alias("property_program_code"),
            F.col("property_program").alias("property_program"),
            F.col("current_stage").alias("property_current_stage"),
            F.col("current_stage_code").alias("property_current_stage_code"),
        ),
        "property_id",
        "left",
    )
    .withColumn("report_state", F.lit(TARGET_STATE))
    .withColumn("source_date_offset_days", F.lit(VOID_SOURCE_DATE_OFFSET_DAYS))
    .select(
        "property_id",
        "property_type_code",
        "property_type",
        "property_program_code",
        "property_program",
        "property_current_stage",
        "property_current_stage_code",
        "void_id",
        "void_reference",
        "raw_void_start_date",
        "void_start_date",
        "raw_void_end_date",
        "void_end_date",
        "void_end_exclusive",
        "void_reason_code",
        "void_reason",
        "property_condition_code",
        "property_condition",
        "key_register_engagement_id",
        "other_vacancy_type_reason",
        "raw_other_start_date",
        "other_start_date",
        "raw_other_end_date",
        "other_end_date",
        "other_end_exclusive",
        "has_other_vacancy_range",
        "other_start_date_source",
        "other_end_date_source",
        "other_effective_start_date",
        "other_effective_end_date",
        "other_effective_end_exclusive",
        "other_vacancy_outside_void_flag",
        "other_start_date_text",
        "other_end_date_text",
        "void_type",
        "source_date_offset_days",
        "report_state",
    )
)

audit_keys_vic = (
    silver_keys.join(
        silver_properties.select(
            "property_id",
            "property_type_code",
            "property_type",
            F.col("property_program_code").alias("property_program_code"),
            F.col("property_program").alias("property_program"),
            F.col("current_stage").alias("property_current_stage"),
            F.col("current_stage_code").alias("property_current_stage_code"),
        ),
        "property_id",
        "left",
    )
    .withColumn("report_state", F.lit(TARGET_STATE))
    .withColumn("source_date_offset_days", F.lit(KEYS_SOURCE_DATE_OFFSET_DAYS))
    .select(
        "property_id",
        "property_type_code",
        "property_type",
        "property_program_code",
        "property_program",
        "property_current_stage",
        "property_current_stage_code",
        "parent_engagement_id",
        "key_id",
        "key_reference",
        "raw_date_received_from_tenant",
        "date_received_from_tenant",
        "raw_outgoing_inspection_date",
        "outgoing_inspection_date",
        "raw_contractor_notified_date",
        "contractor_notified_date",
        "raw_contractor_collect_key_date",
        "contractor_collect_key_date",
        "raw_contractor_return_key_date",
        "contractor_return_key_date",
        "raw_key_anchor_date",
        "key_anchor_date",
        "to_lockbox_onsite",
        "contractor_name_comments",
        "new_activated_property",
        "vacancy_exemptions_code",
        "vacancy_exemptions_desc",
        "property_condition_code",
        "property_condition",
        "source_date_offset_days",
        "report_state",
    )
)

# Step 10: Persist all conformed Gold and audit tables
write_delta(vacancy_day_fact, "fact_vacancy_day_vic")
write_delta(fact_vacancy_interval_vic, "fact_vacancy_interval_vic")
write_delta(keys_staged_vic, "stg_keys_vic")
write_delta(audit_property_vic, "audit_property_vic")
write_delta(audit_tenancy_vic, "audit_tenancy_vic")
write_delta(audit_void_vic, "audit_void_vic")
write_delta(audit_keys_vic, "audit_keys_vic")
write_delta(audit_exceptions_vic, "audit_exceptions_vic")

print("Gold facts, conformed keys staging, and validation audit tables successfully completed.")
