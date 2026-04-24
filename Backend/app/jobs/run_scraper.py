# import asyncio
# from playwright.async_api import async_playwright
# from scraper.scrapers.bookmyshow import BookMyShowScraper
# from scraper.scrapers.district import DistrictScraper


# async def run():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()

#         bms = BookMyShowScraper()
#         district = DistrictScraper()

#         print("🔄 Running BookMyShow scraper...")
#         await bms.scrape(page)

#         print("🔄 Running District scraper...")
#         await district.scrape(page)

#         await browser.close()


# if __name__ == "__main__":
#     asyncio.run(run())

"""
Entry point used by: python -m app.jobs.run_scraper
Runs all scrapers once immediately.
"""
import asyncio
from scraper.main import run_all

if __name__ == "__main__":
    asyncio.run(run_all())
