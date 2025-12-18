"""
Worksheets Router
Worksheet CRUD operations
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from api.schemas import (
    WorksheetCreate, WorksheetUpdate, WorksheetResponse, WorksheetListResponse, ErrorResponse
)
from api.dependencies import get_db, get_current_user
from api.security import TokenData
from database.models import Worksheet
import logging

router = APIRouter(prefix="/worksheets", tags=["Worksheets"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=WorksheetListResponse,
    dependencies=[Depends(get_current_user)]
)
async def list_worksheets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    machine_id: Optional[int] = Query(None)
):
    """
    List worksheets with pagination and filtering
    
    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Number of records to return (default: 10, max: 100)
    - `status`: Filter by status (pending, in_progress, completed)
    - `machine_id`: Filter by machine ID
    """
    try:
        stmt = select(Worksheet).offset(skip).limit(limit)
        
        if status_filter:
            stmt = stmt.where(Worksheet.status == status_filter)
        if machine_id:
            stmt = stmt.where(Worksheet.machine_id == machine_id)
        
        worksheets = db.execute(stmt).scalars().all()
        
        # Get total count
        count_stmt = select(func.count()).select_from(Worksheet)
        if status_filter:
            count_stmt = count_stmt.where(Worksheet.status == status_filter)
        if machine_id:
            count_stmt = count_stmt.where(Worksheet.machine_id == machine_id)
        total = db.execute(count_stmt).scalar()
        
        return WorksheetListResponse(
            total=total,
            items=[WorksheetResponse.from_orm(w) for w in worksheets]
        )
    except Exception as e:
        logger.error(f"Error listing worksheets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list worksheets"
        )


@router.get(
    "/{worksheet_id}",
    response_model=WorksheetResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_worksheet(worksheet_id: int, db: Session = Depends(get_db)):
    """
    Get worksheet by ID
    """
    try:
        stmt = select(Worksheet).where(Worksheet.id == worksheet_id)
        worksheet = db.execute(stmt).scalars().first()
        
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worksheet not found"
            )
        
        return WorksheetResponse.from_orm(worksheet)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting worksheet {worksheet_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get worksheet"
        )


@router.post(
    "/",
    response_model=WorksheetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]
)
async def create_worksheet(
    worksheet_data: WorksheetCreate,
    db: Session = Depends(get_db)
):
    """
    Create new worksheet
    """
    try:
        new_worksheet = Worksheet(
            machine_id=worksheet_data.machine_id,
            maintenance_type=worksheet_data.maintenance_type,
            description=worksheet_data.description,
            assigned_to_user_id=worksheet_data.assigned_to_user_id,
            status=worksheet_data.status or "pending"
        )
        
        db.add(new_worksheet)
        db.commit()
        db.refresh(new_worksheet)
        
        logger.info(f"Worksheet created for machine {worksheet_data.machine_id}")
        return WorksheetResponse.from_orm(new_worksheet)
        
    except Exception as e:
        logger.error(f"Error creating worksheet: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create worksheet"
        )


@router.put(
    "/{worksheet_id}",
    response_model=WorksheetResponse
)
async def update_worksheet(
    worksheet_id: int,
    worksheet_data: WorksheetUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update worksheet
    """
    try:
        stmt = select(Worksheet).where(Worksheet.id == worksheet_id)
        worksheet = db.execute(stmt).scalars().first()
        
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worksheet not found"
            )
        
        # Update fields
        update_dict = worksheet_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(worksheet, key, value)
        
        db.commit()
        db.refresh(worksheet)
        
        logger.info(f"Worksheet {worksheet_id} updated by {current_user.username}")
        return WorksheetResponse.from_orm(worksheet)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating worksheet {worksheet_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update worksheet"
        )


@router.delete(
    "/{worksheet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)]
)
async def delete_worksheet(worksheet_id: int, db: Session = Depends(get_db)):
    """
    Delete worksheet
    """
    try:
        stmt = select(Worksheet).where(Worksheet.id == worksheet_id)
        worksheet = db.execute(stmt).scalars().first()
        
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worksheet not found"
            )
        
        db.delete(worksheet)
        db.commit()
        logger.info(f"Worksheet {worksheet_id} deleted")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting worksheet {worksheet_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete worksheet"
        )
