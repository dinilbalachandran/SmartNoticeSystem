import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
import time
from datetime import datetime

from scraper.scraper import process_notices
from database.database import (
    get_all_notice_sources,
    update_source_last_checked
)


def start_scheduler():

    print()
    print("===========================================")
    print("SmartNotice Scheduler Started")
    print("===========================================")

    waiting_line_active = False

    while True:

        sources = get_all_notice_sources()
        min_remaining = None

        for source in sources:

            if source["status"] != "Active":
                continue

            interval = source["check_interval"]
            last_checked = source["last_checked"]

            should_check = False
            remaining = interval

            if last_checked is None:
                should_check = True
            else:
                last_time = datetime.fromisoformat(last_checked)
                elapsed = (datetime.now() - last_time).total_seconds()

                if elapsed >= interval:
                    should_check = True
                else:
                    remaining = int(interval - elapsed)

            if should_check:
                if waiting_line_active:
                    print()
                    waiting_line_active = False

                print()
                print("-------------------------------------------")
                print(f"Checking source: {source['website_name']}")
                print(f"Check interval: {interval} seconds")

                try:
                    process_notices()
                    update_source_last_checked(source["id"])

                    print(f"Last checked updated for {source['website_name']}")
                    print()
                    remaining = interval

                except Exception as error:
                    print()
                    print("Scheduler error:")
                    print(error)

            if min_remaining is None or remaining < min_remaining:
                min_remaining = remaining

        if min_remaining is not None:
            print(
                f"\rWaiting for next check cycle... [{min_remaining}s remaining].",
                end="",
                flush=True
            )
            waiting_line_active = True

        time.sleep(1)


if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")