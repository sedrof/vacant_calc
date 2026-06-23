# Semantic Model: Report Tables and Fields

This document lists all the tables and fields used in the **Vacancy turnaround (working operational) report pages** for the Victoria (VIC) Vacancy reporting solution built in Microsoft Fabric.

---

## 1. Core Model Tables (Used for Main Reporting & KPIs)

### Table: `fact_vacancy_day_vic`
* **Purpose:** The central fact table at the **daily grain** (one row per vacancy per day). It handles precise date slicing via the global date filter and guarantees accurate day counting for KPI measures.
* **Fields:**
  * `vacancy_id` (String) - Unique identifier for each vacancy instance (formatted as `property_id_dd/MM/yy`).
  * `property_id` (String) - ID of the associated property.
  * `property_number` (String) - Business identifier for the property.
  * `property_short_address` (String) - Address of the property.
  * `entity` (String) - Entity description (reporting unit).
  * `ownership` (String) - Ownership type.
  * `housing_program` (String) - Housing program description.
  * `property_type` (String) - Type of property (e.g., House, Unit).
  * `property_program` (String) - Property program.
  * `property_source` (String) - Property source (derived from program).
  * `current_stage` (String) - Current lifecycle stage of the property.
  * `vacancy_origin` (String) - Origin of the vacancy (e.g., `tenancy_end`, `property_start`).
  * `vacancy_reason_code` (String) - Code for the exit/vacancy reason.
  * `vacancy_reason` (String) - Business reason explaining why the property became vacant.
  * `vacancy_start_date` (Date) - Start date of the vacancy.
  * `vacancy_end_date` (Date) - Calculated inclusive end date of the vacancy.
  * `vacancy_end_date_display` (Date) - Business-facing end date (blank for open vacancies).
  * `vacancy_end_exclusive` (Date) - Stored technical exclusive end boundary (used for interval logic).
  * `vacancy_start_tenancy_id` (String) - ID of the tenancy that ended, starting this vacancy.
  * `vacancy_start_tenancy_start_date` (Date) - Start date of the tenancy that ended.
  * `vacancy_start_tenancy_end_date` (Date) - End date of the tenancy that ended.
  * `vacancy_start_tenancy_current_stage` (String) - Stage of the preceding tenancy.
  * `vacancy_end_tenancy_id` (String) - ID of the next tenancy that closed this vacancy.
  * `vacancy_end_tenancy_start_date` (Date) - Start date of the next tenancy.
  * `vacancy_end_tenancy_end_date` (Date) - End date of the next tenancy.
  * `vacancy_end_tenancy_current_stage` (String) - Stage of the succeeding tenancy.
  * `vacancy_date` (Date) - The specific day represented by this fact row (joins to `dim_date[date]`).
  * `day_type` (String) - Classification of the day: `Tenantable`, `Untenantable`, or `Other`.
  * `vacancy_day_count` (Integer) - Constant value `1` representing the vacancy day.
  * `tenantable_day_count` (Integer) - `1` if day is Tenantable, otherwise `0`.
  * `untenantable_day_count` (Integer) - `1` if day is Untenantable (Void and not Other), otherwise `0`.
  * `other_day_count` (Integer) - `1` if day is Other, otherwise `0`.
  * `void_id` (String) - Associated Void ID if the day overlaps a void period.
  * `void_reference` (String) - Associated Void Reference.
  * `void_reason_code` (String) - Code for the void reason.
  * `void_reason` (String) - Description of why the property was void/untenantable.
  * `void_property_condition_code` (String) - Condition code during void.
  * `void_property_condition` (String) - Property condition description during void.
  * `key_register_engagement_id` (String) - Engagement ID for keys.
  * `other_void_id` (String) - Void ID associated with the "Other" day classification.
  * `other_void_reference` (String) - Void Reference for "Other" days.
  * `other_vacancy_type_reason` (String) - Description of the "Other" vacancy type.
  * `other_void_type` (String) - Void type associated with "Other" days.
  * `report_state` (String) - The state context (e.g., `VIC`).

