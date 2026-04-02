-- Vacancy Reporting VIC
-- Fabric SQL maintenance script for vacancy rule parameters

-- 1. Review the current active configuration
SELECT
    rule_name,
    offset_days,
    is_active,
    effective_from,
    comment,
    updated_by,
    updated_at
FROM vacancy_reporting.cfg_vacancy_rule_parameters
WHERE is_active = true
ORDER BY rule_name, effective_from DESC, updated_at DESC;


-- 2. Review the latest active row per rule
WITH ranked AS (
    SELECT
        rule_name,
        offset_days,
        is_active,
        effective_from,
        comment,
        updated_by,
        updated_at,
        ROW_NUMBER() OVER (
            PARTITION BY rule_name
            ORDER BY effective_from DESC, updated_at DESC
        ) AS rn
    FROM vacancy_reporting.cfg_vacancy_rule_parameters
    WHERE is_active = true
)
SELECT
    rule_name,
    offset_days,
    effective_from,
    comment,
    updated_by,
    updated_at
FROM ranked
WHERE rn = 1
ORDER BY rule_name;


-- 3. Insert the default rule set if the table is empty
INSERT INTO vacancy_reporting.cfg_vacancy_rule_parameters
(
    rule_name,
    offset_days,
    is_active,
    effective_from,
    comment,
    updated_by,
    updated_at
)
SELECT *
FROM (
    SELECT 'tenancy_end_to_vacancy_start', 1, true, CAST('1900-01-01' AS DATE), 'Workbook logic: vacancy start is tenancy end plus one day.', 'fabric_admin', CURRENT_TIMESTAMP()
    UNION ALL
    SELECT 'next_tenancy_start_to_vacancy_end', -1, true, CAST('1900-01-01' AS DATE), 'Workbook logic: vacancy inclusive end is next tenancy start minus one day.', 'fabric_admin', CURRENT_TIMESTAMP()
    UNION ALL
    SELECT 'property_start_to_vacancy_start', 0, true, CAST('1900-01-01' AS DATE), 'Usually zero. Change only if property start dates need the same correction.', 'fabric_admin', CURRENT_TIMESTAMP()
    UNION ALL
    SELECT 'property_source_date_offset', 0, true, CAST('1900-01-01' AS DATE), 'Optional raw source date shift for the Property table.', 'fabric_admin', CURRENT_TIMESTAMP()
    UNION ALL
    SELECT 'tenancy_source_date_offset', 0, true, CAST('1900-01-01' AS DATE), 'Optional raw source date shift for the Tenancy table.', 'fabric_admin', CURRENT_TIMESTAMP()
    UNION ALL
    SELECT 'void_source_date_offset', 0, true, CAST('1900-01-01' AS DATE), 'Optional raw source date shift for the Void table.', 'fabric_admin', CURRENT_TIMESTAMP()
    UNION ALL
    SELECT 'keys_source_date_offset', 0, true, CAST('1900-01-01' AS DATE), 'Optional raw source date shift for the Keys table.', 'fabric_admin', CURRENT_TIMESTAMP()
) s
WHERE NOT EXISTS (
    SELECT 1
    FROM vacancy_reporting.cfg_vacancy_rule_parameters
);


-- 4. Template: replace one active rule value
-- Example below updates tenancy_end_to_vacancy_start to 1.

UPDATE vacancy_reporting.cfg_vacancy_rule_parameters
SET is_active = false
WHERE rule_name = 'tenancy_end_to_vacancy_start'
  AND is_active = true;

INSERT INTO vacancy_reporting.cfg_vacancy_rule_parameters
(
    rule_name,
    offset_days,
    is_active,
    effective_from,
    comment,
    updated_by,
    updated_at
)
VALUES
(
    'tenancy_end_to_vacancy_start',
    1,
    true,
    CURRENT_DATE(),
    'Server is one day behind AU business date.',
    'fabric_admin',
    CURRENT_TIMESTAMP()
);


-- 5. Template: replace multiple rules together in one controlled change
-- Adjust the values before running.

UPDATE vacancy_reporting.cfg_vacancy_rule_parameters
SET is_active = false
WHERE rule_name IN (
    'tenancy_end_to_vacancy_start',
    'next_tenancy_start_to_vacancy_end',
    'property_start_to_vacancy_start'
)
  AND is_active = true;

INSERT INTO vacancy_reporting.cfg_vacancy_rule_parameters
(
    rule_name,
    offset_days,
    is_active,
    effective_from,
    comment,
    updated_by,
    updated_at
)
VALUES
(
    'tenancy_end_to_vacancy_start',
    1,
    true,
    CURRENT_DATE(),
    'Boundary rule update.',
    'fabric_admin',
    CURRENT_TIMESTAMP()
),
(
    'next_tenancy_start_to_vacancy_end',
    -1,
    true,
    CURRENT_DATE(),
    'Boundary rule update.',
    'fabric_admin',
    CURRENT_TIMESTAMP()
),
(
    'property_start_to_vacancy_start',
    0,
    true,
    CURRENT_DATE(),
    'Boundary rule update.',
    'fabric_admin',
    CURRENT_TIMESTAMP()
);


-- 6. After changing parameters:
--    1) rerun the notebook
--    2) refresh the semantic model
--    3) validate the Config page in the report
