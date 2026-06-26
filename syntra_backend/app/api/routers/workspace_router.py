from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import Workspace, ChatSession

router = APIRouter(prefix="/v1", tags=["Workspaces"])


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None

class SessionCreate(BaseModel):
    workspace_id: int
    session_name: str = "Untitled Session"


# ─── Workspace Endpoints ──────────────────────────────────────────────────────

@router.get("/workspaces/{user_id}")
async def get_user_workspaces(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get all workspaces for a user."""
    result = await db.execute(
        select(Workspace).where(Workspace.user_id == user_id)
    )
    workspaces = result.scalars().all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "created_at": w.created_at.isoformat() if w.created_at else None
        }
        for w in workspaces
    ]


@router.post("/workspaces")
async def create_workspace(payload: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    """Create a new workspace for a user."""
    workspace = Workspace(
        user_id=payload.user_id,
        name=payload.name,
        description=payload.description
    )
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)
    return {"id": workspace.id, "name": workspace.name, "message": "Workspace created."}


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(workspace_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a workspace and all its sessions/history."""
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    await db.delete(workspace)
    await db.commit()
    return {"message": f"Workspace '{workspace.name}' deleted."}


# ─── ChatSession Endpoints ────────────────────────────────────────────────────

@router.get("/workspaces/{workspace_id}/sessions")
async def get_sessions(workspace_id: int, db: AsyncSession = Depends(get_db)):
    """Get all chat sessions inside a workspace."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.workspace_id == workspace_id)
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "session_name": s.session_name,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in sessions
    ]


@router.post("/sessions")
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new chat session inside a workspace."""
    session = ChatSession(
        workspace_id=payload.workspace_id,
        session_name=payload.session_name
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"id": session.id, "session_name": session.session_name, "message": "Session created."}
