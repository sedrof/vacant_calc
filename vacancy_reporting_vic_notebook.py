from pyspark.sql import functions as F
from pyspark.sql.window import Window


# Fabric notebook parameters. Replace these values for your environment.
WAREHOUSE_PREFIX = "`Evolve-TechOne`.Shortcut.ev"
OUTPUT_DATABASE = "vacancy_reporting"
TARGET_STATE = "VIC"
AS_AT_DATE = None  # Example: "2026-03-31". Leave as None to use today's date.
CONFIG_TABLE = "cfg_vacancy_rule_parameters"
ACTIVE_CONFIG_TABLE = "dim_active_vacancy_rule_parameters"

DEFAULT_RULE_PARAMETERS = [
    {
        "rule_name": "tenancy_end_to_vacancy_start",
        "offset_days": 1,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Workbook logic: vacancy start is tenancy end plus one day.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
    {
        "rule_name": "next_tenancy_start_to_vacancy_end",
        "offset_days": -1,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Workbook logic: vacancy inclusive end is next tenancy start minus one day.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
    {
        "rule_name": "property_start_to_vacancy_start",
        "offset_days": 0,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Usually zero. Change only if property start dates need the same correction.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
    {
        "rule_name": "property_source_date_offset",
        "offset_days": 0,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Optional raw source date shift for the Property table.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
    {
        "rule_name": "tenancy_source_date_offset",
        "offset_days": 0,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Optional raw source date shift for the Tenancy table.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
    {
        "rule_name": "void_source_date_offset",
        "offset_days": 0,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Optional raw source date shift for the Void table.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
    {
        "rule_name": "keys_source_date_offset",
        "offset_days": 0,
        "is_active": True,
        "effective_from": "1900-01-01",
        "comment": "Optional raw source date shift for the Keys table.",
        "updated_by": "notebook_bootstrap",
        "updated_at": "1900-01-01 00:00:00",
    },
]


def qcol(name: str):
    return F.col(f"`{name}`")


def load_table(table_name: str, column_map: list[tuple[str, str]]):
    return spark.table(f"{WAREHOUSE_PREFIX}.{table_name}").select(
        *[qcol(source).alias(alias) for source, alias in column_map]
    )


def with_date(df, columns: list[str]):
    for column_name in columns:
        df = df.withColumn(column_name, F.to_date(F.col(column_name)))
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


def write_delta(df, table_name: str):
    (
        df.write.mode("overwrite")
        .format("delta")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{OUTPUT_DATABASE}.{table_name}")
    )


spark.sql(f"CREATE DATABASE IF NOT EXISTS {OUTPUT_DATABASE}")
config_table_fqn = f"{OUTPUT_DATABASE}.{CONFIG_TABLE}"


if not spark.catalog.tableExists(config_table_fqn):
    (
        spark.createDataFrame(DEFAULT_RULE_PARAMETERS)
        .withColumn("effective_from", F.to_date("effective_from"))
        .withColumn("updated_at", F.to_timestamp("updated_at"))
        .write.mode("overwrite")
        .format("delta")
        .option("overwriteSchema", "true")
        .saveAsTable(config_table_fqn)
    )

config_window = Window.partitionBy("rule_name").orderBy(
    F.col("effective_from").desc_nulls_last(),
    F.col("updated_at").desc_nulls_last(),
)

active_rule_parameters = (
    spark.table(config_table_fqn)
    .withColumn("effective_from", F.to_date("effective_from"))
    .withColumn("updated_at", F.to_timestamp("updated_at"))
    .filter(F.coalesce(F.col("is_active"), F.lit(True)))
    .withColumn("rule_rank", F.row_number().over(config_window))
    .filter(F.col("rule_rank") == 1)
    .drop("rule_rank")
)

rule_parameter_map = {
    row["rule_name"]: int(row["offset_days"])
    for row in active_rule_parameters.select("rule_name", "offset_days").collect()
}

TENANCY_END_TO_VACANCY_START_OFFSET_DAYS = rule_parameter_map.get(
    "tenancy_end_to_vacancy_start",
    1,
)
NEXT_TENANCY_START_TO_VACANCY_END_OFFSET_DAYS = rule_parameter_map.get(
    "next_tenancy_start_to_vacancy_end",
    -1,
)
PROPERTY_START_TO_VACANCY_START_OFFSET_DAYS = rule_parameter_map.get(
    "property_start_to_vacancy_start",
    0,
)
PROPERTY_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get(
    "property_source_date_offset",
    0,
)
TENANCY_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get(
    "tenancy_source_date_offset",
    0,
)
VOID_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get(
    "void_source_date_offset",
    0,
)
KEYS_SOURCE_DATE_OFFSET_DAYS = rule_parameter_map.get(
    "keys_source_date_offset",
    0,
)

snapshot_end_exclusive = (
    F.date_add(F.current_date(), 1)
    if AS_AT_DATE is None
    else F.date_add(F.to_date(F.lit(AS_AT_DATE)), 1)
)


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
]

keys_columns = [
    ("DataSet.KEY_ID", "key_id"),
    ("DataSet.PARENT_ENGAGEMENT_ID", "parent_engagement_id"),
    ("DataSet.KEY_REFERENCE", "key_reference"),
    ("DataSet.DATE_RECEIVED_FROM_TENANT", "date_received_from_tenant"),
    ("DataSet.OUTGOING_INSPECTION_DATE", "outgoing_inspection_date"),
    ("DataSet.CONTRACTOR_NOTIFIED_DATE", "contractor_notified_date"),
    ("DataSet.CONTRACTOR_COLLECT_K_DATE", "contractor_collect_key_date"),
    ("DataSet.CONTRACTOR_RETURN_K_DATE", "contractor_return_key_date"),
    ("DataSet.NEW_ACTIVATED_PROPERTY", "new_activated_property"),
    ("DataSet.VACANCY_EXEMPTIONS_C", "vacancy_exemptions_code"),
    ("DataSet.VACANCY_EXEMPTIONS_DESC", "vacancy_exemptions_desc"),
    ("DataSet.PROPERTY_CONDITION", "property_condition_code"),
    ("DataSet.PROPERTY_CONDITION_D", "property_condition"),
]


properties = (
    load_table("Property", property_columns)
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
    .withColumn("property_id", F.col("property_id").cast("string"))
    .filter(F.upper(F.col("state")) == TARGET_STATE)
    .dropDuplicates(["property_id"])
)

tenancies = (
    load_table("Tenancy", tenancy_columns)
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
)

voids = (
    load_table("Void", void_columns)
    .transform(lambda df: with_date(df, ["void_start_date", "void_end_date"]))
    .transform(
        lambda df: shift_date_columns(
            df,
            ["void_start_date", "void_end_date"],
            VOID_SOURCE_DATE_OFFSET_DAYS,
        )
    )
    .withColumn("void_id", F.col("void_id").cast("string"))
    .withColumn("property_id", F.col("property_id").cast("string"))
    .withColumn(
        "key_register_engagement_id",
        F.col("key_register_engagement_id").cast("string"),
    )
    .filter(F.col("property_id").isNotNull())
)

keys = (
    load_table("Keys", keys_columns)
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
)


dim_property_vic = (
    properties.withColumnRenamed("property_program", "property_source")
    .withColumnRenamed("property_program_code", "property_source_code")
    .withColumn("report_state", F.lit(TARGET_STATE))
    .select(
        "property_id",
        "property_number",
        "property_short_address",
        "suburb",
        "state",
        "postcode",
        "entity_code",
        "entity",
        "ownership_code",
        "ownership",
        "housing_program_code",
        "housing_program",
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


tenancy_sequence_window = Window.partitionBy("property_id").orderBy(
    F.col("tenancy_start_date").asc_nulls_last(),
    F.col("tenancy_id"),
)

tenancy_rank_window = Window.partitionBy("property_id").orderBy(
    F.col("tenancy_start_date").asc_nulls_last(),
    F.col("tenancy_id"),
)

tenancies_ordered = (
    tenancies.withColumn(
        "next_tenancy_start_date",
        F.lead("tenancy_start_date").over(tenancy_sequence_window),
    )
    .withColumn(
        "next_tenancy_id",
        F.lead("tenancy_id").over(tenancy_sequence_window),
    )
    .withColumn("tenancy_rank", F.row_number().over(tenancy_rank_window))
)

first_tenancy = (
    tenancies_ordered.filter(F.col("tenancy_rank") == 1)
    .select(
        "property_id",
        F.col("tenancy_id").alias("first_tenancy_id"),
        F.col("tenancy_start_date").alias("first_tenancy_start_date"),
    )
)


ended_tenancy_vacancies = (
    tenancies_ordered.filter(F.col("tenancy_end_date").isNotNull())
    .select(
        "property_id",
        F.col("tenancy_id").alias("vacancy_start_tenancy_id"),
        F.col("next_tenancy_id").alias("vacancy_end_tenancy_id"),
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
        .alias("vacancy_end_exclusive"),
        F.col("tenancy_end_reason_code").alias("vacancy_reason_code"),
        F.col("tenancy_end_reason").alias("vacancy_reason"),
        F.lit("tenancy_end").alias("vacancy_origin"),
    )
    .filter(F.col("vacancy_start_date") < F.col("vacancy_end_exclusive"))
)

initial_property_vacancies = (
    properties.alias("p")
    .join(first_tenancy.alias("t"), "property_id", "left")
    .select(
        F.col("property_id"),
        F.lit(None).cast("string").alias("vacancy_start_tenancy_id"),
        F.col("t.first_tenancy_id").alias("vacancy_end_tenancy_id"),
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
        .alias("vacancy_end_exclusive"),
        F.lit("NEW_PROPERTY").alias("vacancy_reason_code"),
        F.lit("Initial vacancy before first tenancy").alias("vacancy_reason"),
        F.lit("property_start").alias("vacancy_origin"),
    )
    .filter(F.col("vacancy_start_date").isNotNull())
    .filter(F.col("vacancy_start_date") < F.col("vacancy_end_exclusive"))
)

vacancy_intervals_base = ended_tenancy_vacancies.unionByName(initial_property_vacancies)

vacancy_id_window = Window.orderBy(
    F.col("property_id"),
    F.col("vacancy_start_date"),
    F.col("vacancy_origin"),
    F.col("vacancy_start_tenancy_id").asc_nulls_last(),
)

vacancy_intervals = (
    vacancy_intervals_base.join(dim_property_vic, "property_id", "inner")
    .withColumn("vacancy_sequence", F.row_number().over(vacancy_id_window))
    .withColumn(
        "vacancy_id",
        F.concat_ws(
            "-",
            F.lit("VIC"),
            F.col("property_id").cast("string"),
            F.date_format("vacancy_start_date", "yyyyMMdd"),
            F.lpad(F.col("vacancy_sequence").cast("string"), 4, "0"),
        ),
    )
    .withColumn(
        "full_vacancy_days",
        F.datediff(F.col("vacancy_end_exclusive"), F.col("vacancy_start_date")),
    )
    .withColumn("is_open_vacancy", F.col("vacancy_end_tenancy_id").isNull())
    .withColumn("report_state", F.lit(TARGET_STATE))
)


void_intervals = (
    voids.join(dim_property_vic.select("property_id"), "property_id", "inner")
    .withColumn(
        "void_end_exclusive",
        F.coalesce(F.col("void_end_date"), snapshot_end_exclusive),
    )
    .filter(F.col("void_start_date").isNotNull())
    .filter(F.col("void_start_date") < F.col("void_end_exclusive"))
    .withColumn("report_state", F.lit(TARGET_STATE))
)


vacancy_days = (
    vacancy_intervals.select(
        "vacancy_id",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_source",
        "vacancy_origin",
        "vacancy_reason_code",
        "vacancy_reason",
        "vacancy_start_date",
        "vacancy_end_exclusive",
        "vacancy_start_tenancy_id",
        "vacancy_end_tenancy_id",
        "report_state",
    )
    .withColumn(
        "vacancy_date",
        F.explode(
            F.sequence(
                F.col("vacancy_start_date"),
                F.date_sub(F.col("vacancy_end_exclusive"), 1),
                F.expr("interval 1 day"),
            )
        ),
    )
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
        F.explode(
            F.sequence(
                F.col("void_start_date"),
                F.date_sub(F.col("void_end_exclusive"), 1),
                F.expr("interval 1 day"),
            )
        ).alias("vacancy_date"),
    )
    .dropDuplicates(["property_id", "vacancy_date", "void_id"])
)

vacancy_day_fact = (
    vacancy_days.alias("v")
    .join(void_days.alias("d"), ["property_id", "vacancy_date"], "left")
    .withColumn("is_untenantable", F.col("d.void_id").isNotNull())
    .withColumn("is_other", F.lit(False))
    .withColumn(
        "day_type",
        F.when(F.col("is_untenantable"), F.lit("Untenantable"))
        .when(F.col("is_other"), F.lit("Other"))
        .otherwise(F.lit("Tenantable")),
    )
    .withColumn("vacancy_day_count", F.lit(1))
    .withColumn(
        "tenantable_day_count",
        F.when(~F.col("is_untenantable") & ~F.col("is_other"), 1).otherwise(0),
    )
    .withColumn("untenantable_day_count", F.when(F.col("is_untenantable"), 1).otherwise(0))
    .withColumn("other_day_count", F.lit(0))
    .select(
        "vacancy_id",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_source",
        "vacancy_origin",
        "vacancy_reason_code",
        "vacancy_reason",
        "vacancy_start_date",
        "vacancy_end_exclusive",
        "vacancy_start_tenancy_id",
        "vacancy_end_tenancy_id",
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
        "report_state",
    )
)


fact_vacancy_interval_vic = (
    vacancy_day_fact.groupBy(
        "vacancy_id",
        "property_id",
        "property_number",
        "property_short_address",
        "entity",
        "ownership",
        "housing_program",
        "property_source",
        "vacancy_origin",
        "vacancy_reason_code",
        "vacancy_reason",
        "vacancy_start_date",
        "vacancy_end_exclusive",
        "vacancy_start_tenancy_id",
        "vacancy_end_tenancy_id",
        "report_state",
    )
    .agg(
        F.sum("vacancy_day_count").alias("full_vacancy_days"),
        F.sum("tenantable_day_count").alias("full_tenantable_days"),
        F.sum("untenantable_day_count").alias("full_untenantable_days"),
        F.sum("other_day_count").alias("full_other_days"),
        F.min("vacancy_date").alias("first_vacancy_date"),
        F.max("vacancy_date").alias("last_vacancy_date"),
        F.countDistinct("void_id").alias("void_record_count"),
    )
    .withColumn("meets_21_day_benchmark", F.col("full_vacancy_days") <= 21)
    .withColumn("meets_48_day_benchmark", F.col("full_vacancy_days") <= 48)
)


keys_staged_vic = (
    keys.withColumn("report_state", F.lit(TARGET_STATE))
    .withColumn(
        "keys_mapping_note",
        F.lit(
            "Keys data is staged only. Parent engagement mapping to the vacancy fact needs business confirmation before relationship activation."
        ),
    )
)


write_delta(dim_property_vic, "dim_property_vic")
write_delta(active_rule_parameters, ACTIVE_CONFIG_TABLE)
write_delta(void_intervals, "fact_void_interval_vic")
write_delta(vacancy_day_fact, "fact_vacancy_day_vic")
write_delta(fact_vacancy_interval_vic, "fact_vacancy_interval_vic")
write_delta(keys_staged_vic, "stg_keys_vic")


display(fact_vacancy_interval_vic.orderBy("property_id", "vacancy_start_date"))
