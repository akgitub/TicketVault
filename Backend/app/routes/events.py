from fastapi import APIRouter, Depends
from app.database import supabase
from app.middleware.auth import get_current_user
from fastapi import HTTPException

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def list_events(
    city_id: str | None = None,
):
    q = (
        supabase.table("events")
        .select("*, cities(name)")
        .gte("date", "now()")
        .order("date", desc=False)
    )
    if city_id:
        q = q.eq("city_id", city_id)
    return q.limit(50).execute().data


@router.get("/{event_id}")
async def get_event(
    event_id: str,
    # claims: dict = Depends(get_current_user),
):
    r = (
        supabase.table("events")
        .select("*, cities(name)")
        .eq("id", event_id)
        .single()
        .execute()
    )

    if not r.data:
        raise HTTPException(status_code=404, detail="Event not found")

    return r.data

# @router.get("")
# async def list_events(city_id: str | None = None):
#     return [
#         {
#             "id": "1",
#             "title": "Arijit Singh Live",
#             "city": {"name": "Indore"},
#             "date": "2026-05-10"
#         },
#         {
#             "id": "2",
#             "title": "Standup Comedy Night",
#             "city": {"name": "Indore"},
#             "date": "2026-05-15"
#         }
#     ]