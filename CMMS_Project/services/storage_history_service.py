"""
Storage History Service
Retrieves storage operation history and related documents
"""

from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from database.session_manager import SessionLocal
from database.models import SystemLog, Part, StorageLocation, User, PartLocation
from services.storage_service import get_storage_location_path
import logging

logger = logging.getLogger(__name__)


def _get_session(session: Optional[Session]) -> tuple[Session, bool]:
    """Get session or create new one"""
    if session is not None:
        return session, False
    return SessionLocal(), True


def get_storage_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action_type: Optional[str] = None,
    part_id: Optional[int] = None,
    location_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = None
) -> List[Dict]:
    """
    Get storage operation history
    
    Args:
        start_date: Start date filter
        end_date: End date filter
        action_type: Action type filter (assign, update, remove, transfer, create, update, delete)
        part_id: Part ID filter
        location_id: Location ID filter
        user_id: User ID filter
        limit: Maximum number of results
        offset: Offset for pagination
        session: Database session
    
    Returns:
        List of storage history entries with details
    """
    session, should_close = _get_session(session)
    try:
        # Query storage logs
        query = session.query(SystemLog).options(
            joinedload(SystemLog.user)
        ).filter(
            SystemLog.log_category == "storage"
        )
        
        # Apply filters
        if start_date:
            query = query.filter(SystemLog.timestamp >= start_date)
        if end_date:
            query = query.filter(SystemLog.timestamp <= end_date)
        if action_type:
            query = query.filter(SystemLog.action_type == action_type)
        if user_id:
            query = query.filter(SystemLog.user_id == user_id)
        
        # Get logs
        logs = query.order_by(desc(SystemLog.timestamp)).limit(limit).offset(offset).all()
        
        result = []
        for log in logs:
            metadata = log.log_metadata or {}
            
            # Extract part and location info from metadata
            part_id_from_meta = metadata.get('part_id')
            location_id_from_meta = metadata.get('storage_location_id') or metadata.get('location_id')
            source_location_id = metadata.get('source_location_id')
            target_location_id = metadata.get('target_location_id')
            
            # Apply filters
            if part_id and part_id_from_meta != part_id:
                continue
            if location_id:
                if location_id_from_meta != location_id and source_location_id != location_id and target_location_id != location_id:
                    continue
            
            # Get part info
            part_info = None
            if part_id_from_meta:
                part = session.query(Part).filter_by(id=part_id_from_meta).first()
                if part:
                    part_info = {
                        'id': part.id,
                        'name': part.name,
                        'sku': part.sku,
                    }
            
            # Get location info
            location_info = None
            if location_id_from_meta:
                location_path = get_storage_location_path(location_id_from_meta, session)
                location = session.query(StorageLocation).filter_by(id=location_id_from_meta).first()
                if location:
                    location_info = {
                        'id': location.id,
                        'name': location.name,
                        'path': location_path,
                    }
            
            # Get source/target location info for transfers
            source_location_info = None
            target_location_info = None
            if source_location_id:
                source_path = get_storage_location_path(source_location_id, session)
                source_loc = session.query(StorageLocation).filter_by(id=source_location_id).first()
                if source_loc:
                    source_location_info = {
                        'id': source_loc.id,
                        'name': source_loc.name,
                        'path': source_path,
                    }
            
            if target_location_id:
                target_path = get_storage_location_path(target_location_id, session)
                target_loc = session.query(StorageLocation).filter_by(id=target_location_id).first()
                if target_loc:
                    target_location_info = {
                        'id': target_loc.id,
                        'name': target_loc.name,
                        'path': target_path,
                    }
            
            # Find related documents
            documents = _find_related_documents(log, session)
            
            result.append({
                'id': log.id,
                'action_type': log.action_type,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'timestamp': log.timestamp,
                'user_id': log.user_id,
                'user_name': log.user.username if log.user else None,
                'description': log.description,
                'metadata': metadata,
                'part': part_info,
                'location': location_info,
                'source_location': source_location_info,
                'target_location': target_location_info,
                'quantity': metadata.get('quantity'),
                'documents': documents,
            })
        
        return result
    finally:
        if should_close:
            session.close()


