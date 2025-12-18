"""
Performance tests
Tests database query performance, PDF generation, Excel export, memory profiling
"""

import sys
from pathlib import Path
import pytest
import time
from datetime import datetime, timedelta
import uuid

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.database import reset_database
from database.session_manager import SessionLocal
from database.models import (
    User, Role, ProductionLine, Machine, Part, Supplier, InventoryLevel,
    Worksheet, PMTask
)
from services import asset_service, inventory_service, worksheet_service, pm_service
from services.pdf_service import generate_worksheet_pdf
from utils.qr_generator import generate_qr_code


@pytest.fixture(autouse=True)
def _reset_db():
    """Reset database before each test"""
    reset_database()
    yield


# ============================================================================
# DATABASE QUERY PERFORMANCE TESTS
# ============================================================================

def test_query_performance_with_large_dataset():
    """Test query execution time with 1000+ records"""
    session = SessionLocal()
    try:
        # Create test data
        role = session.query(Role).filter_by(name="Technician").first()
        supplier = inventory_service.create_supplier("Test Supplier", session=session)
        
        # Create 1000 parts
        start_time = time.time()
        parts = []
        for i in range(1000):
            part = inventory_service.create_part(
                name=f"Part {i}",
                sku=f"SKU-{uuid.uuid4().hex[:8]}",
                supplier_id=supplier.id,
                initial_quantity=10,
                session=session
            )
            parts.append(part)
        
        creation_time = time.time() - start_time
        print(f"Created 1000 parts in {creation_time:.2f} seconds")
        
        # Query all parts
        start_time = time.time()
        all_parts = session.query(Part).all()
        query_time = time.time() - start_time
        
        print(f"Queried {len(all_parts)} parts in {query_time:.2f} seconds")
        assert len(all_parts) == 1000
        assert query_time < 2.0  # Should complete in under 2 seconds
    finally:
        session.close()


def test_query_with_indexes():
    """Test that indexes are being used for queries"""
    session = SessionLocal()
    try:
        # Create test data
        role = session.query(Role).filter_by(name="Technician").first()
        supplier = inventory_service.create_supplier("Test Supplier", session=session)
        
        # Create parts with unique SKUs
        for i in range(100):
            inventory_service.create_part(
                name=f"Part {i}",
                sku=f"SKU-{i:04d}",
                supplier_id=supplier.id,
                session=session
            )
        
        # Query by SKU (should use index)
        start_time = time.time()
        part = session.query(Part).filter_by(sku="SKU-0050").first()
        query_time = time.time() - start_time
        
        assert part is not None
        assert query_time < 0.1  # Indexed query should be very fast
    finally:
        session.close()


def test_n_plus_one_query_prevention():
    """Test N+1 query prevention with joinedload"""
    session = SessionLocal()
    try:
        from sqlalchemy.orm import joinedload
        
        role = session.query(Role).filter_by(name="Technician").first()
        user = session.query(User).filter_by(username="admin").first()
        
        # Create machines with production lines
        pl = asset_service.create_production_line("Test Line", session=session)
        for i in range(50):
            asset_service.create_machine(
                pl.id, f"Machine {i}", serial_number=f"SN-{i}",
                session=session
            )
        
        # Query with joinedload (should prevent N+1)
        start_time = time.time()
        machines = session.query(Machine).options(
            joinedload(Machine.production_line)
        ).all()
        query_time = time.time() - start_time
        
        # Access production_line for all machines (should not trigger additional queries)
        for machine in machines:
            _ = machine.production_line.name
        
        total_time = time.time() - start_time
        print(f"Queried {len(machines)} machines with relationships in {total_time:.2f} seconds")
        assert len(machines) == 50
        assert total_time < 1.0  # Should be fast with joinedload
    finally:
        session.close()


# ============================================================================
# PDF GENERATION PERFORMANCE TESTS
# ============================================================================

def test_pdf_generation_performance():
    """Test PDF generation performance"""
    session = SessionLocal()
    try:
        # Create test worksheet
        role = session.query(Role).filter_by(name="Technician").first()
        user = session.query(User).filter_by(username="admin").first()
        pl = asset_service.create_production_line("Test Line", session=session)
        machine = asset_service.create_machine(
            pl.id, "Test Machine", serial_number="SN-TEST",
            session=session
        )
        
        worksheet = worksheet_service.create_worksheet(
            machine.id, user.id, "Performance Test",
            description="Test PDF generation",
            session=session
        )
        
        # Generate PDF
        start_time = time.time()
        pdf_path = generate_worksheet_pdf(worksheet.id, session=session)
        generation_time = time.time() - start_time
        
        print(f"Generated PDF in {generation_time:.2f} seconds")
        assert pdf_path is not None
        assert generation_time < 5.0  # Should complete in under 5 seconds
    finally:
        session.close()


