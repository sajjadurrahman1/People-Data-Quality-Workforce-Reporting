"""
Step 2: Load raw HR data into SQLite, run the SQL data quality checks,
apply safe automated fixes, re-run the checks, and write the outputs
that feed the Power BI report.

Outputs
  data/people_data.db               SQLite database (raw + clean tables)
  data/clean/employees_clean.csv    Cleaned employees + issue flags  -> Power BI
  data/clean/departments.csv        Dimension table                  -> Power BI
  data/clean/locations.csv          Dimension table                  -> Power BI
  output/dq_check_summary.csv       One row per check (before / after)
  output/dq_score_summary.csv       Headline data quality score
  output/issue_log.csv              One row per issue, with owner + status

Run:  python python/02_run_quality_checks.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN, OUT = ROOT / "data" / "raw", ROOT / "data" / "clean", ROOT / "output"
CLEAN.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

REFERENCE_DATE = "2026-10-13"   # "today" for date-validity checks
AUTO_FIXED = {"DQ04", "DQ05", "DQ08"}   # issues the script resolves safely

JOB_LEVEL_MAP = {
    "senior": "Senior", "sr.": "Senior", "junior": "Junior", "jr.": "Junior",
    "manager": "Manager", "mgr": "Manager", "lead": "Lead", "team lead": "Lead",
    "professional": "Professional", "director": "Director",
}

# ---------------------------------------------------------------- load
read = lambda f: pd.read_csv(RAW / f, dtype=str, keep_default_na=False)
emp_raw = read("employees_raw.csv")
dept = read("departments.csv")
loc = read("locations.csv")

con = sqlite3.connect(ROOT / "data" / "people_data.db")
emp_raw.to_sql("employees_raw", con, if_exists="replace", index=False)
dept.to_sql("departments", con, if_exists="replace", index=False)
loc.to_sql("locations", con, if_exists="replace", index=False)


# ---------------------------------------------------------------- parse SQL
def parse_checks(path: Path):
    text = path.read_text()
    pattern = re.compile(r"-- CHECK:\s*(.+?)\n(.*?)(?=\n-- CHECK:|\Z)", re.S)
    checks = []
    for header, body in pattern.findall(text):
        cid, dim, sev, desc, owner = [p.strip() for p in header.split("|")]
        sql = body.strip().rstrip(";")
        checks.append(dict(id=cid, dimension=dim, severity=sev,
                           description=desc, owner=owner, sql=sql))
    return checks


CHECKS = parse_checks(ROOT / "sql" / "quality_checks.sql")


def run_checks(table: str) -> pd.DataFrame:
    """Return one row per (check, failing employee_id)."""
    frames = []
    for c in CHECKS:
        sql = c["sql"].format(table=table, reference_date=REFERENCE_DATE)
        ids = pd.read_sql_query(sql, con)["employee_id"].tolist()
        for emp_id in ids:
            frames.append({"check_id": c["id"], "employee_id": emp_id})
    return pd.DataFrame(frames, columns=["check_id", "employee_id"])


# ---------------------------------------------------------------- BEFORE
issues_raw = run_checks("employees_raw")
total_raw = emp_raw["employee_id"].nunique()
bad_raw = issues_raw["employee_id"].nunique()

# ---------------------------------------------------------------- safe fixes
clean = emp_raw.copy()
clean = clean.apply(lambda col: col.str.strip())
# DQ08: standardise job level spelling
clean["job_level"] = clean["job_level"].apply(
    lambda v: JOB_LEVEL_MAP.get(v.lower(), v))
# DQ04: drop exact duplicate rows
clean = clean.drop_duplicates()
# DQ05: drop probable duplicate persons (keep the lowest employee_id)
key = ["first_name", "last_name", "hire_date", "department_id"]
has_date = clean["hire_date"] != ""
dupe_mask = has_date & clean.duplicated(subset=key, keep=False)
keep_ids = (clean[dupe_mask].sort_values("employee_id")
            .drop_duplicates(subset=key, keep="first")["employee_id"])
drop_ids = clean[dupe_mask & ~clean["employee_id"].isin(keep_ids)]["employee_id"]
clean = clean[~clean["employee_id"].isin(drop_ids)].reset_index(drop=True)

clean.to_sql("employees_clean", con, if_exists="replace", index=False)

# ---------------------------------------------------------------- AFTER
issues_clean = run_checks("employees_clean")
total_clean = clean["employee_id"].nunique()
bad_clean = issues_clean["employee_id"].nunique()

# ---------------------------------------------------------------- summary per check
meta = pd.DataFrame(CHECKS).drop(columns="sql")
raw_counts = issues_raw.groupby("check_id")["employee_id"].nunique()
clean_counts = issues_clean.groupby("check_id")["employee_id"].nunique()

summary = meta.copy()
summary["failed_records_before"] = summary["id"].map(raw_counts).fillna(0).astype(int)
summary["failed_records_after"] = summary["id"].map(clean_counts).fillna(0).astype(int)
summary["pass_rate_before_pct"] = ((1 - summary["failed_records_before"] / total_raw) * 100).round(1)
summary["pass_rate_after_pct"] = ((1 - summary["failed_records_after"] / total_clean) * 100).round(1)
summary["resolution"] = summary["id"].apply(
    lambda i: "Auto-fixed by script" if i in AUTO_FIXED else "Sent to data owner for review")
summary = summary.rename(columns={"id": "check_id"})
summary.to_csv(OUT / "dq_check_summary.csv", index=False)

# ---------------------------------------------------------------- headline score
score = pd.DataFrame([
    {"stage": "Before cleaning", "total_records": total_raw,
     "records_with_issues": bad_raw,
     "dq_score_pct": round((1 - bad_raw / total_raw) * 100, 1)},
    {"stage": "After automated fixes", "total_records": total_clean,
     "records_with_issues": bad_clean,
     "dq_score_pct": round((1 - bad_clean / total_clean) * 100, 1)},
])
score.to_csv(OUT / "dq_score_summary.csv", index=False)

# ---------------------------------------------------------------- issue log
log = issues_raw.merge(meta, left_on="check_id", right_on="id").drop(columns="id")
log = log.drop_duplicates(subset=["check_id", "employee_id"])
log["status"] = log["check_id"].apply(
    lambda i: "Resolved (auto-fix)" if i in AUTO_FIXED else "Open - owner review")
log["raised_date"] = REFERENCE_DATE
log = log.sort_values(["status", "severity", "check_id", "employee_id"]).reset_index(drop=True)
log.insert(0, "issue_id", [f"ISS-{n:04d}" for n in range(1, len(log) + 1)])
log = log[["issue_id", "employee_id", "check_id", "dimension", "severity",
           "description", "owner", "status", "raised_date"]]
log.to_csv(OUT / "issue_log.csv", index=False)

# ---------------------------------------------------------------- Power BI feed
flag = issues_clean.groupby("employee_id")["check_id"].agg(
    issue_count="count", issue_codes=lambda s: ", ".join(sorted(s))).reset_index()
final = clean.merge(flag, on="employee_id", how="left")
final["issue_count"] = final["issue_count"].fillna(0).astype(int)
final["issue_codes"] = final["issue_codes"].fillna("")
final["dq_status"] = final["issue_count"].apply(lambda n: "Clean" if n == 0 else "Needs review")
final.to_csv(CLEAN / "employees_clean.csv", index=False)
dept.to_csv(CLEAN / "departments.csv", index=False)
loc.to_csv(CLEAN / "locations.csv", index=False)

con.close()

# ---------------------------------------------------------------- print
print("=== DATA QUALITY SCORE ===")
print(score.to_string(index=False))
print("\n=== CHECK SUMMARY ===")
print(summary[["check_id", "dimension", "severity", "failed_records_before",
               "failed_records_after", "resolution"]].to_string(index=False))
print(f"\nIssue log rows: {len(log)}  |  Open: {(log['status'] == 'Open - owner review').sum()}")