### Table: `fact_vacancy_interval_vic`
* **Purpose:** Contains one row per completed or active vacancy interval. Used for row-level details, benchmarks, and drill-down operations. It is enriched with matching keys, exception statuses, and lifetime totals.
* **Fields:**
  * `vacancy_id` (String) - Unique identifier for the vacancy.
  * `property_id` (String) - ID of the property.
  * `property_number` (String) - Business number of the property.
  * `property_short_address` (String) - Property address.
  * `entity` (String) - Associated entity description.
  * `ownership` (String) - Associated ownership type.
  * `housing_program` (String) - Associated housing program.
  * `property_type` (String) - Property type (e.g., Unit).
  * `property_program` (String) - Property program.
  * `property_source` (String) - Property source (derived from program).
  * `current_stage` (String) - Current stage of the property.
  * `vacancy_origin` (String) - Vacancy origin (`tenancy_end` or `property_start`).
  * `vacancy_reason_code` (String) - Exit reason code.
  * `vacancy_reason` (String) - Exit reason description.
  * `vacancy_start_date` (Date) - Start date of the vacancy.
  * `vacancy_end_date` (Date) - Calculated inclusive end date of the vacancy.
  * `vacancy_end_date_display` (Date) - Inclusive end date displayed to users (null if open).
  * `vacancy_end_exclusive` (Date) - Technical exclusive end date.
  * `vacancy_start_tenancy_id` (String) - Previous tenancy ID.
  * `vacancy_start_tenancy_start_date` (Date) - Preceding tenancy start date.
  * `vacancy_start_tenancy_end_date` (Date) - Preceding tenancy end date.
  * `vacancy_start_tenancy_current_stage` (String) - Preceding tenancy stage.
  * `vacancy_end_tenancy_id` (String) - Next tenancy ID.
  * `vacancy_end_tenancy_start_date` (Date) - Succeeding tenancy start date.
  * `vacancy_end_tenancy_end_date` (Date) - Succeeding tenancy end date.
  * `vacancy_end_tenancy_current_stage` (String) - Succeeding tenancy stage.
  * `is_open_vacancy` (Boolean) - `True` if vacancy is still active (unclosed).
  * `report_state` (String) - State context (`VIC`).
  * `full_vacancy_days` (Integer) - Lifetime total vacancy days.
  * `overlap_void_start_date` (Date) - First overlapping void start date.
  * `overlap_void_end_date` (Date) - Last overlapping void end date.
  * `overlap_void_record_count` (Integer) - Number of overlapping void records.
  * `void_id` (String) - First matched Void ID.
  * `void_reference` (String) - Matched Void Reference.
  * `void_start_date` (Date) - Matched Void Start Date.
  * `void_end_date` (Date) - Matched Void End Date.
  * `void_end_exclusive` (Date) - Matched Void Exclusive End.
  * `void_reason_code` (String) - Matched Void Reason Code.
  * `void_reason` (String) - Matched Void Reason.
  * `void_property_condition_code` (String) - Matched Void Condition Code.
  * `void_property_condition` (String) - Matched Void Property Condition.
  * `other_start_date` (Date) - Overlapping Other Vacancy start date.
  * `other_end_date` (Date) - Overlapping Other Vacancy end date.
  * `other_vacancy_record_count` (Integer) - Count of overlapping Other records.
  * `other_vacancy_type_reasons` (String) - Combined Other Vacancy reasons.
  * `other_void_types` (String) - Combined Other Void types.
  * `key_id` (String) - Closest matched Keys Record ID.
  * `key_reference` (String) - Closest matched Keys Reference.
  * `key_date_received_from_tenant` (Date) - Key date received from tenant.
  * `key_outgoing_inspection_date` (Date) - Key outgoing inspection date.
  * `key_contractor_notified_date` (Date) - Key contractor notified date.
  * `key_to_lockbox_onsite` (Date) - Key to lockbox onsite date.
  * `key_contractor_collect_key_date` (Date) - Key contractor collected key date.
  * `key_contractor_name_comments` (String) - Key contractor name & comments.
  * `key_contractor_return_key_date` (Date) - Key contractor returned key date.
  * `key_new_activated_property` (String) - Flag indicating new property activation.
  * `key_vacancy_exemptions_code` (String) - Vacancy exemption code.
  * `key_vacancy_exemptions_desc` (String) - Vacancy exemption description.
  * `key_property_condition_code` (String) - Outgoing property condition code.
  * `key_property_condition` (String) - Outgoing property condition description.
  * `has_exception_flag` (Integer) - `1` if this vacancy overlaps an active data exception, `0` otherwise.
  * `exception_count` (Integer) - Number of exceptions affecting this vacancy.
  * `exception_types` (String) - Comma-separated list of exception types (e.g. `TENANCY_OVERLAPS_VOID`).
  * `property_has_exception_flag` (Integer) - `1` if the property has any active exceptions, `0` otherwise.
  * `property_exception_count` (Integer) - Total exception count for the property.
  * `property_exception_types` (String) - Comma-separated exceptions for the property.
  * `full_tenantable_days` (Integer) - Lifetime total tenantable days.
  * `full_untenantable_days` (Integer) - Lifetime total untenantable days.
  * `full_other_days` (Integer) - Lifetime total other vacancy days.
  * `other_days` (Integer) - Total conformed other vacancy days (retained for Power BI backward compatibility).
  * `first_vacancy_date` (Date) - First calculated vacancy date.
  * `last_vacancy_date` (Date) - Last calculated vacancy date.
  * `void_record_count` (Integer) - Count of void records within this interval.
  * `meets_21_day_benchmark` (Boolean) - `True` if `full_vacancy_days` <= 21.
  * `meets_48_day_benchmark` (Boolean) - `True` if `full_vacancy_days` <= 48.

