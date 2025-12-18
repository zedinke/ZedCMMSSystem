"""
Fix script for user_management_screen.py on_create function
"""
import re

# Read the file
with open('E:/Artence_CMMS/CMMS_Project/ui/screens/user_management_screen.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken on_create function
broken_pattern = r'''        def on_create\(e\):
            error_text.visible = False
            
            if not username_field.value:
                error_text.value = "Felhasználónév megadása kötelező / Username is required"
                error_text.visible = True
            
                            if not full_name_field.value:
                                error_text.value = "Teljes név megadása kötelező / Full name is required"
                                error_text.visible = True
                                self.page.update\(\)
                                return
                self.page.update\(\)
                return'''

fixed_function = '''        def on_create(e):
            error_text.visible = False
            
            if not username_field.value:
                error_text.value = "Felhasználónév megadása kötelező / Username is required"
                error_text.visible = True
                self.page.update()
                return
            
            if not full_name_field.value:
                error_text.value = "Teljes név megadása kötelező / Full name is required"
                error_text.visible = True
                self.page.update()
                return'''

content = re.sub(broken_pattern, fixed_function, content, flags=re.DOTALL)

# Write back
with open('E:/Artence_CMMS/CMMS_Project/ui/screens/user_management_screen.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed on_create function")
