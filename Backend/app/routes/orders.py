from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timedelta, timezone
from app.middleware.auth import get_current_user
from app.database import supabase
from app.services.razorpay import create_order, verify_payment, refund_payment
from app.schemas.orders import InitiateBuyRequest
from app.config import settings

router = APIRouter(prefix="/orders", tags=["orders"])
UTC = timezone.utc


def _get_user(clerk_id: str) -> dict:
    r = supabase.table("users").select("id").eq("clerk_id", clerk_id).single().execute()
    if not r.data:
        raise HTTPException(404, "User not found.")
    return r.data


def _release_lock(ticket_id: str):
    supabase.table("tickets").update({
        "status": "available",
        "locked_by": None,
        "lock_expiry": None,
    }).eq("id", ticket_id).execute()


@router.post("/initiate")
async def initiate_buy(
    body: InitiateBuyRequest,
    claims: dict = Depends(get_current_user),
):
    buyer = _get_user(claims["sub"])
    ticket_id = str(body.ticket_id)

    r = (
        supabase.table("tickets")
        .select("*, events(name)")
        .eq("id", ticket_id)
        .single()
        .execute()
    )
    ticket = r.data
    if not ticket:
        raise HTTPException(404, "Ticket not found.")

    if ticket["status"] != "available":
        raise HTTPException(409, "Ticket is no longer available.")

    if ticket["seller_id"] == buyer["id"]:
        raise HTTPException(400, "You cannot buy your own ticket.")

    now = datetime.now(UTC)
    lock_expiry = now + timedelta(minutes=10)

    lock_res = (
        supabase.table("tickets")
        .update({
            "status": "locked",
            "locked_by": buyer["id"],
            "lock_expiry": lock_expiry.isoformat(),
        })
        .eq("id", ticket_id)
        .eq("status", "available")
        .execute()
    )

    if not lock_res.data:
        raise HTTPException(409, "Ticket was just taken. Please try another.")

    razorpay_order = create_order(
    amount_inr=float(ticket["price"]),
    receipt=f"order_{ticket_id}"
    )

    order_res = (
        supabase.table("orders")
        .insert({
            "buyer_id": buyer["id"],
            "total_price": float(ticket["price"]),
            "payment_status": "pending",
            "stripe_payment_intent": razorpay_order["id"],
            "confirmation_status": "pending",
        })
        .execute()
    )
    order = order_res.data[0]

    supabase.table("order_items").insert({
        "order_id": order["id"],
        "ticket_id": ticket_id,
    }).execute()

    return {
    "order_id": order["id"],
    "razorpay_order_id": razorpay_order["id"],
    "lock_expiry": lock_expiry.isoformat(),
    "amount": float(ticket["price"]),
    }


@router.post("/verify")
async def verify_order_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    claims: dict = Depends(get_current_user),
):
    valid = verify_payment(
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
    )

    if not valid:
        raise HTTPException(400, "Invalid payment signature")

    # Update order → paid
    supabase.table("orders").update({
        "payment_status": "paid"
    }).eq("stripe_payment_intent", razorpay_order_id).execute()

    return {"status": "paid"}


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    claims: dict = Depends(get_current_user),
):
    buyer = _get_user(claims["sub"])
    r = (
        supabase.table("orders")
        .select("""
            *,
            order_items(
                ticket_id,
                tickets(
                    price, original_price, status, listing_fee,
                    events(name, date, venue),
                    cities(name)
                )
            )
        """)
        .eq("id", order_id)
        .eq("buyer_id", buyer["id"])
        .single()
        .execute()
    )
    if not r.data:
        raise HTTPException(404, "Order not found.")

    order = r.data

    if order["payment_status"] == "paid":
        for item in order["order_items"]:
            qr = (
                supabase.table("ticket_qrs")
                .select("qr_image_url")
                .eq("ticket_id", item["ticket_id"])
                .execute()
            )
            if qr.data:
                path = qr.data[0]["qr_image_url"]
                signed = supabase.storage.from_("ticket-qrs").create_signed_url(
                    path, expires_in=3600
                )
                item["qr_signed_url"] = signed.get("signedURL")

    return order
