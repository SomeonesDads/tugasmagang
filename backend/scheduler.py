"""
scheduler.py
Standalone daily pipeline scheduler using APScheduler.

Use this if you want the pipeline to run independently of the API process.

Run with:
    python scheduler.py

The scheduler fires `daily_pipeline()` every day at the configured time
(default: 02:00 local time).  It also runs immediately on startup so you
don't have to wait until 2 AM on the first deploy.

To change the run time, set PIPELINE_HOUR and PIPELINE_MINUTE in .env:
    PIPELINE_HOUR=2
    PIPELINE_MINUTE=0
"""

import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import dotenv_values

from dailypipeline import daily_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
)
log = logging.getLogger(__name__)


def _run() -> None:
    """Wrapper so exceptions don't kill the scheduler process."""
    try:
        daily_pipeline()
    except Exception:
        log.exception("Pipeline run failed — will retry on next scheduled run")


def main() -> None:
    cfg  = dotenv_values(".env")
    hour = int(cfg.get("PIPELINE_HOUR",   2))
    minute = int(cfg.get("PIPELINE_MINUTE", 0))

    scheduler = BlockingScheduler()
    scheduler.add_job(
        _run,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="daily_pipeline",
        name="Daily ticket pipeline",
        misfire_grace_time=3600,   # if the job is missed by up to 1 h, still run it
        coalesce=True,             # if multiple runs were missed, only run once
    )

    # Graceful shutdown on Ctrl-C / SIGTERM
    def _shutdown(signum, frame):
        log.info("Shutdown signal received — stopping scheduler")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    log.info(f"Scheduler started — pipeline fires daily at {hour:02d}:{minute:02d}")
    log.info("Running pipeline immediately on startup...")
    _run()   # catch-up run so you don't wait until 2 AM on first deploy

    scheduler.start()


if __name__ == "__main__":
    main()
