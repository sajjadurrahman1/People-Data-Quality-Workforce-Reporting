# HR Data Governance Guideline

This guideline describes who owns which employee data, which standards the data must meet, and how errors are reported and fixed. It supports the data quality checks in `sql/quality_checks.sql`.

## 1. Purpose

Workforce reports are only useful when the underlying employee data is accurate, complete, and consistent. This guideline defines simple rules so that issues are found early, assigned to the right person, and tracked until they are closed.

## 2. Data quality dimensions

| Dimension | Meaning | Example check |
|---|---|---|
| Completeness | Required fields are filled | DQ02 Hire date is missing |
| Uniqueness | Each employee exists once | DQ04 Duplicate employee_id |
| Validity | Values follow the allowed format or list | DQ08 Job level is not a standard value |
| Consistency | Fields do not contradict each other | DQ09 Termination date before hire date |
| Integrity | References point to existing records | DQ12 Manager ID does not exist |

## 3. Data ownership

| Data area | Data owner | Responsibility |
|---|---|---|
| Hire date, termination date, employment status, email | HR Operations | Correct and complete entry at onboarding and offboarding |
| Employee ID, department, manager, job level | HR Systems | Structure and reference data stay consistent |
| Reports and dashboards | People Data & Analytics | Run checks, publish results, report issues to owners |

## 4. Data entry standards

1. Dates use the format YYYY-MM-DD.
2. Job levels use only the standard list in the data dictionary.
3. Every employee has exactly one record and one unique employee_id.
4. Every employee belongs to a department that exists in the department table.
5. A terminated employee always has a termination date. An active employee never has one.
6. A manager must be an existing employee and never the employee themselves.

## 5. Issue handling process

1. **Detect:** The quality script runs the checks and writes every failed record to `output/issue_log.csv`.
2. **Classify:** Each issue gets a severity (High, Medium, Low) and a data owner.
3. **Fix safely:** Issues with a clear safe fix (spelling of job levels, exact duplicates) are corrected by the script and logged as "Resolved (auto-fix)".
4. **Escalate:** All other issues get the status "Open - owner review" and are sent to the data owner with the employee ID and the rule that failed.
5. **Confirm:** After the owner corrects the source system, the checks run again. The issue closes when the record passes.

## 6. Severity rules

| Severity | Meaning | Target response |
|---|---|---|
| High | Affects headcount, attrition, or reporting accuracy | Within 3 working days |
| Medium | Affects contact or hierarchy data | Within 10 working days |
| Low | Formatting issue with a safe fix | Fixed automatically |

## 7. Data protection

Employee data is personal data. Reports use only the fields they need, salary amounts are not stored, and test data must be synthetic or anonymized.

## 8. Data quality score

DQ score = records with no open issues divided by total records, shown as a percentage. The score is calculated before and after cleaning, so the effect of the fixes is visible.
