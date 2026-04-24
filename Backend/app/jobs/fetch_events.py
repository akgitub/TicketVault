from scraper.scrapers.bookmyshow import scrape_bookmyshow
from scraper.scrapers.district import scrape_district
from app.database import supabase


# 🔹 Get city_id from DB
def get_city_id(city_name: str):
    res = supabase.table("cities").select("id").eq("name", city_name).execute()
    if res.data:
        return res.data[0]["id"]
    return None


# 🔹 Insert events into DB
def insert_events(events):
    for event in events:
        try:
            city_id = get_city_id(event.get("city"))

            if not city_id:
                print(f"Skipping event (unknown city): {event.get('city')}")
                continue

            supabase.table("events").insert({
                "name": event.get("name"),
                "venue": event.get("venue"),
                "date": event.get("date"),
                "city_id": city_id,
                "image_url": event.get("image_url"),
                "source": event.get("source", "scraper"),
            }).execute()

        except Exception as e:
            print("Insert failed:", e)


# 🔹 Main runner
def run():
    print("🔄 Fetching events...")

    try:
        bms_events = scrape_bookmyshow()
    except Exception as e:
        print("BookMyShow scraper failed:", e)
        bms_events = []

    try:
        district_events = scrape_district()
    except Exception as e:
        print("District scraper failed:", e)
        district_events = []

    all_events = bms_events + district_events

    print(f"Total events fetched: {len(all_events)}")

    insert_events(all_events)

    print("Done inserting events!")


if __name__ == "__main__":
    run()