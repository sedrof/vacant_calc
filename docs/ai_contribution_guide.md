# AI Data Pipeline Standards & Design Patterns
**Owner**: Head of Architects  
**Scope**: Microsoft Fabric & Power BI Reporting Platforms (Generalized Reference)

---

## 1. Architectural Philosophy: The Medallion Pattern

To ensure high data quality, maintainability, and structural scalability, all reporting data pipelines in this workspace must follow a strict **Bronze $\rightarrow$ Silver $\rightarrow$ Gold** Medallion architecture.

```
┌───────────────────────────────┐
│         Source APIs           │ (e.g., ServiceNow, TechOne, SAP, JIRA)
└───────────────┬───────────────┘
                │
                ▼ (Raw paginated extractions with zero transformations)
┌───────────────────────────────┐
│         BRONZE LAYER          │ (Raw Landing Delta Tables)
└───────────────┬───────────────┘
                │
                ▼ (Type casting, structural cleaning, Timezone shifting)
┌───────────────────────────────┐
│         SILVER LAYER          │ (Conformed Standardized Tables)
└───────────────┬───────────────┘
                │
                ▼ (Business rules, mappings, period calculations, star schema)
┌───────────────────────────────┐
│          GOLD LAYER           │ (Read-optimized Presentation Facts & Dims)
└───────────────────────────────┘
```

### Ingestion & Processing Rules
1. **Bronze (Raw Ingestion)**:
   * **Mandate**: Ingest source data 1:1 exactly as it comes from the API or database. No timezone shifts, no type conversions, no field filtering.
   * **Role**: Serves as the immutable historical record. Enables full pipeline re-runs without hitting the source system APIs again.
2. **Silver (Standardization & Quality)**:
   * **Mandate**: Cast columns, resolve dates, handle nulls, standardize strings, and perform timezone shifting.
   * **Role**: Delivers conformed, clean, and typed data. Silver tables are designed for general operational queries and serve as the base for downstream Gold tables.
3. **Gold (Analytical / Presentation)**:
   * **Mandate**: Join reference tables, apply business logic, calculate aggregates, route value priorities, and generate star-schema facts and dimensions.
   * **Role**: Deliver read-optimized presentation tables designed specifically for Power BI import with zero runtime overhead.

---

## 2. Naming & Namespace Conventions

To prevent table pollution and ensure immediate visibility of a table's tier, all database tables and notebooks must follow these naming rules:

### A. Lakehouse Table Names
| Layer | Naming Template | Target Namespace Template | Example (Work Orders Report) | Example (Vacancy Report) |
| :--- | :--- | :--- | :--- | :--- |
| **Bronze** | `Bronze_<System>_<Entity>` | `<schema>.Bronze_<System>_<Entity>` | `wo.Bronze_ServiceNow_WM_Order` | `vac.Bronze_TechOne_Vacancy` |
| **Silver** | `silver_<system>_<entity>` | `<schema>.silver_<system>_<entity>` | `wo.silver_wo_servicenow` | `vac.silver_techone_vacancy` |
| **Gold** | `gold_<domain>_<fact_or_dimension>` | `<schema>.gold_<domain>_<fact_or_dimension>` | `wo.gold_wo_servicenow_event_fact` | `vac.fact_vacancy_day_vic` |
| **Dimension** | `dim_<dimension_name>` | `<schema>.dim_<dimension_name>` | `wo.dim_supplier` | `vac.dim_property_vic` |
| **Slicer** | `slicer_<slicer_name>` | `<schema>.slicer_<slicer_name>` | `wo.slicer_fin_year` | `vac.slicer_report_date` |
| **Metadata** | `<prefix>_<rules_name>` | `<schema>.<prefix>_<rules_name>` | `wo.wo_state_rule_mapping` | `vac.vacancy_rule_parameters` |

*Note: `<schema>` represents the report-specific database namespace folder (e.g., `wo`, `vac`, `smk`).*

### B. Notebook Names
All notebooks must be named after their target tier, reporting prefix, and domain:
* `<report_prefix>_<domain>_bronze_notebook.py` (e.g., `wo_servicenow_bronze_notebook.py`)
* `<report_prefix>_<domain>_silver_notebook.py` (e.g., `wo_servicenow_silver_notebook.py`)
* `<report_prefix>_<domain>_gold_notebook.py` (e.g., `wo_servicenow_gold_notebook.py`)
* `<report_prefix>_<domain>_dimensions_notebook.py` (e.g., `wo_servicenow_dimensions_notebook.py`)

---

## 3. Engineering & Code Standards

### A. Timezone Integrity Constraint
* **Standard**: All timestamp data stored in source databases (e.g. ServiceNow, TechOne) is in UTC.
* **Pipeline Rule**: Conversions to local timezone must occur **exclusively in the Silver Layer**. No raw UTC datetimes are allowed to progress into the Gold layer.
* **Spark Implementation**:
  ```python
  # Shift UTC to local time (e.g., Australia/Sydney)
  df.withColumn("local_datetime", F.from_utc_timestamp(F.col("utc_datetime"), "Australia/Sydney"))
  ```
