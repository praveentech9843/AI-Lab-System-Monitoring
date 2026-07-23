"""
Blocked Website CRUD Operations Module.
Provides database access functions for BlockedWebsite ORM models with safe transaction handling.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import BlockedWebsite
from schemas.blocked_website import BlockedWebsiteCreate


def get_all_blocked_websites(db: Session) -> List[BlockedWebsite]:
    """
    Retrieves all BlockedWebsite records from the database.
    """
    statement = select(BlockedWebsite).order_by(BlockedWebsite.domain.asc())
    return list(db.scalars(statement).all())


def get_blocked_website_by_id(db: Session, website_id: UUID) -> Optional[BlockedWebsite]:
    """
    Retrieves a BlockedWebsite by its ID.
    """
    statement = select(BlockedWebsite).where(BlockedWebsite.id == website_id)
    return db.scalar(statement)


def get_blocked_website_by_domain(db: Session, domain: str) -> Optional[BlockedWebsite]:
    """
    Retrieves a BlockedWebsite by its domain.
    """
    statement = select(BlockedWebsite).where(BlockedWebsite.domain == domain.lower().strip())
    return db.scalar(statement)


def create_blocked_website(db: Session, website: BlockedWebsiteCreate) -> BlockedWebsite:
    """
    Creates a new BlockedWebsite configuration.
    """
    db_website = BlockedWebsite(
        domain=website.domain.lower().strip(),
        enabled=website.enabled
    )
    db.add(db_website)
    try:
        db.commit()
        db.refresh(db_website)
    except Exception:
        db.rollback()
        raise
    return db_website


def update_blocked_website(db: Session, db_website: BlockedWebsite, enabled: bool) -> BlockedWebsite:
    """
    Updates the enabled state of a BlockedWebsite configuration.
    """
    db_website.enabled = enabled
    try:
        db.commit()
        db.refresh(db_website)
    except Exception:
        db.rollback()
        raise
    return db_website


def delete_blocked_website(db: Session, website_id: UUID) -> bool:
    """
    Deletes a BlockedWebsite record by ID. Returns True if deleted, False if not found.
    """
    db_website = get_blocked_website_by_id(db, website_id)
    if not db_website:
        return False
    db.delete(db_website)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
