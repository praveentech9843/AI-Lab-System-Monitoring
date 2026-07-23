"""
Blocked Website Management REST API Router.
Provides endpoints for creating, querying, updating, and deleting Blocked Website rules.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import BlockedWebsite
from schemas.blocked_website import BlockedWebsiteCreate, BlockedWebsiteResponse
from crud.blocked_website import (
    get_all_blocked_websites,
    get_blocked_website_by_id,
    get_blocked_website_by_domain,
    create_blocked_website,
    update_blocked_website,
    delete_blocked_website,
)
from websocket.manager import manager

router = APIRouter(prefix="/blocked-websites", tags=["Blocked Websites"])


async def notify_clients_of_update(db: Session):
    """Broadcasts the latest enabled blocked websites to all agents/listeners."""
    websites = get_all_blocked_websites(db)
    enabled_domains = [w.domain for w in websites if w.enabled]
    await manager.broadcast({
        "event": "BLOCKED_WEBSITES_UPDATED",
        "data": {
            "domains": enabled_domains
        }
    })


@router.get("/", response_model=List[BlockedWebsiteResponse], status_code=status.HTTP_200_OK)
def read_all_blocked_websites(db: Session = Depends(get_db)):
    """
    Retrieves all blocked websites configurations.
    """
    return get_all_blocked_websites(db)


@router.post("/", response_model=BlockedWebsiteResponse, status_code=status.HTTP_201_CREATED)
async def add_blocked_website(
    website_data: BlockedWebsiteCreate,
    db: Session = Depends(get_db)
):
    """
    Adds a new blocked website configuration rule.
    """
    existing = get_blocked_website_by_domain(db, website_data.domain)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain is already in the blocked list."
        )
    new_website = create_blocked_website(db, website_data)
    await notify_clients_of_update(db)
    return new_website


@router.put("/{website_id}", response_model=BlockedWebsiteResponse, status_code=status.HTTP_200_OK)
async def toggle_blocked_website(
    website_id: UUID,
    website_data: BlockedWebsiteCreate,
    db: Session = Depends(get_db)
):
    """
    Toggles/updates a blocked website configuration.
    """
    db_website = get_blocked_website_by_id(db, website_id)
    if not db_website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked website config not found."
        )
    updated = update_blocked_website(db, db_website, enabled=website_data.enabled)
    await notify_clients_of_update(db)
    return updated


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_blocked_website(
    website_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Deletes a blocked website configuration rule.
    """
    success = delete_blocked_website(db, website_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked website config not found."
        )
    await notify_clients_of_update(db)
    return None
