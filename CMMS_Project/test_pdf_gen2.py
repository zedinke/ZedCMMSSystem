#!/usr/bin/env python3
"""Direct PDF generation test"""
import sys, os
os.chdir('E:/Artence_CMMS/CMMS_Project')
sys.path.insert(0, '.')

from database.models import Worksheet, Machine, ProductionLine, Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Initialize DB
db_path = 'data/cmms.db'
engine = create_engine(f'sqlite:///{db_path}', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Get or create admin user
admin = session.query(User).filter_by(username='admin').first()
if not admin:
    from services.auth_service import hash_password
    admin = User(username='admin', password_hash=hash_password('admin'))
    session.add(admin)
    session.flush()

# Get or create test data
prod_line = session.query(ProductionLine).first()
if not prod_line:
    prod_line = ProductionLine(name='Test Line')
    session.add(prod_line)
    session.flush()

machine = session.query(Machine).first()
if not machine:
    machine = Machine(name='Test Machine', production_line_id=prod_line.id, serial_number='SN123', manufacturer='TestMfg', model='Model-X')
    session.add(machine)
    session.flush()

# Create worksheet
try:
    ws = Worksheet(
        machine_id=machine.id,
        assigned_to_user_id=admin.id,
        status='Open',
        breakdown_time=datetime.now() - timedelta(hours=2),
        repair_finished_time=datetime.now(),
        notes='Test worksheet for PDF generation'
    )
    session.add(ws)
    session.commit()
    print(f'Created worksheet {ws.id}')
    ws_id = ws.id
except Exception as e:
    print(f'ERROR creating worksheet: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test PDF generation
from services.pdf_service import generate_worksheet_pdf
try:
    pdf_path = generate_worksheet_pdf(ws_id, generated_by='test_user')
    print(f'SUCCESS - PDF generated: {pdf_path}')
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f'File size: {size} bytes')
except Exception as e:
    print(f'ERROR generating PDF: {e}')
    import traceback
    traceback.print_exc()
finally:
    session.close()
