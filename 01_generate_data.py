"""
Step 1: Generate a SYNTHETIC HR dataset (no real employee data).

Creates three raw CSV files and then injects realistic data quality errors
(duplicates, missing values, invalid dates, inconsistent names, broken
manager links) so the validation step in 02_build_database_and_checks.py has
something to find.

Run:  python python/01_generate_data.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)
RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

N_EMPLOYEES = 600

FIRST = ["Anna", "Lukas", "Mia", "Jonas", "Lea", "Felix", "Sophie", "Paul", "Emma", "Noah",
         "Hannah", "Ben", "Clara", "Max", "Laura", "Tim", "Julia", "Leon", "Nina", "David",
         "Sara", "Tom", "Eva", "Jan", "Lina", "Erik", "Maria", "Finn", "Ida", "Omar"]
LAST = ["Meyer", "Schmidt", "Fischer", "Weber", "Wagner", "Becker", "Hoffmann", "Koch",
        "Richter", "Klein", "Wolf", "Neumann", "Schwarz", "Zimmermann", "Braun", "Krueger",
        "Hartmann", "Lange", "Werner", "Krause", "Lehmann", "Maier", "Huber", "Peters"]

DEPARTMENTS = [
    (1, "Trading"), (2, "Operations"), (3, "Finance"), (4, "IT"), (5, "Human Resources"),
    (6, "Legal"), (7, "Logistics"), (8, "Sales"), (9, "Sustainability"), (10, "Procurement"),
]
LOCATIONS = [
    (1, "Hamburg", "Germany"), (2, "Berlin", "Germany"), (3, "Rotterdam", "Netherlands"),
    (4, "Houston", "USA"), (5, "Singapore", "Singapore"),
]
JOB_LEVELS = ["Junior", "Professional", "Senior", "Lead", "Manager", "Director"]
STATUSES = ["Active", "Terminated", "On Leave"]


def rand_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


# ---------- Clean base data ----------
rows = []
for i in range(1, N_EMPLOYEES + 1):
    first, last = random.choice(FIRST), random.choice(LAST)
    hire = rand_date(date(2012, 1, 1), date(2026, 8, 31))
    status = random.choices(STATUSES, weights=[82, 15, 3])[0]
    term = ""
    if status == "Terminated":
        term_d = hire + timedelta(days=random.randint(120, 2500))
        term_d = min(term_d, date(2026, 9, 30))
        if term_d <= hire:
            term_d = hire + timedelta(days=200)
        term = term_d.isoformat()
    dept_id = random.choice(DEPARTMENTS)[0]
    rows.append({
        "employee_id": f"E{1000 + i}",
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}{i}@example-company.com",
        "department_id": dept_id,
        "location_id": random.choices([l[0] for l in LOCATIONS], weights=[50, 15, 12, 13, 10])[0],
        "job_level": random.choices(JOB_LEVELS, weights=[20, 30, 25, 12, 10, 3])[0],
        "manager_id": "",
        "hire_date": hire.isoformat(),
        "termination_date": term,
        "employment_status": status,
        "salary_band": random.choice(["B1", "B2", "B3", "B4", "B5"]),
    })

emp = pd.DataFrame(rows)
emp["department_id"] = emp["department_id"].astype(str)
emp["location_id"] = emp["location_id"].astype(str)

# Assign managers: each employee reports to someone earlier in the list (valid hierarchy)
ids = emp["employee_id"].tolist()
for idx in range(10, len(emp)):
    emp.loc[idx, "manager_id"] = random.choice(ids[: max(10, idx // 3)])

dept = pd.DataFrame(DEPARTMENTS, columns=["department_id", "department_name"])
loc = pd.DataFrame(LOCATIONS, columns=["location_id", "city", "country"])

# ---------- Inject data quality errors ----------
def pick(n, exclude=()):
    pool = [i for i in range(len(emp)) if i not in exclude]
    return random.sample(pool, n)

used = set()

# 1) Missing email (25)
for i in (idx := pick(25, used)):
    emp.loc[i, "email"] = ""
used |= set(idx)

# 2) Missing hire date (12)
for i in (idx := pick(12, used)):
    emp.loc[i, "hire_date"] = ""
used |= set(idx)

# 3) Hire date in the future (10)
for i in (idx := pick(10, used)):
    emp.loc[i, "hire_date"] = (date(2027, 1, 1) + timedelta(days=random.randint(30, 600))).isoformat()
used |= set(idx)

# 4) Termination before hire date (10)
for i in (idx := pick(10, used)):
    emp.loc[i, "employment_status"] = "Terminated"
    emp.loc[i, "hire_date"] = "2020-06-15"
    emp.loc[i, "termination_date"] = "2019-03-01"
used |= set(idx)

# 5) Active employee with a termination date (12)
for i in (idx := pick(12, used)):
    emp.loc[i, "employment_status"] = "Active"
    emp.loc[i, "termination_date"] = "2024-11-30"
used |= set(idx)

# 6) Terminated employee without termination date (10)
for i in (idx := pick(10, used)):
    emp.loc[i, "employment_status"] = "Terminated"
    emp.loc[i, "termination_date"] = ""
used |= set(idx)

# 7) Orphan manager id (manager does not exist) (15)
for i in (idx := pick(15, used)):
    emp.loc[i, "manager_id"] = f"E{random.randint(9000, 9999)}"
used |= set(idx)

# 8) Employee is their own manager (6)
for i in (idx := pick(6, used)):
    emp.loc[i, "manager_id"] = emp.loc[i, "employee_id"]
used |= set(idx)

# 9) Invalid department id (not in departments table) (8)
for i in (idx := pick(8, used)):
    emp.loc[i, "department_id"] = str(random.choice([0, 11, 99]))
used |= set(idx)

# 10) Missing department id (10)
for i in (idx := pick(10, used)):
    emp.loc[i, "department_id"] = ""
used |= set(idx)

# 11) Inconsistent job level spelling (20)
bad_levels = {"Senior": ["senior", "Sr.", "SENIOR"], "Manager": ["manager", "Mgr"],
              "Junior": ["junior", "Jr."], "Lead": ["lead", "Team Lead"]}
cands = [i for i in range(len(emp)) if emp.loc[i, "job_level"] in bad_levels and i not in used]
for i in random.sample(cands, 20):
    emp.loc[i, "job_level"] = random.choice(bad_levels[emp.loc[i, "job_level"]])
    used.add(i)

# 12) Invalid email format (missing @) (10)
for i in (idx := pick(10, used)):
    emp.loc[i, "email"] = emp.loc[i, "email"].replace("@", "_at_") or "no-email"
used |= set(idx)

# 13) Duplicate employee records (same person, new row) (15)
dups = emp.sample(15, random_state=7).copy()
dups["employee_id"] = [f"E{2000 + k}" for k in range(len(dups))]  # new id, same person
emp = pd.concat([emp, dups], ignore_index=True)

# 14) Duplicate employee_id (exact key duplicate) (5)
key_dups = emp.sample(5, random_state=11).copy()
emp = pd.concat([emp, key_dups], ignore_index=True)

emp = emp.sample(frac=1, random_state=3).reset_index(drop=True)

emp.to_csv(RAW / "employees_raw.csv", index=False)
dept.to_csv(RAW / "departments.csv", index=False)
loc.to_csv(RAW / "locations.csv", index=False)

print(f"employees_raw.csv : {len(emp)} rows")
print(f"departments.csv   : {len(dept)} rows")
print(f"locations.csv     : {len(loc)} rows")
