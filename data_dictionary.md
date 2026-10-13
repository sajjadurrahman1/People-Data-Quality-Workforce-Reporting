# Data Dictionary

All data in this project is **synthetic**. No real employee information is used.

## employees_clean (main table)

| Field | Type | Description | Rules |
|---|---|---|---|
| employee_id | Text | Unique ID of the employee record (primary key) | Required, unique, format `E` + digits |
| first_name | Text | First name | Required |
| last_name | Text | Last name | Required |
| email | Text | Work email address | Required, must contain `@` |
| department_id | Text | Link to `departments.department_id` | Required, must exist in departments |
| location_id | Text | Link to `locations.location_id` | Required, must exist in locations |
| job_level | Text | Standard job level | One of: Junior, Professional, Senior, Lead, Manager, Director |
| manager_id | Text | `employee_id` of the line manager | Must exist in the employee table, cannot equal own ID |
| hire_date | Date (YYYY-MM-DD) | First working day | Required, cannot be in the future |
| termination_date | Date (YYYY-MM-DD) | Last working day | Only for terminated employees, cannot be before hire date |
| employment_status | Text | Current status | One of: Active, On Leave, Terminated |
| salary_band | Text | Salary band (no amounts stored) | B1 to B5 |
| issue_count | Integer | Number of open data quality issues for this record | Added by the quality script |
| issue_codes | Text | Check IDs that failed (for example `DQ02, DQ09`) | Added by the quality script |
| dq_status | Text | `Clean` or `Needs review` | Added by the quality script |

## departments

| Field | Description |
|---|---|
| department_id | Primary key |
| department_name | Name of the department |

## locations

| Field | Description |
|---|---|
| location_id | Primary key |
| city | City |
| country | Country |

## Output tables

| File | Purpose |
|---|---|
| output/dq_check_summary.csv | One row per check with failed records and pass rate before and after cleaning |
| output/dq_score_summary.csv | Overall data quality score before and after cleaning |
| output/issue_log.csv | One row per issue with severity, data owner, and status |
