"""
Machines Router
Machine CRUD operations
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from api.schemas import (
    MachineCreate, MachineUpdate, MachineResponse, MachineListResponse, ErrorResponse
)
from api.dependencies import get_db, get_current_user, require_role, get_user_language
from api.security import TokenData
from database.models import Machine
from services.asset_service import create_machine as service_create_machine
from utils.localization_helper import get_localized_error
import logging

router = APIRouter(prefix="/machines", tags=["Machines"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=MachineListResponse,
    dependencies=[Depends(get_current_user)]
)
async def list_machines(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status")
):
    """
    List all machines with pagination and filtering
    
    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Number of records to return (default: 10, max: 100)
    - `status`: Filter by status (operational, maintenance, offline)
    
    **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/machines?skip=0&limit=20&status=operational" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        stmt = select(Machine).offset(skip).limit(limit)
        
        if status_filter:
            stmt = stmt.where(Machine.status == status_filter)
        
        machines = db.execute(stmt).scalars().all()
        
        # Get total count
        count_stmt = select(func.count()).select_from(Machine)
        if status_filter:
            count_stmt = count_stmt.where(Machine.status == status_filter)
        total = db.execute(count_stmt).scalar()
        
        return MachineListResponse(
            total=total,
            items=[MachineResponse.from_orm(m) for m in machines]
        )
    except Exception as e:
        logger.error(f"Error listing machines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list machines"
        )


@router.get(
    "/{machine_id}",
    response_model=MachineResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_machine(machine_id: int, db: Session = Depends(get_db)):
    """
    Get machine by ID
    
    **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/machines/1" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        stmt = select(Machine).where(Machine.id == machine_id)
        machine = db.execute(stmt).scalars().first()
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Machine not found"
            )
        
        return MachineResponse.from_orm(machine)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting machine {machine_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get machine"
        )


@router.post(
    "/",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    dependencies=[Depends(get_current_user)]
)
async def create_machine(
    machine_data: MachineCreate,
    current_user: TokenData = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """
    Create new machine
    
    **Request Body:**
    - `name`: Machine name (required)
    - `model`: Machine model (optional)
    - `serial_number`: Serial number (optional)
    - `production_line_id`: Production line ID (optional)
    - `status`: Status (optional, default: "operational")
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/machines/" \\
      -H "Authorization: Bearer <token>" \\
      -H "Content-Type: application/json" \\
      -d '{
        "name": "CNC Machine A1",
        "model": "HAAS VF-4",
        "serial_number": "ABC123456",
        "status": "operational"
      }'
    ```
    """
    try:
        new_machine = service_create_machine(
            production_line_id=machine_data.production_line_id,
            name=machine_data.name,
            serial_number=machine_data.serial_number,
            model=machine_data.model,
            manufacturer=None,
            manual_pdf_path=None,
            session=db,
        )

        # státusz: ha küldött, állítsuk
        if machine_data.status:
            new_machine.status = machine_data.status
            db.commit(); db.refresh(new_machine)

        logger.info(f"Machine created: {machine_data.name} by {current_user.username}")
        return MachineResponse.from_orm(new_machine)

    except Exception as e:
        logger.error(f"Error creating machine: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{machine_id}",
    response_model=MachineResponse,
    responses={404: {"model": ErrorResponse}}
)
async def update_machine(
    machine_id: int,
    machine_data: MachineUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update machine
    
    **Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/machines/1" \\
      -H "Authorization: Bearer <token>" \\
      -H "Content-Type: application/json" \\
      -d '{"status": "maintenance"}'
    ```
    """
    try:
        stmt = select(Machine).where(Machine.id == machine_id)
        machine = db.execute(stmt).scalars().first()
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Machine not found"
            )
        
        # Update fields
        update_dict = machine_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(machine, key, value)
        
        db.commit()
        db.refresh(machine)
        
        logger.info(f"Machine {machine_id} updated by {current_user.username}")
        return MachineResponse.from_orm(machine)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating machine {machine_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update machine"
        )


@router.delete(
    "/{machine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    dependencies=[Depends(get_current_user)]
)
async def delete_machine(
    machine_id: int, 
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    lang_code: str = Depends(get_user_language)
):
    """
    Scrap machine (ISO 55001 compliant - soft delete)
    Sets status to 'Selejtezve' instead of hard delete
    
    **Example:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/machines/1" \\
      -H "Authorization: Bearer <token>"
    ```
    """
    try:
        from services import asset_service
        from utils.localization_helper import get_localized_error
        
        stmt = select(Machine).where(Machine.id == machine_id)
        machine = db.execute(stmt).scalars().first()
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_localized_error("machine_not_found", lang_code=lang_code)
            )
        
        # Use scrap_machine instead of hard delete (ISO 55001 compliant)
        asset_service.scrap_machine(machine_id=machine_id, scrapped_by_user_id=current_user.user_id, session=db)
        logger.info(f"Machine {machine_id} scrapped (ISO 55001 compliant) by user {current_user.user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scrapping machine {machine_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_localized_error("database.query_failed", lang_code=lang_code)
        )
