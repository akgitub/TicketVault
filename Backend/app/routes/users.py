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
    """Called on first sign-in to sync Clerk user into Supabase users table."""
    clerk_id = claims["sub"]
    result = (
        supabase.table("users")
        .upsert(
            {"clerk_id": clerk_id, "name": body.name, "email": body.email},
            on_conflict="clerk_id",
        )
        .execute()
    )
    return result.data[0]


@router.get("/me")
async def get_me(claims: dict = Depends(get_current_user)):
    clerk_id = claims["sub"]
    result = (
        supabase.table("users")
        .select("*")
        .eq("clerk_id", clerk_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data