* All date derivations (e.g., event date, financial year, financial month) must be calculated *after* the timezone shift.

### B. Schema Completeness & Resilience
* **Rule**: To prevent schema drift from crashing downstream processes, notebooks must proactively assert column completeness.
* **Spark Implementation**: Use `ensure_columns()` to check that expected schema fields exist, appending them as Nulls if missing:
  ```python
  def ensure_columns(df: DataFrame, expected_cols: list[str]) -> DataFrame:
      result = df
      for col_name in expected_cols:
          if col_name not in result.columns:
              result = result.withColumn(col_name, F.lit(None).cast("string"))
      return result
  ```

### C. Graceful Degradation of Reference Joins
* **Rule**: Mappings and reference tables may occasionally be modified or fail to load. The pipeline must never fail due to a missing reference table.
* **Spark Implementation**: Use try-except blocks when reading lookup tables and fall back to local regex or heuristics to ensure the report continues to load:
  ```python
  map_df = None
  try:
      map_df = spark.read.table("dim_reference_mapping_table")
  except Exception:
      # Degrade gracefully using local regex fallback
      print("Warning: Reference mapping table missing. Falling back to local rules.")
  ```

---

## 4. Release & Verification Protocol

Before pushing any data pipeline changes, you must execute the following validation checklist:

1. **Syntax Compilation**: Run the Python compilability test to guarantee there are no parse errors:
   ```bash
   python3 -m py_compile <notebook_dir>/<report_prefix>_<domain>_notebook.py
   ```
2. **Schema Matching Audit**: Compare the schema of any modified Gold table against the documented database catalog or data dictionary. All column names, spelling, and types must remain 100% identical to maintain downstream Power BI stability.
3. **Data Parity Test**: Compare a sample dataset's sums and counts before and after your refactoring to verify that totals remain identical down to the last cent.

---

## 5. Reporting Schema Architecture & Best Practices

To avoid performance degradation, schema pollution, and complex DAX query locks, follow these presentation schema standards for Power BI and Microsoft Fabric:

### A. Report-Specific Presentation Facts (Gold)
* **Best Practice**: **Yes, it is an absolute best practice to maintain a dedicated presentation schema (fact table) tailored to each specific report or business domain.**
* **Rule**: 
  * Do not attempt to merge distinct business domains (e.g., ServiceNow Work Orders, TechOne Supplier Invoices, and Property Assets) into a single monolithic "master fact" table.
  * Specialized, domain-focused Gold fact tables (e.g., `wo.gold_wo_servicenow_event_fact` and a separate `vac.fact_vacancy_day_vic`) keep facts compact, eliminate hundreds of wide `Null` columns, and keep DAX measures straightforward, maintainable, and high-performing.

### B. Single-Schema Domain Encapsulation
* **Best Practice**: **To guarantee maximum cohesion, security, and simplicity, all tables required by a specific report (including conformed dimensions, slicers, and rules tables) must be encapsulated under the exact same report-specific schema namespace (e.g., `wo` or `vac`).**
* **Rule**:
  * Keep all supporting dimensions (e.g., `dim_supplier`, `dim_fin_period`) in the same database schema namespace as the main facts and slicers for that report.
  * This keeps the reporting domain self-contained, makes schema-level permissions simple to enforce, and allows visual developers to connect to and fetch their entire model from a single namespace.

### C. Isolated Parameter & Slicer Tables
* **Best Practice**: Parameter tables used for disconnected slicers must be **isolated to each specific reporting model**.
* **Rule**:
  * Slicer tables (e.g., `slicer_fin_year`, `slicer_report_date`) supply inputs parsed directly inside DAX measures. Keep these slicers dedicated to their specific report workspace to avoid logical cross-filtering pollution, parameter bleeding, and visual bugs.

### D. Database Hygiene & Schema Cleanup Rules
* **Best Practice**: Keep your presentation lakehouse clean by aggressively dropping staging leftovers, legacy tables, and temporary files.
* **Rule**:
  * **Retire Legacy Tables**: When a table is replaced by a newer model (e.g., replacing `gold_fact_work_orders` with `gold_wo_servicenow_event_fact`), drop the legacy table immediately to prevent developers from binding reports to outdated logic.
  * **Drop Staging Leftovers**: Temporary tables created during migrations or test runs (e.g., tables prefixed with `_` like `_end_date`, `_start_date` or legacy lookup tests like `dim_budget_category`) must be dropped immediately.
  * **Audit Dependencies**: Before dropping a table, cross-reference it against active reporting documentation (e.g., conformed dimensions like `dim_date` supporting multiple reporting areas like Vacancy or Smoke Alarms must be preserved).
