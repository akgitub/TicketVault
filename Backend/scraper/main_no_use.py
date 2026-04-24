import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper.scrapers.bookmyshow import BookMyShowScraper
from scraper.scrapers.district import DistrictScraper


async def run_all():
    print("[Scraper] Starting run...")
    await BookMyShowScraper().run()
    await DistrictScraper().run()
    print("[Scraper] Run complete.")


async def main():
    await run_all()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        lambda: asyncio.create_task(run_all()),
        "interval",
        hours=6,
    )
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
