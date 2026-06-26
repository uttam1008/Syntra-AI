import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.db.session import get_db
from app.db.models import FeatureHistory, ChatSession, Workspace, FeatureNameEnum

router = APIRouter(prefix="/v1", tags=["History"])


@router.get("/history/{feature_name}")
async def get_feature_history(
    feature_name: str,
    session_id: Optional[int] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch history for a specific feature (enhance, intent, compress, chat).
    Optionally filter by session_id.
    """
    # Validate feature name
    try:
        feature_enum = FeatureNameEnum(feature_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid feature name: '{feature_name}'. Must be one of: enhance, intent, compress, chat")

    query = (
        select(FeatureHistory)
        .where(FeatureHistory.feature_name == feature_enum)
        .order_by(desc(FeatureHistory.created_at))
        .limit(limit)
    )

    if session_id:
        query = query.where(FeatureHistory.session_id == session_id)

    result = await db.execute(query)
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "session_id": item.session_id,
            "feature_name": item.feature_name.value,
            "input_prompt": item.input_prompt,
            "output_data": json.loads(item.output_data) if item.output_data else {},
            "model_used": item.model_used,
            "created_at": item.created_at.isoformat() if item.created_at else None
        }
        for item in items
    ]


@router.get("/history")
async def get_all_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Fetch recent history across all features."""
    result = await db.execute(
        select(FeatureHistory)
        .order_by(desc(FeatureHistory.created_at))
        .limit(limit)
    )
    items = result.scalars().all()

    return [
        {
            "id": item.id,
            "session_id": item.session_id,
            "feature_name": item.feature_name.value,
            "input_prompt": item.input_prompt,
            "output_data": json.loads(item.output_data) if item.output_data else {},
            "model_used": item.model_used,
            "created_at": item.created_at.isoformat() if item.created_at else None
        }
        for item in items
    ]