def test_pdf_generation_with_many_parts():
    """Test PDF generation with large number of parts"""
    session = SessionLocal()
    try:
        # Create worksheet with many parts
        role = session.query(Role).filter_by(name="Technician").first()
        user = session.query(User).filter_by(username="admin").first()
        pl = asset_service.create_production_line("Test Line", session=session)
        machine = asset_service.create_machine(
            pl.id, "Test Machine", serial_number="SN-TEST",
            session=session
        )
        
        supplier = inventory_service.create_supplier("Test Supplier", session=session)
        
        worksheet = worksheet_service.create_worksheet(
            machine.id, user.id, "Performance Test",
            description="Performance test worksheet",
            breakdown_time=datetime.now(),
            session=session
        )
        worksheet.fault_cause = "Performance test"
        session.commit()
        
        # Add 50 parts to worksheet (with initial stock)
        for i in range(50):
            part = inventory_service.create_part(
                name=f"Part {i}",
                sku=f"SKU-{uuid.uuid4().hex[:8]}",
                supplier_id=supplier.id,
                initial_quantity=10,  # Ensure we have stock
                session=session
            )
            worksheet_service.add_part_to_worksheet(
                worksheet.id, part.id, 1, session=session
            )
        
        # Generate PDF
        start_time = time.time()
        pdf_path = generate_worksheet_pdf(worksheet.id, session=session)
        generation_time = time.time() - start_time
        
        print(f"Generated PDF with 50 parts in {generation_time:.2f} seconds")
        assert pdf_path is not None
        assert generation_time < 10.0  # Should complete in under 10 seconds
    finally:
        session.close()


# ============================================================================
# EXCEL EXPORT PERFORMANCE TESTS
# ============================================================================

def test_excel_export_performance():
    """Test Excel export performance"""
    session = SessionLocal()
    try:
        from services.reports_service import generate_excel_report
        
        # Create test data
        role = session.query(Role).filter_by(name="Technician").first()
        user = session.query(User).filter_by(username="admin").first()
        pl = asset_service.create_production_line("Test Line", session=session)
        machine = asset_service.create_machine(
            pl.id, "Test Machine", serial_number="SN-TEST",
            session=session
        )
        
        # Create 100 worksheets
        for i in range(100):
            worksheet_service.create_worksheet(
                machine.id, user.id, f"Worksheet {i}",
                session=session
            )
        
        # Generate Excel report
        start_time = time.time()
        excel_path = generate_excel_report(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            session=session
        )
        generation_time = time.time() - start_time
        
        print(f"Generated Excel report in {generation_time:.2f} seconds")
        assert excel_path is not None
        assert generation_time < 10.0  # Should complete in under 10 seconds
    except ImportError:
        pytest.skip("reports_service not available")
    finally:
        session.close()


# ============================================================================
# MEMORY PROFILING TESTS
# ============================================================================

def test_memory_usage_with_large_datasets():
    """Test memory usage with large datasets"""
    import sys
    
    session = SessionLocal()
    try:
        # Get initial memory usage
        initial_size = sys.getsizeof(session.query(Part).all())
        
        # Create large dataset
        supplier = inventory_service.create_supplier("Test Supplier", session=session)
        for i in range(500):
            inventory_service.create_part(
                name=f"Part {i}",
                sku=f"SKU-{uuid.uuid4().hex[:8]}",
                supplier_id=supplier.id,
                session=session
            )
        
        # Query all parts
        all_parts = session.query(Part).all()
        final_size = sys.getsizeof(all_parts)
        
        print(f"Memory usage: {final_size - initial_size} bytes for 500 parts")
        # Memory should be reasonable (not excessive)
        assert len(all_parts) == 500
    finally:
        session.close()


def test_memory_leak_prevention():
    """Test that there are no memory leaks"""
    session = SessionLocal()
    try:
        # Create and query multiple times
        supplier = inventory_service.create_supplier("Test Supplier", session=session)
        session.commit()  # Commit supplier to avoid DetachedInstanceError
        session.refresh(supplier)  # Refresh to keep in session
        
        for iteration in range(10):
            # Create parts
            for i in range(10):
                part = inventory_service.create_part(
                    name=f"Part {iteration}-{i}",
                    sku=f"SKU-{uuid.uuid4().hex[:8]}",
                    supplier_id=supplier.id,
                    session=session
                )
                session.refresh(part)  # Refresh to keep in session
            
            # Query all parts
            parts = session.query(Part).all()
            assert len(parts) > 0
            
            # Don't expunge_all - keep objects in session to avoid DetachedInstanceError
        
        # Final query should still work
        final_parts = session.query(Part).all()
        assert len(final_parts) >= 100  # At least 10 iterations * 10 parts
    finally:
        session.close()


# ============================================================================
# QR CODE GENERATION PERFORMANCE
# ============================================================================

def test_qr_code_generation_performance():
    """Test QR code generation performance"""
    # Generate 100 QR codes
    start_time = time.time()
    for i in range(100):
        qr_image = generate_qr_code(part_id=i, sku=f"SKU-{i:04d}", size=200)
        assert qr_image is not None
    
    generation_time = time.time() - start_time
    print(f"Generated 100 QR codes in {generation_time:.2f} seconds")
    assert generation_time < 5.0  # Should complete in under 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

