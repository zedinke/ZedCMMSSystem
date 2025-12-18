"""
Parts/Assets Router
Part inventory management (Assets endpoint uses Part model)
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional
from api.schemas import (
    AssetCreate, AssetUpdate, AssetResponse, AssetListResponse, ErrorResponse
)
from api.dependencies import get_db, get_current_user, require_role
from api.security import TokenData
from database.models import Part
from services.inventory_service import create_part as service_create_part
import logging

router = APIRouter(prefix="/assets", tags=["Assets"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=AssetListResponse,
    dependencies=[Depends(get_current_user)]
)
async def list_assets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status")
):
    """
    List parts/assets with pagination and filtering
    
    **Query Parameters:**
    - `skip`: Number of records to skip
    - `limit`: Number of records to return (max: 100)
    - `status`: Filter by status
    """
    try:
        stmt = select(Part).offset(skip).limit(limit)
        
        if status_filter:
            stmt = stmt.where(Part.status == status_filter)
        
        assets = db.execute(stmt).scalars().all()
        
        # Get total count
        count_stmt = select(func.count()).select_from(Part)
        if status_filter:
            count_stmt = count_stmt.where(Part.status == status_filter)
        total = db.execute(count_stmt).scalar()
        
        return AssetListResponse(
            total=total,
            items=[AssetResponse.from_orm(a) for a in assets]
        )
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list assets"
        )


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Get asset/part by ID
    """
    try:
        stmt = select(Part).where(Part.id == asset_id)
        asset = db.execute(stmt).scalars().first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return AssetResponse.from_orm(asset)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset {asset_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get asset"
        )


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]
)
async def create_asset(
    asset_data: AssetCreate,
    current_user: TokenData = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db)
):
    """
    Create new asset/part
    """
    try:
        new_part = service_create_part(
            sku=asset_data.asset_tag,
            name=asset_data.name,
            category=None,
            supplier_id=None,
            buy_price=0.0,
            sell_price=0.0,
            safety_stock=0,
            reorder_quantity=0,
            description=None,
            session=db,
        )

        # státusz/asset_type mentése a modell mezőibe, ha vannak ilyen oszlopok
        if asset_data.asset_type:
            new_part.part_type = asset_data.asset_type
        if asset_data.status:
            new_part.status = asset_data.status
        db.commit(); db.refresh(new_part)

        logger.info(f"Asset created: {asset_data.name} by {current_user.username}")
        return AssetResponse.from_orm(new_part)

    except Exception as e:
        logger.error(f"Error creating asset: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{asset_id}",
    response_model=AssetResponse
)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update asset/part
    """
    try:
        stmt = select(Part).where(Part.id == asset_id)
        asset = db.execute(stmt).scalars().first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        # Update fields
        update_dict = asset_data.dict(exclude_unset=True)
        
        # Map API field names to Part model field names
        if "name" in update_dict:
            asset.name = update_dict["name"]
        if "asset_type" in update_dict:
            asset.part_type = update_dict["asset_type"]
        if "asset_tag" in update_dict:
            asset.part_number = update_dict["asset_tag"]
        if "status" in update_dict:
            asset.status = update_dict["status"]
        
        db.commit()
        db.refresh(asset)
        
        logger.info(f"Asset {asset_id} updated by {current_user.username}")
        return AssetResponse.from_orm(asset)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating asset {asset_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update asset"
        )


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)]
)
async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Delete asset/part
    """
    try:
        stmt = select(Part).where(Part.id == asset_id)
        asset = db.execute(stmt).scalars().first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        db.delete(asset)
        db.commit()
        logger.info(f"Asset {asset_id} deleted")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting asset {asset_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete asset"
        )
