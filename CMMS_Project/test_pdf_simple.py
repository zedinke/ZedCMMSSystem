#!/usr/bin/env python3
"""Direct PDF generation test - use existing worksheet"""
import sys, os
os.chdir('E:/Artence_CMMS/CMMS_Project')
sys.path.insert(0, '.')

from database.models import Worksheet
from services.worksheet_service import _get_session
from services.pdf_service import generate_worksheet_pdf

session, _ = _get_session(None)

# Get first worksheet or create test data via service
worksheets = session.query(Worksheet).all()
print(f"Found {len(worksheets)} worksheets")

if worksheets:
    ws_id = worksheets[0].id
    print(f"Testing PDF generation for worksheet {ws_id}")
    
    try:
        pdf_path = generate_worksheet_pdf(ws_id, generated_by='test_user')
        print(f'SUCCESS - PDF generated: {pdf_path}')
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path)
            print(f'File size: {size} bytes')
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
else:
    print("No worksheets found in database. Create one first in the UI.")
