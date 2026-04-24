from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from app.middleware.auth import get_current_user
from app.database import supabase

router = APIRouter(prefix="/users", tags=["users"])


class UpsertUserRequest(BaseModel):
    name: str
    email: EmailStr


@router.post("/me")
async def upsert_user(
    body: UpsertUserRequest,
    claims: dict = Depends(get_current_user),
):
    """
    Sync Clerk user into Supabase.
    - If user exists → update
    - If not → create
    """

    clerk_id = claims["sub"]

    # 🔹 Check if user exists
    existing = (
        supabase.table("users")
        .select("*")
        .eq("clerk_id", clerk_id)
        .maybe_single()
        .execute()
    )

    if existing.data:
        # 🔹 Update user
        updated = (
            supabase.table("users")
            .update({
                "name": body.name,
                "email": body.email,
            })
            .eq("clerk_id", clerk_id)
            .execute()
        )
        return updated.data[0]

    # 🔹 Create new user
    created = (
        supabase.table("users")
        .insert({
            "clerk_id": clerk_id,
            "name": body.name,
            "email": body.email,
        })
        .execute()
    )

    return created.data[0]


@router.get("/me")
async def get_me(claims: dict = Depends(get_current_user)):
    """
    Get current logged-in user from DB
    """
    clerk_id = claims["sub"]

    result = (
        supabase.table("users")
        .select("*")
        .eq("clerk_id", clerk_id)
        .maybe_single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="User not found. Call /users/me POST first."
        )

    return result.data