### Table: `dim_property_vic`
* **Purpose:** Property dimension table. Houses standard property attributes and standard-address performance filters.
* **Fields:**
  * `property_id` (String) - Unique property identifier (1:1 with Property).
  * `property_number` (String) - Business property number.
  * `property_short_address` (String) - Short form of the address.
  * `is_standard_address` (Boolean) - `True` if the address does not contain brackets or markers (optimized standard address filter).
  * `suburb` (String) - Property suburb.
  * `state` (String) - VIC.
  * `postcode` (String) - Postcode.
  * `entity_code` (String) - Entity identifier code.
  * `entity` (String) - Entity name.
  * `ownership_code` (String) - Ownership category code.
  * `ownership` (String) - Ownership category description.
  * `housing_program_code` (String) - Housing program code.
  * `housing_program` (String) - Housing program description.
  * `property_type_code` (String) - Property type code.
  * `property_type` (String) - Property type description.
  * `property_program_code` (String) - Property program code.
  * `property_program` (String) - Property program description.
  * `property_source_code` (String) - Property source code.
  * `property_source` (String) - Property source description.
  * `property_start_date` (Date) - Corrected property start date.
  * `property_end_date` (Date) - Corrected property end date.
  * `inactive_date` (Date) - Record inactivation date.
  * `current_stage` (String) - Property current stage.
  * `current_stage_code` (String) - Stage code.
  * `active_code` (String) - Active stage code.
  * `report_state` (String) - VIC.

### Table: `dim_date`
* **Purpose:** Existing physical calendar dimension.
* **Fields:**
  * `date` (Date) - Date key (slicer driven).
  * *Additional standard calendar columns (Year, Quarter, Month, Day of Week, etc.).*

---

## 2. Parameter & Config Tables (Used for Governance)

