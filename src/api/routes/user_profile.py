from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["User Profile"])

# ─── Pydantic Models ───────────────────────────────────────────────

class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Request model for updating user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, description="Valid email address")
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=2048)
    phone: Optional[str] = Field(None, max_length=20)


# ─── Simulated Database ────────────────────────────────────────────

# Replace with actual DB queries in production
fake_db: dict[int, dict] = {
    1: {
        "id": 1,
        "user_id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "bio": "Backend engineer & open-source enthusiast.",
        "avatar_url": "https://avatars.example.com/jane.png",
        "phone": "+1-555-0100",
        "created_at": datetime(2024, 1, 15, 10, 30, 0),
        "updated_at": datetime(2025, 6, 1, 8, 0, 0),
    }
}


# ─── GET /api/users/{user_id}/profile ──────────────────────────────

@router.get(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
    summary="Get User Profile",
    responses={
        200: {"description": "User profile retrieved successfully"},
        404: {"description": "User profile not found"},
    },
)
async def get_user_profile(
    user_id: int = Path(..., gt=0, description="The ID of the user"),
) -> UserProfileResponse:
    """
    Retrieve a user's profile by their user ID.
    """
    profile = fake_db.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile for user {user_id} not found")
    return UserProfileResponse(**profile)


# ─── PUT /api/users/{user_id}/profile ──────────────────────────────

@router.put(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
    summary="Update User Profile",
    responses={
        200: {"description": "User profile updated successfully"},
        404: {"description": "User profile not found"},
        422: {"description": "Validation error"},
    },
)
async def update_user_profile(
    user_id: int = Path(..., gt=0, description="The ID of the user"),
    payload: UserProfileUpdate = ...,
) -> UserProfileResponse:
    """
    Update a user's profile. Only provided fields are updated (partial update).
    """
    profile = fake_db.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile for user {user_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="No fields provided for update")

    for field, value in update_data.items():
        profile[field] = value
    profile["updated_at"] = datetime.utcnow()

    fake_db[user_id] = profile
    return UserProfileResponse(**profile)
