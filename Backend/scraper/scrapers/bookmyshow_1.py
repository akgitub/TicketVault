import asyncio
import re
from datetime import datetime
from playwright.async_api import Page

from scraper.scrapers.base import BaseScraper
from scraper.config import BMS_CITY_MAP
from scraper.storage import get_city_id, upsert_event


class BookMyShowScraper(BaseScraper):
    source = "bookmyshow"
    BASE = "https://in.bookmyshow.com/explore/concerts-{city}"

    async def scrape(self, page: Page):
        for slug, canonical in BMS_CITY_MAP.items():
            url = self.BASE.format(city=slug)
            try:
                await self._scrape_city(page, url, canonical)
            except Exception as e:
                print(f"[BMS] Failed {slug}: {e}")
            await asyncio.sleep(4)

    async def _scrape_city(self, page: Page, url: str, canonical: str):
        city_id = get_city_id(canonical)
        if not city_id:
            print(f"[BMS] City not found in DB: {canonical}")
            return

        # 1. Navigate — networkidle lets JS finish rendering
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(5)

        # 2. Dismiss popups
        for dismiss_sel in [
            "text=Close", "text=CLOSE",
            "[aria-label='close']", "[aria-label='Close']",
            "button[class*='close']", "button[class*='Close']",
        ]:
            try:
                await page.click(dismiss_sel, timeout=2000)
                await asyncio.sleep(0.5)
            except Exception:
                pass

        # 3. Scroll progressively to trigger lazy-loaded cards
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(1.5)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # 4. Try multiple card selectors
        card_selectors = [
            "a[href*='/events/']",
            "[class*='EventCard'] a",
            "[class*='event-card'] a",
            "[class*='ShowCard'] a",
            "[class*='show-card'] a",
            "li[class*='event'] a",
            "div[class*='listing'] a",
        ]

        cards = []
        used_selector = None
        for sel in card_selectors:
            try:
                await page.wait_for_selector(sel, timeout=6000)
                found = await page.query_selector_all(sel)
                if found:
                    cards = found
                    used_selector = sel
                    break
            except Exception:
                continue

        if not cards:
            print(f"[BMS] No cards found for {canonical}")
            print(f"[BMS]   URL: {url}")
            print(f"[BMS]   Title: {await page.title()!r}")
            body = await page.inner_text("body")
            print(f"[BMS]   Body preview: {body[:300]!r}")
            return

        print(f"[BMS] {canonical}: {len(cards)} cards via '{used_selector}'")

        seen = set()
        for card in cards:
            try:
                # Name
                name_el = None
                for name_sel in ["h3","h2","h4",
                                  "[class*='title']","[class*='Title']",
                                  "[class*='name']","[class*='Name']",
                                  "strong","b"]:
                    name_el = await card.query_selector(name_sel)
                    if name_el:
                        break

                name_text = (await name_el.inner_text()).strip() if name_el else None
                if not name_text:
                    raw = (await card.inner_text()).strip()
                    name_text = raw.split("\n")[0].strip() if raw else None

                if not name_text or name_text in seen:
                    continue
                seen.add(name_text)

                # Image
                img_el = await card.query_selector("img")
                img_src = None
                if img_el:
                    img_src = (
                        await img_el.get_attribute("src") or
                        await img_el.get_attribute("data-src") or
                        await img_el.get_attribute("data-lazy-src")
                    )

                # Venue + Date from sub-elements
                all_sub = await card.query_selector_all(
                    "span, p, small, "
                    "div[class*='date'], div[class*='Date'], "
                    "div[class*='venue'], div[class*='Venue'], "
                    "div[class*='meta'], div[class*='info']"
                )
                texts = []
                for el in all_sub:
                    t = (await el.inner_text()).strip()
                    if t and 2 < len(t) < 150 and t != name_text:
                        texts.append(t)

                unique_texts: list[str] = []
                for t in texts:
                    if t not in unique_texts:
                        unique_texts.append(t)

                # Fallback: use all card lines
                if not unique_texts:
                    card_text = await card.inner_text()
                    unique_texts = [
                        line.strip()
                        for line in card_text.split("\n")
                        if line.strip() and line.strip() != name_text
                    ]

                venue_text, date_text = _extract_venue_date(unique_texts)
                parsed_date = _parse_date(date_text) if date_text else None
                if not parsed_date:
                    print(f"[BMS] Skipping '{name_text}' — bad date: {date_text!r}")
                    continue

                upsert_event({
                    "name":      name_text,
                    "venue":     venue_text or "TBD",
                    "city_id":   city_id,
                    "date":      parsed_date,
                    "image_url": img_src,
                    "source":    self.source,
                })
                print(f"[BMS] OK  {name_text[:40]:<40} | {(venue_text or 'TBD')[:25]:<25} | {parsed_date}")

            except Exception as e:
                print(f"[BMS] Card parse error: {e}")


def _extract_venue_date(texts: list[str]) -> tuple[str | None, str | None]:
    month_kw = {
        "jan","feb","mar","apr","may","jun",
        "jul","aug","sep","oct","nov","dec",
        "january","february","march","april","june","july",
        "august","september","october","november","december",
    }
    day_kw   = {"mon","tue","wed","thu","fri","sat","sun"}
    misc_kw  = {"onwards","2024","2025","2026","today","tomorrow"}
    all_kw   = month_kw | day_kw | misc_kw

    date_text  = None
    venue_text = None

    for t in texts:
        lower = t.lower()
        has_kw    = any(kw in lower for kw in all_kw)
        has_digit = any(c.isdigit() for c in t)
        if has_kw and (has_digit or any(kw in lower for kw in misc_kw)):
            if date_text is None:
                date_text = t
        elif venue_text is None and len(t) > 3:
            venue_text = t

    return venue_text, date_text


def _parse_date(raw: str) -> str | None:
    if not raw:
        return None

    clean = raw.strip()

    for noise in ["onwards","Onwards","ONWARDS","onward","|","»"]:
        clean = clean.replace(noise, "").strip()

    # Strip ordinal suffixes: 24th → 24
    clean = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", clean, flags=re.IGNORECASE)

    # Strip day-of-week: "Sat, 24 May" → "24 May"
    if "," in clean:
        clean = clean.split(",", 1)[1].strip()

    # Take first of a range
    for sep in [" - ", " – ", " to ", "-", "–"]:
        if sep in clean:
            clean = clean.split(sep)[0].strip()
            break

    clean = " ".join(clean.split())

    formats = [
        "%d %b %Y", "%d %B %Y",
        "%d %b",    "%d %B",
        "%B %d %Y", "%b %d %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(clean, fmt)
            if dt.year == 1900:
                now = datetime.now()
                dt = dt.replace(year=now.year)
                if dt < now:
                    dt = dt.replace(year=now.year + 1)
            return dt.isoformat()
        except ValueError:
            continue

    return None