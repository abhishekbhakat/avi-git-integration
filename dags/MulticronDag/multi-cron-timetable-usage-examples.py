from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from multicron_timetable.timetable import MultiCronTimetable

doc_md = """
# MultiCronTimetable Overlap Strategies

The MultiCronTimetable in Airflow offers three strategies to handle overlapping schedules: Earliest, Latest, and Merge.

## Example Scenario

Assume a MultiCronTimetable with these cron expressions:
1. `"0 9 * * *"` (daily at 9:00 AM)
2. `"30 9 * * *"` (daily at 9:30 AM)
3. `"0 10 * * *"` (daily at 10:00 AM)

## Strategies

### 1. Earliest Strategy

- Triggers at the earliest scheduled time when there's an overlap
- Example DAG runs:
  1. 9:00 AM - 9:30 AM
  2. 9:30 AM - 10:00 AM
  3. 10:00 AM - Next Day 9:00 AM

Use when you want the DAG to run as soon as any schedule is due.

### 2. Latest Strategy

- Waits for the latest scheduled time when there's an overlap
- Example DAG runs:
  1. 9:00 AM - 9:30 AM
  2. 9:30 AM - 10:00 AM
  3. 10:00 AM - Next Day 9:00 AM

Use when you want to delay the DAG run until the last scheduled time.

### 3. Merge Strategy

- Combines nearby scheduled times into a single DAG run
- Example DAG runs:
  1. 9:00 AM - 10:00 AM (merging all three schedules)
  2. 10:00 AM - Next Day 9:00 AM

Use to reduce the number of DAG runs by combining closely timed schedules.

## Summary

- **Earliest**: Runs at first scheduled time
- **Latest**: Waits for last scheduled time
- **Merge**: Combines nearby schedules

Choose based on your DAG's timing requirements and resource constraints.
"""

# Example 1: Basic usage with default overlap strategy
timetable1 = MultiCronTimetable(
    cron_list=["0 9 * * 1-5", "0 12 * * 6-7"],
    timezone="America/New_York",
    description="Weekdays at 9 AM, Weekends at 12 PM"
)

with DAG(
    'example_dag_1',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 2, 1),
    schedule=timetable1,
    catchup=True,
    tags=['multi-cron-timetable'],
    doc_md=doc_md
) as dag1:
    EmptyOperator(task_id='task1')

# Example 2: Using 'latest' overlap strategy
timetable2 = MultiCronTimetable(
    cron_list=["*/15 9-17 * * 1-5", "0 * * * *"],
    timezone="Europe/London",
    overlap_strategy="latest",
    description="Every 15 mins during business hours, hourly otherwise"
)

with DAG(
    'example_dag_2',
    start_date=datetime(2023, 1, 1),
    schedule=timetable2,
    catchup=False,
    tags=['multi-cron-timetable'],
    doc_md=doc_md
) as dag2:
    EmptyOperator(task_id='task2')

# Example 3: Using 'merge' overlap strategy
timetable3 = MultiCronTimetable(
    cron_list=["0 9 * * *", "30 9 * * *", "0 10 * * *"],
    timezone="Asia/Tokyo",
    overlap_strategy="merge",
    description="Daily at 9:00, 9:30, and 10:00"
)

with DAG(
    'example_dag_3',
    start_date=datetime(2023, 1, 1),
    schedule=timetable3,
    catchup=False,
    tags=['multi-cron-timetable'],
    doc_md=doc_md
) as dag3:
    EmptyOperator(task_id='task3')