### Table: `dim_active_vacancy_rule_parameters`
* **Purpose:** Exposes the active date corrections and offset parameters applied in Fabric to the report's Config page.
* **Fields:**
  * `rule_name` (String) - Name of the operational rule (e.g. `property_source_date_offset`, `tenancy_end_to_vacancy_start`).
  * `offset_days` (Integer) - Configured day offset to adjust raw TechOne dates.
  * `is_active` (Boolean) - `True` if active.
  * `effective_from` (Date) - Effective date of the rule.
  * `comment` (String) - Business reason or description for the offset.
  * `updated_by` (String) - Author of the rule parameter.
  * `updated_at` (Timestamp) - Rule parameter modification date.

---

## 3. Operational Staging Tables (Used in Staging & Keys Detail)

### Table: `stg_keys_vic`
* **Purpose:** Stages raw key register details matched per property.
* **Fields:**
  * `key_id` (String) - Unique key record ID.
  * `parent_engagement_id` (String) - Maps to `property_id`.
  * `key_reference` (String) - Keys reference ID.
  * `date_received_from_tenant` (Date) - Adjusted date keys received.
  * `outgoing_inspection_date` (Date) - Adjusted inspection date.
  * `contractor_notified_date` (Date) - Adjusted contractor notification date.
  * `to_lockbox_onsite` (Date) - Adjusted lockbox onsite date.
  * `contractor_collect_key_date` (Date) - Adjusted contractor collect date.
  * `contractor_name_comments` (String) - Contractor comments.
  * `contractor_return_key_date` (Date) - Adjusted contractor return date.
  * `new_activated_property` (String) - New property activation indicator.
  * `vacancy_exemptions_code` (String) - Exemption code.
  * `vacancy_exemptions_desc` (String) - Exemption details.
  * `property_condition_code` (String) - Condition code.
  * `property_condition` (String) - Condition description.
  * `report_state` (String) - VIC.
  * `keys_mapping_note` (String) - Diagnostic information about the mapping of keys.

---

## 4. Deep-Trace Validation Tables (Used on Property Trace & Exception pages)

These tables preserve both raw source dates (prefixed with `raw_`) and adjusted operational dates (after rule parameter offsets) for developers and auditors to trace calculations step-by-step.

### Table: `audit_property_vic`
* **Fields:**
  * `property_id`, `property_number`, `property_short_address`, `is_standard_address`, `suburb`, `state`, `postcode`
  * `entity_code`, `entity`, `ownership_code`, `ownership`, `housing_program_code`, `housing_program`, `property_type_code`, `property_type`, `property_program_code`, `property_program`
  * `raw_property_start_date` (Date) - Raw start date.
  * `raw_record_start_date` (Date) - Raw baseline record start date.
  * `raw_effective_property_start_date` (Date) - Raw effective start date.
  * `property_start_date` (Date) - Adjusted effective start date.
  * `raw_property_end_date` (Date) - Raw end date.
  * `property_end_date` (Date) - Adjusted end date.
  * `raw_inactive_date` (Date) - Raw inactive date.
  * `inactive_date` (Date) - Adjusted inactive date.
  * `current_stage`, `current_stage_code`, `active_code`, `source_date_offset_days`, `report_state`

### Table: `audit_tenancy_vic`
* **Fields:**
  * `property_id`, `property_type_code`, `property_type`, `property_program_code`, `property_program`, `property_current_stage`, `property_current_stage_code`
  * `tenancy_id` (String) - Unique tenancy ID.
  * `tenancy_reference` (String) - Tenancy code reference.
  * `raw_tenancy_start_date` (Date) - Raw tenancy start.
  * `tenancy_start_date` (Date) - Adjusted tenancy start.
  * `raw_tenancy_end_date` (Date) - Raw tenancy end.
  * `tenancy_end_date` (Date) - Adjusted tenancy end.
  * `tenancy_end_reason_code`, `tenancy_end_reason`, `current_stage`, `current_stage_code`, `active_code`
  * `raw_inactive_date` (Date), `inactive_date` (Date)
  * `is_excluded_from_vacancy_logic` (Integer) - `1` if stage is `ALLOCATION CANCELLED` (ignored in calculations), `0` otherwise.
  * `source_date_offset_days`, `report_state`

