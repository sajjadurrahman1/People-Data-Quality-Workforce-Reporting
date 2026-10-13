# People Data Quality & Workforce Reporting

An end-to-end HR data project. It checks the quality of employee data, fixes what can be fixed safely, tracks the remaining issues with data owners, and reports workforce KPIs in Power BI.

> **Data note:** All data is synthetic and created by `python/01_generate_data.py`. It contains no real employee information. Errors were added on purpose so the checks have something to find.

## Why this project

Workforce reports are only useful when the employee data behind them is accurate. This project shows the full process: find the errors, fix what is safe, hand the rest to the right owner, document the rules, and report the results.

## What it does

1. **Generates** a synthetic HR dataset (600 employees, 10 departments, 5 locations) with realistic errors.
2. **Validates** the data with 14 SQL checks across five quality dimensions: completeness, uniqueness, validity, consistency, and integrity.
3. **Cleans** what is safe to fix automatically (duplicates and job level spelling) and re-runs the checks.
4. **Logs** every issue with severity, data owner, and status.
5. **Documents** a data dictionary and a data governance guideline.
6. **Reports** workforce KPIs and data quality results in a two-page Power BI report.

## Results

| Stage | Records | Records with issues | Data quality score |
|---|---|---|---|
| Before cleaning | 615 | 168 | 72.7% |
| After automated fixes | 600 | 128 | 78.7% |

- 176 issues were logged in total.
- 41 were resolved automatically (duplicate records and job level spelling).
- 135 remain open for the data owner, because fixing them needs a decision (for example, which hire date is correct).

## Tools

SQL (SQLite) · Python (pandas) · Power BI (DAX, Power Query) · CSV/Excel · Markdown

## Project structure

```
python/01_generate_data.py          Creates synthetic raw data with injected errors
python/02_run_quality_checks.py     Loads SQLite, runs checks, applies fixes, writes outputs
sql/quality_checks.sql              The 14 data quality checks
data/raw/                           Raw input files
data/clean/                         Cleaned tables used by Power BI
data/people_data.db                 SQLite database (raw and clean tables)
output/dq_check_summary.csv         Pass rate per check, before and after
output/dq_score_summary.csv         Overall data quality score
output/issue_log.csv                One row per issue with owner and status
docs/data_dictionary.md             Fields, types, and rules
docs/data_governance.md             Ownership, standards, and issue process
docs/dax_measures.md                Power BI measures
docs/powerbi_guide.md               Report layout
```

## Data quality checks

| ID | Dimension | Check |
|---|---|---|
| DQ01 | Completeness | Email is missing |
| DQ02 | Completeness | Hire date is missing |
| DQ03 | Completeness | Department is missing |
| DQ04 | Uniqueness | Duplicate employee ID |
| DQ05 | Uniqueness | Probable duplicate person |
| DQ06 | Validity | Hire date is in the future |
| DQ07 | Validity | Email format is invalid |
| DQ08 | Validity | Job level is not a standard value |
| DQ09 | Consistency | Termination date is before hire date |
| DQ10 | Consistency | Active employee has a termination date |
| DQ11 | Consistency | Terminated employee has no termination date |
| DQ12 | Integrity | Manager ID does not exist |
| DQ13 | Integrity | Employee is their own manager |
| DQ14 | Integrity | Department ID does not exist |

## Issue handling

Issues with a safe fix are corrected by the script and logged as **Resolved (auto-fix)**. All other issues are logged as **Open - owner review** with the employee ID, the failed rule, the severity, and the responsible owner. See `docs/data_governance.md` for the full process.

## How to run

```bash
pip install pandas
python python/01_generate_data.py
python python/02_run_quality_checks.py
```

The scripts create the cleaned tables in `data/clean/` and the results in `output/`. Load these files into Power BI Desktop and follow `docs/powerbi_guide.md`.

## Power BI report

- **Page 1, Workforce overview:** active headcount, attrition rate, average tenure, hires, and breakdowns by department, location, and job level.
- **Page 2, Data quality:** data quality score, failed records per check before and after cleaning, and open issues by owner and severity.

<!-- Add your screenshots here, for example: -->
<!-- ![Workforce overview](screenshots/page1_workforce.png) -->
<!-- ![Data quality](screenshots/page2_data_quality.png) -->

## Possible next steps

- Schedule the checks so the score refreshes automatically.
- Add a Power Automate approval flow for data correction requests.
- Track the data quality score over time to show the trend.

## Author

Sajjadur Rahman · [LinkedIn](https://www.linkedin.com/in/sajjadur-rahman-7a30b6284/) · [Portfolio](https://sajjadurrahman1.github.io/Know_ME/)
