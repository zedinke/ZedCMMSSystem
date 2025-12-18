
import sys
import os
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.models import Base, Machine, Part
from services import asset_service, inventory_service

class TestBackendChanges(unittest.TestCase):
    def setUp(self):
        # In-memory database
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_machine_with_new_fields(self):
        # Create Production Line first
        pl = asset_service.create_production_line("Line 1", session=self.session)
        
        # Create Machine with new fields
        install_date = datetime(2023, 1, 15)
        machine = asset_service.create_machine(
            production_line_id=pl.id,
            name="Test Machine",
            serial_number="SN123",
            install_date=install_date,
            status="Stopped",
            maintenance_interval="Monthly",
            session=self.session
        )

        # Verify fields
        self.assertEqual(machine.install_date, install_date)
        self.assertEqual(machine.status, "Stopped")
        self.assertEqual(machine.maintenance_interval, "Monthly")

    def test_create_part_with_unit_and_compatibility(self):
        # Setup Machines
        pl = asset_service.create_production_line("Line 1", session=self.session)
        m1 = asset_service.create_machine(pl.id, "Machine 1", serial_number="M1", session=self.session)
        m2 = asset_service.create_machine(pl.id, "Machine 2", serial_number="M2", session=self.session)

        # Create Part with unit and compatible machines
        part = inventory_service.create_part(
            sku="SKU001",
            name="Test Part",
            unit="kg",
            compatible_machine_ids=[m1.id, m2.id],
            session=self.session
        )

        # Verify Unit
        self.assertEqual(part.unit, "kg")

        # Verify Compatibility
        self.assertEqual(len(part.compatible_machines), 2)
        compatible_ids = [m.id for m in part.compatible_machines]
        self.assertIn(m1.id, compatible_ids)
        self.assertIn(m2.id, compatible_ids)

if __name__ == '__main__':
    unittest.main()
