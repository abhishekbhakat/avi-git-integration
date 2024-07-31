from datetime import timedelta
from typing import Any, Optional

from airflow.exceptions import AirflowTimetableInvalid
from airflow.plugins_manager import AirflowPlugin
from airflow.timetables.base import DagRunInfo, DataInterval, TimeRestriction, Timetable
from croniter import croniter
from pendulum import DateTime, now, timezone, timezones


class MultiCronTimetable(Timetable):
    def __init__(
        self,
        cron_list: list[str],
        timezone: str,
        overlap_strategy: str = "earliest",
        description: Optional[str] = None,
    ):
        self.cron_list = cron_list
        self.timezone = timezone
        self.overlap_strategy = overlap_strategy
        self.description = description

        # Validate inputs
        self.validate()

    def serialize(self) -> dict[str, Any]:
        return {
            "cron_list": self.cron_list,
            "timezone": self.timezone,
            "overlap_strategy": self.overlap_strategy,
            "description": self.description
        }

    @classmethod
    def deserialize(cls, value: dict[str, Any]) -> Timetable:
        return cls(
            value["cron_list"], 
            value["timezone"],
            value["overlap_strategy"],
            value["description"]    
        )

    @property
    def summary(self) -> str:
        return self.description or str(self.cron_list)

    def infer_manual_data_interval(self, run_after: DateTime) -> DataInterval:
        start = run_after.subtract(milliseconds=1)
        return DataInterval(start=start, end=run_after)

    def next_dagrun_info(
        self,
        *,
        last_automated_data_interval: DataInterval | None,
        restriction: TimeRestriction,
    ) -> DagRunInfo | None:
        tz = timezone(self.timezone)

        if last_automated_data_interval is None:
            next_start_utc = restriction.earliest or now(tz="UTC")
        else:
            next_start_utc = last_automated_data_interval.end

        if restriction.latest and next_start_utc > restriction.latest:
            return None

        next_start_tz = tz.convert(next_start_utc)

        # Find the next run time for each cron expression
        next_times = [
            croniter(expr, next_start_tz).get_next(DateTime)
            for expr in self.cron_list
        ]

        # Apply overlap strategy
        if self.overlap_strategy == "earliest":
            next_end_tz = min(next_times)
        elif self.overlap_strategy == "latest":
            next_end_tz = max(next_times)
        else:  # merge
            next_end_tz = min(next_times)
            for time in next_times:
                if time - next_end_tz <= timedelta(minutes=1):  # merge if within 1 minute
                    next_end_tz = max(next_end_tz, time)

        # Handle DST transitions
        if next_end_tz.fold != next_start_tz.fold:
            # Adjust for DST change
            dst_delta = tz.convert(next_end_tz) - tz.convert(next_start_tz)
            next_end_tz = next_start_tz + dst_delta

        return DagRunInfo.interval(start=next_start_tz, end=next_end_tz)

    def validate(self) -> None:
        if not self.cron_list:
            raise AirflowTimetableInvalid("Cron list cannot be empty")

        if not all(croniter.is_valid(cron) for cron in self.cron_list):
            raise AirflowTimetableInvalid(f"Invalid cron schedule(s): {self.cron_list}")

        if not all(len(cron.split()) == 5 for cron in self.cron_list):
            raise AirflowTimetableInvalid("All cron expressions must be in 5-part format")

        if self.overlap_strategy not in ["earliest", "latest", "merge"]:
            raise AirflowTimetableInvalid(f"Invalid overlap strategy: {self.overlap_strategy}")

        if self.timezone not in timezones():
            raise AirflowTimetableInvalid(f"Timezone `{self.timezone}` is not a valid pendulum timezone")

    def check_schedules_overlap(self) -> bool:
        # This method is now informational only, as overlaps are handled by the overlap_strategy
        all_times = set()
        for cron in self.cron_list:
            iter_time = croniter(cron, now())
            times = set(iter_time.all_next(DateTime, 24))  # Check next 24 occurrences
            if all_times.intersection(times):
                return True
            all_times.update(times)
        return False


class MultiCronTimetablePlugin(AirflowPlugin):
    name = "multi_cron_timetable_plugin"
    timetables = [MultiCronTimetable]