-- =====================================================================
-- HR DATA QUALITY CHECKS
-- Each check returns the employee_id of every record that FAILS the rule.
-- The placeholder {table} is replaced by the Python runner so the same
-- checks run on both the raw table and the cleaned table.
--
-- Each query is preceded by a tag line with five fields separated by pipes:
-- id, dimension, severity, description, data owner
-- =====================================================================

-- CHECK: DQ01 | Completeness | Medium | Employee email is missing | HR Operations
SELECT employee_id FROM {table}
WHERE TRIM(email) = '';

-- CHECK: DQ02 | Completeness | High | Hire date is missing | HR Operations
SELECT employee_id FROM {table}
WHERE TRIM(hire_date) = '';

-- CHECK: DQ03 | Completeness | High | Department is missing | HR Systems
SELECT employee_id FROM {table}
WHERE TRIM(department_id) = '';

-- CHECK: DQ04 | Uniqueness | High | Duplicate employee_id (same key appears more than once) | HR Systems
SELECT employee_id FROM {table}
GROUP BY employee_id
HAVING COUNT(*) > 1;

-- CHECK: DQ05 | Uniqueness | High | Probable duplicate person (same name, hire date and department, different ID) | HR Systems
SELECT e.employee_id
FROM {table} e
JOIN (
    SELECT first_name, last_name, hire_date, department_id,
           MIN(employee_id) AS keep_id
    FROM {table}
    WHERE TRIM(hire_date) <> ''
    GROUP BY first_name, last_name, hire_date, department_id
    HAVING COUNT(DISTINCT employee_id) > 1
) d
  ON  e.first_name    = d.first_name
  AND e.last_name     = d.last_name
  AND e.hire_date     = d.hire_date
  AND e.department_id = d.department_id
WHERE e.employee_id <> d.keep_id;

-- CHECK: DQ06 | Validity | High | Hire date is in the future | HR Operations
SELECT employee_id FROM {table}
WHERE TRIM(hire_date) <> '' AND hire_date > '{reference_date}';

-- CHECK: DQ07 | Validity | Medium | Email format is invalid (no @ sign) | HR Operations
SELECT employee_id FROM {table}
WHERE TRIM(email) <> '' AND email NOT LIKE '%@%';

-- CHECK: DQ08 | Validity | Low | Job level is not a standard value | HR Systems
SELECT employee_id FROM {table}
WHERE job_level NOT IN ('Junior','Professional','Senior','Lead','Manager','Director');

-- CHECK: DQ09 | Consistency | High | Termination date is before hire date | HR Operations
SELECT employee_id FROM {table}
WHERE TRIM(termination_date) <> '' AND TRIM(hire_date) <> ''
  AND termination_date < hire_date;

-- CHECK: DQ10 | Consistency | High | Active / On Leave employee has a termination date | HR Operations
SELECT employee_id FROM {table}
WHERE employment_status IN ('Active','On Leave') AND TRIM(termination_date) <> '';

-- CHECK: DQ11 | Consistency | High | Terminated employee has no termination date | HR Operations
SELECT employee_id FROM {table}
WHERE employment_status = 'Terminated' AND TRIM(termination_date) = '';

-- CHECK: DQ12 | Integrity | Medium | Manager ID does not exist in the employee table | HR Systems
SELECT e.employee_id FROM {table} e
WHERE TRIM(e.manager_id) <> ''
  AND e.manager_id NOT IN (SELECT employee_id FROM {table});

-- CHECK: DQ13 | Integrity | Medium | Employee is listed as their own manager | HR Systems
SELECT employee_id FROM {table}
WHERE manager_id = employee_id;

-- CHECK: DQ14 | Integrity | High | Department ID does not exist in departments table | HR Systems
SELECT employee_id FROM {table}
WHERE TRIM(department_id) <> ''
  AND department_id NOT IN (SELECT department_id FROM departments);
