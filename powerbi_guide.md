# Power BI Build Guide (about 2 hours)

The Power BI file (.pbix) is the one part of this project you build yourself, so that the work and the screenshots are really yours.

## 1. Load the data (15 min)

1. Open Power BI Desktop and choose **Get data > Text/CSV**.
2. Load these three files from `data/clean/`: `employees_clean.csv`, `departments.csv`, `locations.csv`.
3. Also load `output/dq_check_summary.csv`, `output/dq_score_summary.csv`, and `output/issue_log.csv`.
4. In Power Query, set `hire_date` and `termination_date` to type **Date**, and `department_id` and `location_id` to **Text** in all tables.

## 2. Create relationships (5 min)

In **Model view**, connect:

- `employees_clean[department_id]` to `departments[department_id]` (many to one)
- `employees_clean[location_id]` to `locations[location_id]` (many to one)

Records with a missing or invalid department will show as blank. That is expected and is part of the story.

## 3. Add the DAX measures (20 min)

Copy the measures from `docs/dax_measures.md` into a table called `_Measures`.

## 4. Page 1: Workforce overview (30 min)

| Visual | Fields |
|---|---|
| 4 KPI cards | Active Headcount, Attrition Rate, Average Tenure (Years), Hires This Year |
| Bar chart | Active Headcount by department_name |
| Column chart | Active Headcount by city |
| Line chart | Hires by hire year |
| Donut or bar | Active Headcount by job_level |
| Slicers | department_name, city, employment_status |

## 5. Page 2: Data quality (30 min)

| Visual | Fields |
|---|---|
| KPI cards | DQ Score, Records with Issues, Open Issues, Open High Severity |
| Bar chart | `dq_check_summary`: failed_records_before and failed_records_after by check_id |
| Stacked bar | Open issues by dimension and severity (from `issue_log`) |
| Table | `issue_log`: issue_id, employee_id, check_id, severity, owner, status |
| Slicers | owner, severity, status |

## 6. Finish (20 min)

1. Use one color theme, short titles, and no more than 8 visuals per page.
2. Add a text box on each page with one sentence on what the page shows.
3. Take screenshots of both pages and save them in a `screenshots/` folder in the repo.
4. Save the .pbix file in the repo, or note in the README that it is available on request.
