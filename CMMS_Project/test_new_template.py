
import sys
import os
from unittest.mock import patch
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.getcwd())

from database.models import Worksheet, Machine, ProductionLine
from services.worksheet_service import _get_session
from services.pdf_service import generate_worksheet_pdf
from datetime import datetime, timedelta

def test_template_generation():
    print("Starting template verification...")
    
    if not Path("generated_worksheet_template.docx").exists():
        print("Error: generated_worksheet_template.docx not found!")
        return

    session, _ = _get_session(None)
    try:
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
        
        # Create role if needed
        from database.models import User, Role
        role = session.query(Role).first()
        if not role:
            role = Role(name='TestRole', permissions={})
            session.add(role)
            session.flush()

        # Create user if needed
        user = session.query(User).first()
        if not user:
            user = User(
                username='test_verifier', 
                email='test@example.com', 
                password_hash='hash', 
                role_id=role.id,
                is_active=True
            )
            session.add(user)
            session.flush()

        # Create worksheet
        ws = Worksheet(
            machine_id=machine.id,
            assigned_to_user_id=user.id,
            title='Test Worksheet Title', # Also required per model? let's check. Yes, title is nullable=False
            status='Open',
            breakdown_time=datetime.now() - timedelta(hours=2),
            repair_finished_time=datetime.now(),
            notes='Test worksheet verification'
        )
        session.add(ws)
        session.commit()
        print(f'Created temporary worksheet {ws.id}')

        # Patch the function imported inside generate_worksheet_pdf
        # Note: Since it is imported inside the function as "from services.settings_service import ...",
        # we might need to patch 'services.settings_service.get_selected_worksheet_template' globally if the module is already loaded,
        # or patch where it is used.
        # But since it is a function-local import, verifying the patch target is tricky if we don't know if the module was already loaded.
        # However, sys.modules cache should make it consistent.
        
        with patch('services.settings_service.get_selected_worksheet_template') as mock_get:
            mock_get.return_value = Path("generated_worksheet_template.docx").resolve()
            
            print(f"Testing with template: {mock_get.return_value}")
            pdf_path = generate_worksheet_pdf(ws.id, generated_by='test_verifier')
            print(f'PDF generated successfully: {pdf_path}')
            
            if os.path.exists(pdf_path):
                print("VERIFICATION SUCCESSFUL: PDF exists along with the new template logic.")
            else:
                print("VERIFICATION FAILED: PDF path returned but file not found.")

    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_template_generation()
