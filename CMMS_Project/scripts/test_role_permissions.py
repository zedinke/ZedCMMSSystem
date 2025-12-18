"""
Test script to verify role-based permission system
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services import user_service
from utils.permissions import *
from config.roles import *

def test_permissions():
    print("=== Testing Role-Based Permission System ===\n")
    
    from database.session_manager import SessionLocal
    session = SessionLocal()
    
    try:
        # Clean up any leftover test users first
        for username in ["test_manager", "test_tech"]:
            existing = session.query(user_service.User).filter_by(username=username).first()
            if existing:
                session.delete(existing)
        session.commit()
        
        # Get admin user (should be Developer)
        admin = session.query(user_service.User).first()
        print(f"Admin user: {admin.username}")
        print(f"Role: {admin.role.name}")
        print(f"Must change password: {admin.must_change_password}")
        print(f"Permissions: {admin.role.permissions}")
        print()
        
        # Test Developer permissions
        print("Developer Permissions:")
        print(f"  - can_view_dashboard: {can_view_dashboard(admin)}")
        print(f"  - can_manage_users: {can_manage_users(admin)}")
        print(f"  - can_view_developer_tools: {can_view_developer_tools(admin)}")
        print(f"  - is_developer: {is_developer(admin)}")
        print()
        
        # Create a test Manager user
        manager = user_service.create_user(
            username="test_manager",
            email="manager@test.com",
            password=DEFAULT_PASSWORD,
            role_name=ROLE_MANAGER
        )
        session.expire_all()
        manager = session.query(user_service.User).filter_by(username="test_manager").first()
        print(f"Created test Manager: {manager.username}")
        print(f"Must change password: {manager.must_change_password}")
        print()
        
        # Test Manager permissions
        print("Manager Permissions:")
        print(f"  - can_view_dashboard: {can_view_dashboard(manager)}")
        print(f"  - can_manage_users: {can_manage_users(manager)}")
        print(f"  - can_view_developer_tools: {can_view_developer_tools(manager)}")
        print(f"  - can_edit_inventory: {can_edit_inventory(manager)}")
        print()
        
        # Create a test Maintenance Tech user
        tech = user_service.create_user(
            username="test_tech",
            email="tech@test.com",
            password=DEFAULT_PASSWORD,
            role_name=ROLE_MAINTENANCE_TECH
        )
        session.expire_all()
        tech = session.query(user_service.User).filter_by(username="test_tech").first()
        print(f"Created test Maintenance Tech: {tech.username}")
        print(f"Must change password: {tech.must_change_password}")
        print()
        
        # Test Tech permissions
        print("Maintenance Tech Permissions:")
        print(f"  - can_view_dashboard: {can_view_dashboard(tech)}")
        print(f"  - can_manage_users: {can_manage_users(tech)}")
        print(f"  - can_view_developer_tools: {can_view_developer_tools(tech)}")
        print(f"  - can_view_worksheets: {can_view_worksheets(tech)}")
        print(f"  - can_edit_worksheet: {can_edit_worksheet(tech)}")
        print()
        
        # Test password reset
        print("Testing password reset...")
        user_service.reset_user_password(manager.id)
        
        # Re-fetch to see changes
        session.expire_all()
        manager_refreshed = session.query(user_service.User).filter_by(id=manager.id).first()
        print(f"Manager must_change_password after reset: {manager_refreshed.must_change_password}")
        print()
        
        # Test role update
        print("Testing role update...")
        user_service.update_user_role(tech.id, ROLE_PRODUCTION_SUPERVISOR)
        
        session.expire_all()
        tech_refreshed = session.query(user_service.User).filter_by(id=tech.id).first()
        print(f"Tech role after update: {tech_refreshed.role.name}")
        print()
        
        # List all users
        print("All users:")
        all_users = session.query(user_service.User).all()
        for user in all_users:
            print(f"  - {user.username} ({user.role.name}) - must_change_pwd: {user.must_change_password}")
        print()
        
        # Clean up test users
        print("Cleaning up test users...")
        user_service.delete_user(manager.id)
        user_service.delete_user(tech.id)
        print("✓ Test users deleted")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_permissions()