### Table: `audit_void_vic`
* **Fields:**
  * `property_id`, `property_type_code`, `property_type`, `property_program_code`, `property_program`, `property_current_stage`, `property_current_stage_code`
  * `void_id`, `void_reference`
  * `raw_void_start_date` (Date), `void_start_date` (Date)
  * `raw_void_end_date` (Date), `void_end_date` (Date)
  * `void_end_exclusive` (Date) - Technical exclusive void end.
  * `void_reason_code`, `void_reason`, `property_condition_code`, `property_condition`, `key_register_engagement_id`
  * `other_vacancy_type_reason`
  * `raw_other_start_date` (Date), `other_start_date` (Date)
  * `raw_other_end_date` (Date), `other_end_date` (Date)
  * `other_end_exclusive` (Date) - Technical exclusive other end.
  * `has_other_vacancy_range` (Boolean) - `True` if other range is specified.
  * `other_start_date_source`, `other_end_date_source`
  * `other_effective_start_date` (Date) - Counted start date (capped to parent void).
  * `other_effective_end_date` (Date) - Counted inclusive end date (capped).
  * `other_effective_end_exclusive` (Date) - Counted exclusive boundary.
  * `other_vacancy_outside_void_flag` (Integer) - `1` if other range exceeded void limits (anomaly), `0` otherwise.
  * `other_start_date_text`, `other_end_date_text`
  * `void_type`, `source_date_offset_days`, `report_state`

### Table: `audit_keys_vic`
* **Fields:**
  * `property_id`, `property_type_code`, `property_type`, `property_program_code`, `property_program`, `property_current_stage`, `property_current_stage_code`, `parent_engagement_id`
  * `key_id`, `key_reference`
  * `raw_date_received_from_tenant` (Date), `date_received_from_tenant` (Date)
  * `raw_outgoing_inspection_date` (Date), `outgoing_inspection_date` (Date)
  * `raw_contractor_notified_date` (Date), `contractor_notified_date` (Date)
  * `raw_contractor_collect_key_date` (Date), `contractor_collect_key_date` (Date)
  * `raw_contractor_return_key_date` (Date), `contractor_return_key_date` (Date)
  * `raw_key_anchor_date` (Date), `key_anchor_date` (Date)
  * `to_lockbox_onsite` (Date)
  * `contractor_name_comments`, `new_activated_property`, `vacancy_exemptions_code`, `vacancy_exemptions_desc`, `property_condition_code`, `property_condition`, `source_date_offset_days`, `report_state`

### Table: `audit_exceptions_vic`
* **Fields:**
  * `exception_id` (String) - Unique identifier for the exception.
  * `exception_type` (String) - Typology (e.g. `TENANCY_OVERLAPS_VOID`, `OTHER_VACANCY_OUTSIDE_VOID`).
  * `exception_severity` (String) - Anomaly impact (e.g. `Error`, `Warning`).
  * `property_id`, `property_number`, `property_short_address`, `entity`, `ownership`, `housing_program`, `property_type`, `property_program`, `current_stage`
  * `tenancy_id`, `tenancy_reference`, `tenancy_current_stage`, `tenancy_current_stage_code`
  * `raw_tenancy_start_date` (Date), `tenancy_start_date` (Date)
  * `raw_tenancy_end_date` (Date), `tenancy_end_date` (Date)
  * `void_id`, `void_reference`
  * `raw_void_start_date` (Date), `void_start_date` (Date)
  * `raw_void_end_date` (Date), `void_end_date` (Date)
  * `overlap_start_date` (Date) - Calculated start boundary of the overlap.
  * `overlap_end_date` (Date) - Calculated inclusive end boundary of the overlap.
  * `overlap_days` (Integer) - Quantity of overlapping error days.
  * `exception_summary` (String) - Explanatory text summarizing the data violation.
  * `report_state` (String) - VIC.
