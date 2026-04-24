"""
Auto-confirm cron job.
Runs every 5 minutes via APScheduler.
Auto-confirms paid orders where buyer did not act within 2 hours.
"""
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import supabase

UTC = timezone.utc


def run_auto_confirm():
    now = datetime.now(UTC).isoformat()

    r = (
        supabase.table("orders")
        .select("*, order_items(ticket_id, tickets(seller_id, price, listing_fee))")
        .eq("payment_status", "paid")
        .eq("confirmation_status", "pending")
        .lt("confirmation_deadline", now)
        .execute()
    )

    orders = r.data or []
    confirmed = []

    for order in orders:
        try:
            supabase.table("orders").update({
                "confirmation_status": "auto_confirmed",
            }).eq("id", order["id"]).execute()

            for item in order["order_items"]:
                ticket_id = item["ticket_id"]

                supabase.table("tickets").update({
                    "status": "sold",
                }).eq("id", ticket_id).execute()

                listing_fee_inr = float(item["tickets"]["listing_fee"])
                if listing_fee_inr > 0 and order.get("stripe_payment_intent"):
                    try:
                        from app.services.stripe import refund_payment
                        refund_payment(
                            payment_intent_id=order["stripe_payment_intent"],
                            amount_paise=int(listing_fee_inr * 100),
                        )
                    except Exception:
                        pass

            confirmed.append(order["id"])

        except Exception as e:
            print(f"[auto_confirm] Failed for order {order['id']}: {e}")

    print(f"[auto_confirm] Auto-confirmed {len(confirmed)} orders.")
    return confirmed


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app):
    scheduler.add_job(run_auto_confirm, "interval", minutes=5, id="auto_confirm")
    scheduler.start()
    print("[scheduler] Auto-confirm job started.")
    yield
    scheduler.shutdown()
