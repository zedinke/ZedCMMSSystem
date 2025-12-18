"""
Tests for context service
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.context_service import get_app_context, set_app_context, clear_app_context


def test_context_set_and_clear():
    ctx = get_app_context()
    assert ctx.user_id is None

    user_info = {
        "user_id": 1,
        "username": "admin",
        "email": "admin@cmms.local",
        "role": "Manager",
        "language": "hu",
        "permissions": {"can_edit_inventory": True}
    }

    set_app_context(user_info, token="token123")
    ctx = get_app_context()
    assert ctx.user_id == 1
    assert ctx.username == "admin"
    assert ctx.role == "Manager"
    assert ctx.permissions.get("can_edit_inventory") is True

    clear_app_context()
    ctx = get_app_context()
    assert ctx.user_id is None


if __name__ == "__main__":
    test_context_set_and_clear()
    print("Context service tests passed")
