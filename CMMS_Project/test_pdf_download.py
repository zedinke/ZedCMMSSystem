#!/usr/bin/env python3
"""Test PDF download with assigned_user access"""
import sys
sys.path.insert(0, '.')

from database.models import Worksheet
from services.worksheet_service import _get_session
from pathlib import Path

session, _ = _get_session(None)

# Get a worksheet that is closed
ws = session.query(Worksheet).filter_by(status='Closed').first()
if ws:
    print(f"Found closed worksheet: {ws.id}")
    print(f"Closed at: {ws.closed_at}")
    
    # Try to access assigned_user (this would cause the error)
    try:
        username = ws.assigned_user.username if ws.assigned_user else "unknown"
        print(f"Assigned user: {username}")
    except Exception as e:
        print(f"ERROR accessing assigned_user: {e}")
        # Fallback
        print(f"Fallback: just use closed_at")
        if ws.closed_at:
            closed_date = ws.closed_at.strftime("%Y-%m-%d")
            print(f"Filename: worksheet_{ws.id}_{closed_date}.docx")
else:
    print("No closed worksheet found")
