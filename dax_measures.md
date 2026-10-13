# DAX Measures

Create a blank table called `_Measures` and add these measures. Table and column names match the CSV files.

## Workforce measures

```dax
Total Records = COUNTROWS ( employees_clean )
```

```dax
Active Headcount =
CALCULATE (
    COUNTROWS ( employees_clean ),
    employees_clean[employment_status] IN { "Active", "On Leave" }
)
```

```dax
Terminations =
CALCULATE (
    COUNTROWS ( employees_clean ),
    employees_clean[employment_status] = "Terminated"
)
```

```dax
Attrition Rate = DIVIDE ( [Terminations], [Total Records] )
```

```dax
Average Tenure (Years) =
AVERAGEX (
    FILTER ( employees_clean, NOT ISBLANK ( employees_clean[hire_date] ) ),
    DATEDIFF (
        employees_clean[hire_date],
        IF ( ISBLANK ( employees_clean[termination_date] ), TODAY (), employees_clean[termination_date] ),
        DAY
    ) / 365.25
)
```

```dax
Hires This Year =
CALCULATE (
    COUNTROWS ( employees_clean ),
    YEAR ( employees_clean[hire_date] ) = YEAR ( TODAY () )
)
```

## Data quality measures

```dax
Records with Issues =
CALCULATE ( COUNTROWS ( employees_clean ), employees_clean[issue_count] > 0 )
```

```dax
DQ Score = DIVIDE ( [Total Records] - [Records with Issues], [Total Records] )
```

```dax
Open Issues =
CALCULATE ( COUNTROWS ( issue_log ), issue_log[status] = "Open - owner review" )
```

```dax
Open High Severity =
CALCULATE (
    COUNTROWS ( issue_log ),
    issue_log[status] = "Open - owner review",
    issue_log[severity] = "High"
)
```

Format `Attrition Rate` and `DQ Score` as percentages, and `Average Tenure (Years)` with one decimal.

## Notes

- In the synthetic data the attrition rate is simply terminations divided by all records. In a real report you would divide by average headcount for a period.
- `hire_date` and `termination_date` must have the data type Date in Power Query before these measures work.
