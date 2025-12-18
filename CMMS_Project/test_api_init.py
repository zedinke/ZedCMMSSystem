#!/usr/bin/env python
"""Test API initialization"""

from api.app import create_app

try:
    app = create_app()
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    
    print("✅ API successfully created")
    print(f"Total routes: {len(routes)}")
    print("\nRegistered endpoints:")
    for route in sorted(set(routes)):
        print(f"  - {route}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
