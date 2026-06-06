from __future__ import annotations

import logging
import time
from collections.abc import Callable

try:
    import schedule
except ImportError:  # pragma: no cover - exercised only before dependencies are installed
    schedule = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class LocalScheduler:
    """Small schedule-based local runner."""

    def __init__(self, config: dict, daily_job: Callable[[], None]) -> None:
        self.config = config
        self.daily_job = daily_job

    def start(self) -> None:
        """Start the blocking local scheduler loop."""
        if schedule is None:
            raise RuntimeError("schedule is not installed. Run: pip install -r requirements.txt")

        daily_time = self.config.get("schedule", {}).get("daily_time", "08:00")
        schedule.every().day.at(daily_time).do(self._run_daily_job)
        logger.info("Scheduler started. Daily job time: %s", daily_time)

        while True:
            schedule.run_pending()
            time.sleep(30)

    def _run_daily_job(self) -> None:
        try:
            self.daily_job()
        except Exception:
            logger.exception("Scheduled daily job failed.")
