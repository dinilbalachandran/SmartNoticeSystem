import time
from datetime import datetime, timezone

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

    while True:

        sources = get_all_notice_sources()

        for source in sources:

            if source["status"] != "Active":
                continue

            interval = source["check_interval"]

            last_checked = source["last_checked"]

            should_check = False

            if last_checked is None:
                should_check = True

            else:

                last_time = datetime.fromisoformat(
                    last_checked
                )

                elapsed = (
                    datetime.now(timezone.utc).replace(tzinfo=None) - last_time
                ).total_seconds()

                if elapsed >= interval:
                    should_check = True

            if should_check:

                print()
                print("-------------------------------------------")
                print(
                    f"Checking source: "
                    f"{source['website_name']}"
                )
                print(
                    f"Check interval: "
                    f"{interval} seconds"
                )

                try:

                    process_notices()

                    update_source_last_checked(
                        source["id"]
                    )

                    print(
                        f"Last checked updated for "
                        f"{source['website_name']}"
                    )

                except Exception as error:

                    print()
                    print("Scheduler error:")
                    print(error)

        time.sleep(10)


if __name__ == "__main__":
    start_scheduler()