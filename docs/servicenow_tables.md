# ServiceNow Data Source Assessment & Scope Report

**Project**: VIC Vacancy Reporting (Fabric Implementation)  
**System of Record**: TechOne  
**ServiceNow Scope Status**: **Out of Scope (0 Tables Used)**

---

## 1. ServiceNow Table Inventory
There are **no ServiceNow tables** ingested, processed, or modeled in the VIC Vacancy Reporting data pipeline. 

All staging (Bronze), standardization (Silver), and analytical presentation (Gold) tables are built exclusively using TechOne source data.

| ServiceNow Table Name | Label / Description | Scope Status |
| :--- | :--- | :--- |
| *None* | No ServiceNow tables are used in this project. | **Out of Scope** |

---

## 2. Dotwalking (Relationship Traversals)
In ServiceNow, "dotwalking" refers to the process of referencing fields on related tables by traversing reference fields (e.g., `incident.caller_id.email`).

* **Dotwalks in Scope**: **None** (since no ServiceNow tables are utilized).
* **Join Logic**: All table relationships in the medallion pipeline are established via physical joins on TechOne primary keys (e.g., matching `Property.PROPERTYID` to `Tenancy.PROPID`, `Void.PROP_ID`, and `Keys.PARENT_ENGAGEMENT_ID`).

---

## 3. Actual System of Record (In-Scope Tables)
For management approval, the following tables from **TechOne** represent the entire data model footprint:

* **`Property`** (ingested as `Bronze_TechOne_Property` / `silver_techone_property`)
* **`Tenancy`** (ingested as `Bronze_TechOne_Tenancy` / `silver_techone_tenancy`)
* **`Void`** (ingested as `Bronze_TechOne_Void` / `silver_techone_void`)
* **`Keys`** (ingested as `Bronze_TechOne_Keys` / `silver_techone_keys`)
