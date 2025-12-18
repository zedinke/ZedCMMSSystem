#!/usr/bin/env python3
"""Test PDF generation"""
import sys
sys.path.insert(0, '.')

from database.models import Worksheet, Machine, ProductionLine
from services.worksheet_service import _get_session
from datetime import datetime, timedelta

session, _ = _get_session(None)

# Create test data
prod_line = session.query(ProductionLine).first()
if not prod_line:
    prod_line = ProductionLine(name='Test Line')
    session.add(prod_line)
    session.flush()

machine = session.query(Machine).first()
if not machine:
    machine = Machine(name='Test Machine', production_line_id=prod_line.id, serial_number='SN123')
    session.add(machine)
    session.flush()

# Create worksheet
ws = Worksheet(
    machine_id=machine.id,
    status='Open',
    breakdown_time=datetime.now() - timedelta(hours=2),
    repair_finished_time=datetime.now(),
    notes='Test worksheet'
)
session.add(ws)
session.commit()
print(f'Created worksheet {ws.id}')

# Test PDF generation
from services.pdf_service import generate_worksheet_pdf
try:
    pdf_path = generate_worksheet_pdf(ws.id, generated_by='test_user')
    print(f'PDF generated: {pdf_path}')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
