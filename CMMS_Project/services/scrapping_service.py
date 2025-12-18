"""
Scrapping service for generating scrapping documents
"""

from typing import Optional, List
from pathlib import Path
from sqlalchemy.orm import Session

from database.session_manager import SessionLocal
from database.models import ScrappingDocument, Part, Machine, utcnow
from services.pdf_service import generate_scrapping_docx
from services.settings_service import get_selected_scrapping_template, get_auto_generate_scrapping_doc
from services.log_service import log_action
from services.context_service import get_current_user_id

import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def generate_scrapping_document(
    entity_type: str,
    entity_id: int,
    reason: Optional[str] = None,
    worksheet_id: Optional[int] = None,
    pm_history_id: Optional[int] = None,
    item_number: Optional[int] = None,
    total_items: Optional[int] = None,
    session: Session = None
) -> ScrappingDocument:
    """
    Generate a scrapping document for a part or machine
    
    Args:
        entity_type: "Part" or "Machine"
        entity_id: ID of the part or machine
        reason: Reason for scrapping
        worksheet_id: Optional worksheet ID if from worksheet
        pm_history_id: Optional PM history ID if from PM task
        session: Database session
    
    Returns:
        ScrappingDocument: Created scrapping document
    """
    session, should_close = _get_session(session)
    try:
        # Get entity
        if entity_type == "Part":
            entity = session.query(Part).filter_by(id=entity_id).first()
            if not entity:
                raise ValueError(f"Part with ID {entity_id} not found")
        elif entity_type == "Machine":
            entity = session.query(Machine).filter_by(id=entity_id).first()
            if not entity:
                raise ValueError(f"Machine with ID {entity_id} not found")
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        
        # Get template path
        template_path = get_selected_scrapping_template()
        
        # Update reason to include item number if provided
        final_reason = reason or "Selejtezés"
        if item_number and total_items:
            final_reason = f"{final_reason} (Darab {item_number}/{total_items})"
        elif item_number:
            final_reason = f"{final_reason} (Darab {item_number})"
        
        # Generate DOCX document
        docx_path = generate_scrapping_docx(
            entity_type=entity_type,
            entity_id=entity_id,
            reason=final_reason,
            template_path=template_path,
            worksheet_id=worksheet_id,
            pm_history_id=pm_history_id,
            session=session
        )
        
        # Get current user ID
        user_id = get_current_user_id()
        
        # Create scrapping document record
        scrapping_doc = ScrappingDocument(
            entity_type=entity_type,
            entity_id=entity_id,
            docx_path=str(docx_path),
            generated_at=utcnow(),
            generated_by_user_id=user_id,
            reason=final_reason,
            worksheet_id=worksheet_id,
            pm_history_id=pm_history_id,
        )
        
        session.add(scrapping_doc)
        session.commit()
        session.refresh(scrapping_doc)
        
        # Log the action
        log_action(
            category="scrapping",
            action_type="generate",
            entity_type="ScrappingDocument",
            entity_id=scrapping_doc.id,
            user_id=user_id,
            description=f"Selejtezési lap generálva: {entity_type} ID {entity_id}",
            metadata={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "reason": reason,
                "worksheet_id": worksheet_id,
                "pm_history_id": pm_history_id,
            },
            session=session
        )
        
        logger.info(f"Scrapping document generated for {entity_type}:{entity_id}")
        return scrapping_doc
    except Exception as e:
        session.rollback()
        logger.error(f"Error generating scrapping document: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_scrapping_document(
    entity_type: str,
    entity_id: int,
    session: Session = None
) -> Optional[ScrappingDocument]:
    """
    Get scrapping document for an entity
    
    Args:
        entity_type: "Part" or "Machine"
        entity_id: ID of the part or machine
        session: Database session
    
    Returns:
        Optional[ScrappingDocument]: Scrapping document if exists
    """
    session, should_close = _get_session(session)
    try:
        return session.query(ScrappingDocument).filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).first()
    finally:
        if should_close:
            session.close()


def list_scrapping_documents(
    entity_type: Optional[str] = None,
    session: Session = None
) -> List[ScrappingDocument]:
    """
    List scrapping documents
    
    Args:
        entity_type: Optional filter by entity type
        session: Database session
    
    Returns:
        List[ScrappingDocument]: List of scrapping documents
    """
    session, should_close = _get_session(session)
    try:
        query = session.query(ScrappingDocument)
        
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        
        return query.order_by(ScrappingDocument.generated_at.desc()).all()
    finally:
        if should_close:
            session.close()

