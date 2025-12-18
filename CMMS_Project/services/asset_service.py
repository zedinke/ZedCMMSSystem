"""
Asset service: production line, machine, module, history
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from config.constants import ASSET_ACTIONS, MACHINE_STATUS_SCRAPPED
from database.session_manager import SessionLocal
from database.models import (
    ProductionLine,
    Machine,
    Module,
    AssetHistory,
    MachineVersion,
    utcnow,
)

from utils.localization_helper import get_localized_error
import logging

logger = logging.getLogger(__name__)


class AssetServiceError(Exception):
    """Generic asset service error"""
    pass


def _get_session(session: Optional[Session]) -> (Session, bool):
    if session is None:
        return SessionLocal(), True
    return session, False


def create_production_line(
    name: str, 
    description: Optional[str] = None,
    location: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[str] = None,
    capacity: Optional[str] = None,
    responsible_person: Optional[str] = None,
    commission_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> ProductionLine:
    session, should_close = _get_session(session)
    try:
        if session.query(ProductionLine).filter_by(name=name).first():
            raise AssetServiceError(get_localized_error("production_line_name_exists"))
        if code and session.query(ProductionLine).filter_by(code=code).first():
            raise AssetServiceError(get_localized_error("production_line_code_exists"))
        pl = ProductionLine(
            name=name, 
            description=description, 
            location=location,
            code=code,
            status=status or "Active",
            capacity=capacity,
            responsible_person=responsible_person,
            commission_date=commission_date,
            notes=notes,
            created_at=utcnow(), 
            updated_at=utcnow()
        )
        session.add(pl)
        session.commit()
        logger.info(f"Production line created: {name}")
        return pl
    except AssetServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in asset_service.create_production_line: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in asset_service.create_production_line: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def list_production_lines(session: Session = None) -> List[ProductionLine]:
    """List all production lines"""
    session, should_close = _get_session(session)
    try:
        return session.query(ProductionLine).order_by(ProductionLine.name).all()
    except Exception as e:
        logger.error(f"Unexpected error in asset_service.list_production_lines: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def update_production_line(
    production_line_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    code: Optional[str] = None,
    status: Optional[str] = None,
    capacity: Optional[str] = None,
    responsible_person: Optional[str] = None,
    commission_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    session: Session = None
) -> ProductionLine:
    """Update a production line"""
    session, should_close = _get_session(session)
    try:
        pl = session.query(ProductionLine).filter_by(id=production_line_id).first()
        if not pl:
            raise AssetServiceError(get_localized_error("production_line_not_found"))
        
        # Check name uniqueness if name is being changed
        if name is not None and name != pl.name:
            existing = session.query(ProductionLine).filter(
                ProductionLine.name == name,
                ProductionLine.id != production_line_id
            ).first()
            if existing:
                raise AssetServiceError(get_localized_error("production_line_name_exists"))
            pl.name = name
        
        # Check code uniqueness if code is being changed
        if code is not None and code != pl.code:
            existing = session.query(ProductionLine).filter(
                ProductionLine.code == code,
                ProductionLine.id != production_line_id
            ).first()
            if existing:
                raise AssetServiceError(get_localized_error("production_line_code_exists"))
            pl.code = code
        
        if description is not None:
            pl.description = description
        if location is not None:
            pl.location = location
        if status is not None:
            pl.status = status
        if capacity is not None:
            pl.capacity = capacity
        if responsible_person is not None:
            pl.responsible_person = responsible_person
        if commission_date is not None:
            pl.commission_date = commission_date
        if notes is not None:
            pl.notes = notes
        
        pl.updated_at = utcnow()
        session.commit()
        logger.info(f"Production line updated: {production_line_id}")
        return pl
    except AssetServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in asset_service.update_production_line: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in asset_service.update_production_line: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def delete_production_line(production_line_id: int, session: Session = None) -> bool:
    """Delete a production line (only if it has no machines)"""
    session, should_close = _get_session(session)
    try:
        pl = session.query(ProductionLine).filter_by(id=production_line_id).first()
        if not pl:
            return False
        
        # Check if production line has machines
        machine_count = session.query(Machine).filter_by(production_line_id=production_line_id).count()
        if machine_count > 0:
            raise AssetServiceError(get_localized_error("production_line_has_machines"))
        
        pl_name = pl.name
        session.delete(pl)
        session.commit()
        
        # Log deletion
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id()
        try:
            log_action(
                category="asset",
                action_type="delete",
                entity_type="ProductionLine",
                entity_id=production_line_id,
                user_id=user_id,
                description=f"Termelési sor törölve: {pl_name}",
                metadata={
                    "production_line_name": pl_name,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging production line deletion: {e}")
        
        logger.info(f"Production line deleted: {production_line_id}")
        return True
    except AssetServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in asset_service.delete_production_line: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in asset_service.delete_production_line: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def create_machine(production_line_id: int, name: str, serial_number: Optional[str] = None,
                   model: Optional[str] = None, manufacturer: Optional[str] = None,
                   manual_pdf_path: Optional[str] = None, install_date: Optional[datetime] = None,
                   status: str = "Active", maintenance_interval: Optional[str] = None,
                   asset_tag: Optional[str] = None, purchase_date: Optional[datetime] = None,
                   purchase_price: Optional[float] = None, warranty_expiry_date: Optional[datetime] = None,
                   supplier: Optional[str] = None, operating_hours: Optional[float] = None,
                   last_service_date: Optional[datetime] = None, next_service_date: Optional[datetime] = None,
                   criticality_level: Optional[str] = None, energy_consumption: Optional[str] = None,
                   power_requirements: Optional[str] = None, operating_temperature_range: Optional[str] = None,
                   weight: Optional[float] = None, dimensions: Optional[str] = None, notes: Optional[str] = None,
                   created_by_user_id: Optional[int] = None,
                   operating_hours_update_frequency_type: Optional[str] = None,
                   operating_hours_update_frequency_value: Optional[int] = None,
                   session: Session = None) -> Machine:
    session, should_close = _get_session(session)
    try:
        pl = session.query(ProductionLine).filter_by(id=production_line_id).first()
        if not pl:
            raise AssetServiceError(get_localized_error("production_line_not_found"))
        if serial_number:
            if session.query(Machine).filter_by(serial_number=serial_number).first():
                raise AssetServiceError(get_localized_error("serial_number_exists"))
        if asset_tag:
            if session.query(Machine).filter_by(asset_tag=asset_tag).first():
                raise AssetServiceError(get_localized_error("asset_tag_exists"))
        machine = Machine(
            production_line_id=production_line_id,
            name=name,
            serial_number=serial_number,
            model=model,
            manufacturer=manufacturer,
            manual_pdf_path=manual_pdf_path,
            install_date=install_date,
            status=status,
            maintenance_interval=maintenance_interval,
            asset_tag=asset_tag,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            warranty_expiry_date=warranty_expiry_date,
            supplier=supplier,
            operating_hours=operating_hours or 0.0,
            last_service_date=last_service_date,
            next_service_date=next_service_date,
            criticality_level=criticality_level,
            energy_consumption=energy_consumption,
            power_requirements=power_requirements,
            operating_temperature_range=operating_temperature_range,
            weight=weight,
            dimensions=dimensions,
            notes=notes,
            version=1,
            created_by_user_id=created_by_user_id,
            operating_hours_update_frequency_type=operating_hours_update_frequency_type,
            operating_hours_update_frequency_value=operating_hours_update_frequency_value,
            last_operating_hours_update=None,
            updated_by_user_id=created_by_user_id,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        session.add(machine)
        session.flush()  # Flush to get machine.id
        
        # Logolás
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = created_by_user_id or get_current_user_id()
        try:
            log_action(
                category="asset",
                action_type="create",
                entity_type="Machine",
                entity_id=machine.id,
                user_id=user_id,
                description=f"Gép létrehozva: {name}",
                metadata={
                    "machine_name": name,
                    "serial_number": serial_number,
                    "manufacturer": manufacturer,
                    "model": model,
                    "production_line_id": production_line_id,
                    "purchase_price": purchase_price,
                    "status": status,
                    "install_date": str(install_date) if install_date else None,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging machine creation: {e}")
        
        # Log creation in asset history
        if created_by_user_id:
            hist = AssetHistory(
                machine_id=machine.id,
                action_type="created",
                description=f"Machine created: {name}",
                user_id=created_by_user_id,
                timestamp=utcnow(),
            )
            session.add(hist)
        
        session.commit()
        logger.info(f"Machine created: {name} (line {production_line_id}) by user {created_by_user_id}")
        return machine
    finally:
        if should_close:
            session.close()


def add_module(machine_id: int, name: str, description: Optional[str] = None,
               specifications: Optional[dict] = None, session: Session = None) -> Module:
    session, should_close = _get_session(session)
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise AssetServiceError(get_localized_error("machine_not_found"))
        module = Module(
            machine_id=machine_id,
            name=name,
            description=description,
            specifications=specifications or {},
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        session.add(module)
        session.commit()
        logger.info(f"Module added: {name} to machine {machine_id}")
        return module
    finally:
        if should_close:
            session.close()


def log_asset_history(machine_id: int, action_type: str, description: Optional[str] = None,
                      user_id: Optional[int] = None, session: Session = None) -> AssetHistory:
    session, should_close = _get_session(session)
    try:
        if action_type not in ASSET_ACTIONS:
            raise AssetServiceError(get_localized_error("invalid_asset_action_type"))
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise AssetServiceError(get_localized_error("machine_not_found"))
        hist = AssetHistory(
            machine_id=machine_id,
            action_type=action_type,
            description=description,
            user_id=user_id,
            timestamp=utcnow(),
        )
        session.add(hist)
        session.commit()
        logger.info(f"Asset history logged: machine={machine_id} action={action_type}")
        return hist
    except AssetServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in asset_service.log_asset_history: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in asset_service.log_asset_history: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_machine(machine_id: int, session: Session = None) -> Optional[Machine]:
    """Get machine by ID"""
    session, should_close = _get_session(session)
    try:
        return session.query(Machine).filter_by(id=machine_id).first()
    except Exception as e:
        logger.error(f"Unexpected error in asset_service.get_machine: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def list_modules_for_machine(machine_id: int, session: Session = None) -> List[Module]:
    """List all modules for a machine"""
    session, should_close = _get_session(session)
    try:
        return session.query(Module).filter_by(machine_id=machine_id).order_by(Module.name).all()
    except Exception as e:
        logger.error(f"Unexpected error in asset_service.list_modules_for_machine: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_machine_history(machine_id: int, session: Session = None) -> List[AssetHistory]:
    """Get asset history for a machine"""
    session, should_close = _get_session(session)
    try:
        return session.query(AssetHistory).filter_by(machine_id=machine_id).order_by(AssetHistory.timestamp.desc()).all()
    except Exception as e:
        logger.error(f"Unexpected error in asset_service.get_machine_history: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def update_module(module_id: int, name: Optional[str] = None, description: Optional[str] = None,
                 specifications: Optional[dict] = None, session: Session = None) -> Optional[Module]:
    """Update a module"""
    session, should_close = _get_session(session)
    try:
        module = session.query(Module).filter_by(id=module_id).first()
        if not module:
            return None
        
        if name is not None:
            module.name = name
        if description is not None:
            module.description = description
        if specifications is not None:
            module.specifications = specifications
        module.updated_at = utcnow()
        
        session.commit()
        logger.info(f"Module updated: {module_id}")
        return module
    finally:
        if should_close:
            session.close()


def delete_module(module_id: int, session: Session = None) -> bool:
    """Delete module with logging"""
    session, should_close = _get_session(session)
    try:
        module = session.query(Module).filter_by(id=module_id).first()
        if not module:
            return False
        
        # Get module info before deletion for logging
        module_name = module.name
        machine_id = module.machine_id
        
        session.delete(module)
        session.commit()
        
        # Logolás
        from services.log_service import log_action
        from services.context_service import get_current_user_id
        
        user_id = get_current_user_id()
        try:
            log_action(
                category="asset",
                action_type="delete",
                entity_type="Module",
                entity_id=module_id,
                user_id=user_id,
                description=f"Modul törölve: {module_name}",
                metadata={
                    "module_name": module_name,
                    "machine_id": machine_id,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging module deletion: {e}")
        
        logger.info(f"Module deleted: {module_id}")
        return True
    finally:
        if should_close:
            session.close()


def list_machines(production_line_id: Optional[int] = None, session: Session = None) -> List[Machine]:
    """List machines, optionally filtered by production line"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        query = session.query(Machine).options(
            joinedload(Machine.production_line),
            joinedload(Machine.id_compatible_parts)
        )
        if production_line_id:
            query = query.filter_by(production_line_id=production_line_id)
        return query.all()
    except Exception as e:
        logger.error(f"Unexpected error in asset_service.list_machines: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def update_machine(
    machine_id: int,
    name: Optional[str] = None,
    production_line_id: Optional[int] = None,
    serial_number: Optional[str] = None,
    model: Optional[str] = None,
    manufacturer: Optional[str] = None,
    manual_pdf_path: Optional[str] = None,
    install_date: Optional[datetime] = None,
    status: Optional[str] = None,
    maintenance_interval: Optional[str] = None,
    asset_tag: Optional[str] = None, purchase_date: Optional[datetime] = None,
    purchase_price: Optional[float] = None, warranty_expiry_date: Optional[datetime] = None,
    supplier: Optional[str] = None, operating_hours: Optional[float] = None,
    last_service_date: Optional[datetime] = None, next_service_date: Optional[datetime] = None,
    criticality_level: Optional[str] = None, energy_consumption: Optional[str] = None,
    power_requirements: Optional[str] = None, operating_temperature_range: Optional[str] = None,
    weight: Optional[float] = None, dimensions: Optional[str] = None, notes: Optional[str] = None,
    updated_by_user_id: Optional[int] = None, change_description: Optional[str] = None,
    operating_hours_update_frequency_type: Optional[str] = None,
    operating_hours_update_frequency_value: Optional[int] = None,
    session: Session = None,
) -> Machine:
    """Update machine with automatic version tracking"""
    session, should_close = _get_session(session)
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise AssetServiceError(get_localized_error("machine_not_found"))
        
        # Track changes for version history
        changed_fields = {}
        field_mapping = {
            'name': name,
            'production_line_id': production_line_id,
            'serial_number': serial_number,
            'model': model,
            'manufacturer': manufacturer,
            'manual_pdf_path': manual_pdf_path,
            'install_date': install_date,
            'status': status,
            'maintenance_interval': maintenance_interval,
            'asset_tag': asset_tag,
            'purchase_date': purchase_date,
            'purchase_price': purchase_price,
            'warranty_expiry_date': warranty_expiry_date,
            'supplier': supplier,
            'operating_hours': operating_hours,
            'last_service_date': last_service_date,
            'next_service_date': next_service_date,
            'criticality_level': criticality_level,
            'energy_consumption': energy_consumption,
            'power_requirements': power_requirements,
            'operating_temperature_range': operating_temperature_range,
            'weight': weight,
            'dimensions': dimensions,
            'notes': notes,
            'operating_hours_update_frequency_type': operating_hours_update_frequency_type,
            'operating_hours_update_frequency_value': operating_hours_update_frequency_value,
        }
        
        # Special handling for status field - validate workflow transition BEFORE applying changes
        if status is not None and machine.status != status:
            from services.workflow_service import transition_state
            from utils.error_handler import StateTransitionError
            from utils.localization_helper import get_localized_error
            
            # Validate state transition
            try:
                transition_state("machine", machine.status, status, raise_on_error=True)
            except StateTransitionError as e:
                raise AssetServiceError(
                    get_localized_error("invalid_status_transition", 
                                      old_status=machine.status, 
                                      new_status=status) or 
                    f"Invalid status transition: {machine.status} -> {status}"
                )
        
        # Apply changes and track what changed
        for field_name, new_value in field_mapping.items():
            if new_value is not None:
                old_value = getattr(machine, field_name)
                if old_value != new_value:
                    changed_fields[field_name] = {
                        'old': str(old_value) if old_value is not None else None,
                        'new': str(new_value) if new_value is not None else None
                    }
                    setattr(machine, field_name, new_value)
        
        # Special handling for production_line_id
        if production_line_id is not None:
            pl = session.query(ProductionLine).filter_by(id=production_line_id).first()
            if not pl:
                raise AssetServiceError(get_localized_error("production_line_not_found"))
        
        # Check serial number uniqueness
        if serial_number is not None:
            existing = session.query(Machine).filter(
                Machine.serial_number == serial_number,
                Machine.id != machine_id
            ).first()
            if existing:
                raise AssetServiceError(get_localized_error("serial_number_exists"))
        
        # Check asset_tag uniqueness
        if asset_tag is not None:
            existing = session.query(Machine).filter(
                Machine.asset_tag == asset_tag,
                Machine.id != machine_id
            ).first()
            if existing:
                raise AssetServiceError(get_localized_error("asset_tag_exists"))
        
        # If there are changes, create version history
        if changed_fields and updated_by_user_id:
            machine.version += 1
            machine.updated_by_user_id = updated_by_user_id
            
            # Create version record
            version = MachineVersion(
                machine_id=machine.id,
                version=machine.version,
                changed_fields=changed_fields,
                changed_by_user_id=updated_by_user_id,
                change_description=change_description or f"Updated {len(changed_fields)} field(s)",
                timestamp=utcnow(),
            )
            session.add(version)
            
            # Log in asset history
            changed_field_names = ', '.join(changed_fields.keys())
            hist = AssetHistory(
                machine_id=machine.id,
                action_type="modified",
                description=f"Modified fields: {changed_field_names}",
                user_id=updated_by_user_id,
                timestamp=utcnow(),
            )
            session.add(hist)
        
        machine.updated_at = utcnow()
        session.commit()
        
        # Logolás, ha volt változás
        if changed_fields:
            from services.log_service import log_action
            from services.context_service import get_current_user_id
            
            user_id = updated_by_user_id or get_current_user_id()
            try:
                log_action(
                    category="asset",
                    action_type="update",
                    entity_type="Machine",
                    entity_id=machine_id,
                    user_id=user_id,
                    description=f"Gép módosítva: {machine.name}",
                    metadata={"changes": changed_fields, "change_reason": change_description, "change_description": change_description},
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error logging machine update: {e}")
        
        logger.info(f"Gép frissítve: {machine.name} (verzió {machine.version}) by user {updated_by_user_id}")
        return machine
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in asset_service.update_machine: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in asset_service.update_machine: {e}", exc_info=True)
        raise
    except (StateTransitionError, AssetServiceError) as e:
        session.rollback()
        logger.warning(f"Business logic error in asset_service.update_machine: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in asset_service.update_machine: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def get_machines_with_upcoming_service(
    days_ahead: int = 30,
    session: Session = None
) -> List[Machine]:
    """Get machines with upcoming service dates within specified days"""
    session, should_close = _get_session(session)
    try:
        from datetime import datetime, timedelta
        from sqlalchemy.orm import joinedload
        
        cutoff_date = utcnow() + timedelta(days=days_ahead)
        return session.query(Machine).options(
            joinedload(Machine.production_line),
        ).filter(
            Machine.next_service_date.isnot(None),
            Machine.next_service_date <= cutoff_date,
            Machine.status != MACHINE_STATUS_SCRAPPED
        ).order_by(Machine.next_service_date.asc()).all()
    finally:
        if should_close:
            session.close()


def get_machine_versions(machine_id: int, session: Session = None) -> List[MachineVersion]:
    """Get version history for a machine"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        return session.query(MachineVersion).options(
            joinedload(MachineVersion.changed_by_user)
        ).filter_by(machine_id=machine_id).order_by(MachineVersion.version.desc()).all()
    finally:
        if should_close:
            session.close()


def update_operating_hours(
    machine_id: int,
    new_operating_hours: float,
    notes: Optional[str] = None,
    user_id: Optional[int] = None,
    session: Session = None
) -> Machine:
    """Update operating hours for a machine and log the correction"""
    session, should_close = _get_session(session)
    try:
        from services.context_service import get_current_user_id
        from services.log_service import log_action
        from datetime import datetime
        
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise AssetServiceError(get_localized_error("machine_not_found"))
        
        old_hours = machine.operating_hours or 0.0
        machine.operating_hours = new_operating_hours
        machine.last_operating_hours_update = utcnow()
        machine.updated_at = utcnow()
        
        # Get user ID
        if not user_id:
            try:
                user_id = get_current_user_id()
            except Exception:
                logger.warning("Could not get current user ID for operating hours update")
        
        # Log the correction
        try:
            log_action(
                category="asset",
                action_type="operating_hours_correction",
                entity_type="Machine",
                entity_id=machine_id,
                user_id=user_id,
                description=f"Üzemóra korrekció: {machine.name} - {old_hours:.2f} → {new_operating_hours:.2f} óra",
                metadata={
                    "old_operating_hours": old_hours,
                    "new_operating_hours": new_operating_hours,
                    "difference": new_operating_hours - old_hours,
                    "notes": notes,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging operating hours correction: {e}")
        
        session.commit()
        session.refresh(machine)
        logger.info(f"Updated operating hours for machine {machine_id}: {old_hours} → {new_operating_hours}")
        return machine
    finally:
        if should_close:
            session.close()


def get_operating_hours_history(machine_id: int, limit: int = 10, session: Session = None) -> List[dict]:
    """Get operating hours correction history for a machine"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        from sqlalchemy import desc
        from database.models import SystemLog
        
        # Query SystemLog directly with entity_id filter
        query = session.query(SystemLog).options(joinedload(SystemLog.user))
        query = query.filter(
            SystemLog.log_category == "asset",
            SystemLog.entity_type == "Machine",
            SystemLog.entity_id == machine_id,
            SystemLog.action_type == "operating_hours_correction"
        )
        query = query.order_by(desc(SystemLog.timestamp))
        query = query.limit(limit)
        
        logs = query.all()
        
        # Convert to dictionary format
        corrections = []
        for log in logs:
            metadata = log.log_metadata or {}
            corrections.append({
                "id": log.id,
                "timestamp": log.timestamp,
                "user_id": log.user_id,
                "user_name": log.user.username if log.user else None,
                "old_hours": metadata.get("old_operating_hours", 0.0),
                "new_hours": metadata.get("new_operating_hours", 0.0),
                "difference": metadata.get("difference", 0.0),
                "notes": metadata.get("notes"),
                "description": log.description,
            })
        
        return corrections
    finally:
        if should_close:
            session.close()


def calculate_next_operating_hours_update_date(machine: Machine) -> Optional[datetime]:
    """Calculate the next operating hours update date based on machine settings"""
    if not machine.operating_hours_update_frequency_type or not machine.operating_hours_update_frequency_value:
        return None
    
    last_update = machine.last_operating_hours_update
    if not last_update:
        return None
    
    freq_type = machine.operating_hours_update_frequency_type
    freq_value = machine.operating_hours_update_frequency_value
    
    if freq_type == "day":
        next_date = last_update + timedelta(days=freq_value)
    elif freq_type == "week":
        next_date = last_update + timedelta(weeks=freq_value)
    elif freq_type == "month":
        # Approximate month calculation
        next_date = last_update + timedelta(days=freq_value * 30)
    else:
        return None
    
    return next_date


def get_machines_with_due_operating_hours_update(session: Session = None) -> List[dict]:
    """Get machines that need operating hours update based on their frequency settings"""
    session, should_close = _get_session(session)
    try:
        from datetime import datetime, timedelta
        from sqlalchemy.orm import joinedload
        from services.settings_service import get_operating_hours_notification_settings
        
        now = utcnow()
        if isinstance(now, datetime):
            current_time = now
        else:
            current_time = datetime.now()
        
        # Get notification settings
        notif_settings = get_operating_hours_notification_settings(session)
        days_ahead = (
            notif_settings['months_ahead'] * 30 +
            notif_settings['weeks_ahead'] * 7 +
            notif_settings['days_ahead'] +
            notif_settings['hours_ahead'] / 24
        )
        
        machines = session.query(Machine).options(
            joinedload(Machine.production_line),
        ).filter(
            Machine.operating_hours_update_frequency_type.isnot(None),
            Machine.operating_hours_update_frequency_value.isnot(None),
            Machine.status != MACHINE_STATUS_SCRAPPED
        ).all()
        
        due_machines = []
        
        for machine in machines:
            if not machine.last_operating_hours_update:
                # Never updated, consider it due
                due_machines.append({
                    'machine': machine,
                    'next_update_date': current_time,
                    'is_overdue': True,
                })
                continue
            
            # Calculate next update date based on frequency
            last_update = machine.last_operating_hours_update
            if isinstance(last_update, datetime):
                last_update_dt = last_update
            else:
                last_update_dt = datetime.fromisoformat(str(last_update)) if isinstance(last_update, str) else current_time
            
            frequency_type = machine.operating_hours_update_frequency_type
            frequency_value = machine.operating_hours_update_frequency_value or 1
            
            if frequency_type == 'day':
                next_update = last_update_dt + timedelta(days=frequency_value)
            elif frequency_type == 'week':
                next_update = last_update_dt + timedelta(weeks=frequency_value)
            elif frequency_type == 'month':
                # Approximate month as 30 days
                next_update = last_update_dt + timedelta(days=frequency_value * 30)
            else:
                continue
            
            # Check if update is due within notification period
            notification_cutoff = current_time + timedelta(days=days_ahead)
            if next_update <= notification_cutoff:
                due_machines.append({
                    'machine': machine,
                    'next_update_date': next_update,
                    'is_overdue': next_update < current_time,
                })
        
        # Sort by next update date (overdue first)
        due_machines.sort(key=lambda x: (not x['is_overdue'], x['next_update_date']))
        return due_machines
    finally:
        if should_close:
            session.close()


def get_machine_with_history(machine_id: int, session: Session = None) -> Optional[Machine]:
    """Get machine with version history and asset history"""
    session, should_close = _get_session(session)
    try:
        from sqlalchemy.orm import joinedload
        return session.query(Machine).options(
            joinedload(Machine.production_line),
            joinedload(Machine.id_compatible_parts),
            joinedload(Machine.machine_versions).joinedload(MachineVersion.changed_by_user),
            joinedload(Machine.asset_history).joinedload(AssetHistory.user),
            joinedload(Machine.created_by_user),
            joinedload(Machine.updated_by_user),
        ).filter_by(id=machine_id).first()
    except Exception as e:
        logger.error(f"Unexpected error in asset_service.get_machine_with_history: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def scrap_machine(machine_id: int, scrapped_by_user_id: Optional[int] = None, 
                  scrapping_reason: Optional[str] = None, scrapping_cost: Optional[float] = None,
                  session: Session = None) -> bool:
    """
    Scrap machine (ISO 55001 compliant - soft delete)
    Sets status to 'Selejtezve' instead of hard delete
    """
    session, should_close = _get_session(session)
    try:
        machine = session.query(Machine).filter_by(id=machine_id).first()
        if not machine:
            raise AssetServiceError(get_localized_error("machine_not_found"))
        
        # Check if already scrapped
        if machine.status == MACHINE_STATUS_SCRAPPED:
            raise AssetServiceError(get_localized_error("machine_already_scrapped"))
        
        # Check if machine has active worksheets
        from database.models import Worksheet
        from config.constants import WORKSHEET_STATUS_OPEN, WORKSHEET_STATUS_WAITING
        active_worksheets = session.query(Worksheet).filter(
            Worksheet.machine_id == machine_id,
            Worksheet.status.in_([WORKSHEET_STATUS_OPEN, WORKSHEET_STATUS_WAITING])
        ).count()
        if active_worksheets > 0:
            raise AssetServiceError(get_localized_error("machine_has_active_worksheets"))
        
        # Get machine info before status change for logging
        machine_name = machine.name
        machine_serial = machine.serial_number or machine.asset_tag or f"ID: {machine.id}"
        
        # Set status to scrapped (soft delete) and lifecycle fields
        machine.status = MACHINE_STATUS_SCRAPPED
        machine.scrapping_date = utcnow()
        if scrapping_reason:
            machine.scrapping_reason = scrapping_reason
        if scrapping_cost is not None:
            machine.scrapping_cost = scrapping_cost
        
        # Log scrapping in asset history
        if scrapped_by_user_id:
            hist = AssetHistory(
                machine_id=machine_id,
                action_type="deleted",
                description=f"Machine scrapped: {machine.name}",
                user_id=scrapped_by_user_id,
                timestamp=utcnow(),
            )
            session.add(hist)
        
        session.commit()
        
        # Generate scrapping document if auto-generate is enabled
        from services.settings_service import get_auto_generate_scrapping_doc
        from services.scrapping_service import generate_scrapping_document
        from services.log_service import log_action
        
        if get_auto_generate_scrapping_doc():
            try:
                generate_scrapping_document(
                    entity_type="Machine",
                    entity_id=machine_id,
                    reason="Gép selejtezése",
                    session=session
                )
            except Exception as e:
                logger.warning(f"Error generating scrapping document for machine {machine_id}: {e}")
        
        # Log the scrapping action
        try:
            log_action(
                category="asset",
                action_type="scrap",
                entity_type="Machine",
                entity_id=machine_id,
                user_id=scrapped_by_user_id,
                description=f"Gép selejtezve: {machine_name} (Sorozatszám: {machine_serial})",
                metadata={
                    "machine_name": machine_name,
                    "machine_serial": machine_serial,
                    "status": MACHINE_STATUS_SCRAPPED,
                },
                session=session
            )
        except Exception as e:
            logger.warning(f"Error logging machine scrapping: {e}")
        
        logger.info(f"Gép selejtezve: {machine_id} ({machine.name}) by user {scrapped_by_user_id}")
        return True
    except AssetServiceError as e:
        session.rollback()
        logger.warning(f"Business logic error in asset_service.scrap_machine: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in asset_service.scrap_machine: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()


def delete_machine(machine_id: int, deleted_by_user_id: Optional[int] = None, session: Session = None) -> bool:
    """
    Delete machine (deprecated - ISO 55001 compliant version uses scrap_machine)
    This function now calls scrap_machine() to comply with ISO 55001
    """
    # For backward compatibility, redirect to scrap_machine
    return scrap_machine(machine_id, scrapped_by_user_id=deleted_by_user_id, session=session)