def _find_related_documents(log: SystemLog, session: Session) -> List[Dict]:
    """Find related documents for a storage operation"""
    documents = []
    
    try:
        metadata = log.log_metadata or {}
        
        # Check for storage receipt documents (assign action)
        if log.action_type == "assign" and log.entity_type == "PartLocation":
            part_location_id = log.entity_id
            if part_location_id:
                # Look for storage receipt documents
                doc_pattern = f"storage_receipt_{part_location_id}_*.docx"
                doc_dir = Path.cwd() / "generated_documents"
                if doc_dir.exists():
                    for doc_file in doc_dir.glob(doc_pattern):
                        # Find the most recent one if multiple exist
                        if not documents or doc_file.stat().st_mtime > Path(documents[0]['path']).stat().st_mtime:
                            documents = [{
                                'type': 'receipt',
                                'name': 'Betárazás dokumentum',
                                'path': str(doc_file),
                                'filename': doc_file.name,
                            }]
        
        # Check for storage transfer documents (transfer action)
        elif log.action_type == "transfer" and log.entity_type == "PartLocation":
            part_location_id = log.entity_id
            source_location_id = metadata.get('source_location_id')
            target_location_id = metadata.get('target_location_id')
            if part_location_id and source_location_id and target_location_id:
                # Look for storage transfer documents
                doc_pattern = f"storage_transfer_{part_location_id}_{target_location_id}_*.docx"
                doc_dir = Path.cwd() / "generated_documents"
                if doc_dir.exists():
                    for doc_file in doc_dir.glob(doc_pattern):
                        if not documents or doc_file.stat().st_mtime > Path(documents[0]['path']).stat().st_mtime:
                            documents = [{
                                'type': 'transfer',
                                'name': 'Áttárazás dokumentum',
                                'path': str(doc_file),
                                'filename': doc_file.name,
                            }]
        
        # Check for worksheet documents (usage from storage)
        elif log.action_type in ["issue", "use"] and metadata.get('reference_type') == "Worksheet":
            worksheet_id = metadata.get('reference_id')
            if worksheet_id:
                # Look for worksheet PDFs
                pdf_dir = Path.cwd() / "generated_pdfs"
                if pdf_dir.exists():
                    pdf_pattern = f"worksheet_{worksheet_id}_*.pdf"
                    for pdf_file in pdf_dir.glob(pdf_pattern):
                        documents.append({
                            'type': 'worksheet',
                            'name': f'Munkalap #{worksheet_id}',
                            'path': str(pdf_file),
                            'filename': pdf_file.name,
                        })
    
    except Exception as e:
        logger.warning(f"Error finding related documents for log {log.id}: {e}")
    
    return documents


def get_storage_history_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: Session = None
) -> Dict:
    """
    Get summary statistics for storage history
    
    Returns:
        Dictionary with summary statistics
    """
    session, should_close = _get_session(session)
    try:
        query = session.query(SystemLog).filter(
            SystemLog.log_category == "storage"
        )
        
        if start_date:
            query = query.filter(SystemLog.timestamp >= start_date)
        if end_date:
            query = query.filter(SystemLog.timestamp <= end_date)
        
        total_operations = query.count()
        
        # Count by action type
        action_counts = {}
        for action_type in ["assign", "update", "remove", "transfer", "create", "delete"]:
            count = query.filter(SystemLog.action_type == action_type).count()
            if count > 0:
                action_counts[action_type] = count
        
        # Count unique parts
        all_logs = query.all()
        part_ids = set()
        for log in all_logs:
            metadata = log.log_metadata or {}
            if 'part_id' in metadata:
                part_ids.add(metadata['part_id'])
        
        # Count unique locations
        location_ids = set()
        for log in all_logs:
            metadata = log.log_metadata or {}
            if 'storage_location_id' in metadata:
                location_ids.add(metadata['storage_location_id'])
            if 'source_location_id' in metadata:
                location_ids.add(metadata['source_location_id'])
            if 'target_location_id' in metadata:
                location_ids.add(metadata['target_location_id'])
        
        return {
            'total_operations': total_operations,
            'action_counts': action_counts,
            'unique_parts': len(part_ids),
            'unique_locations': len(location_ids),
        }
    finally:
        if should_close:
            session.close()

