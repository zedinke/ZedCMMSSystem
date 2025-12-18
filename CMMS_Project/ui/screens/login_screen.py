"""
Login képernyő
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
import threading
from services import auth_service, context_service
from services.auth_service import AuthenticationError
from localization.translator import translator
from ui.components.password_change_dialog import PasswordChangeDialog
from ui.components.loading_screen import LoadingScreen
from ui.components.welcome_screen import WelcomeScreen
from ui.components.compliance_badges import create_compliance_footer
from ui.components.modern_components import (
    create_modern_text_field,
    create_modern_button,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
)


class LoginScreen:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.error_text = ft.Text(value="", color="red")
        self.username = create_modern_text_field(
            label=translator.get_text("auth.login.username_label"),
            value="admin",
            width=380,
        )
        self.password = create_modern_text_field(
            label=translator.get_text("auth.login.password_label"),
            password=True,
            width=380,
        )
        if hasattr(self.password, 'can_reveal_password'):
            self.password.can_reveal_password = True
        self.password.value = "admin123"
        self.login_button = None
        self.is_loading = False
    
    def _set_button_state(self, disabled: bool = None, text: str = None):
        """Helper function to set button state, handling Container-wrapped buttons"""
        if not self.login_button:
            return
        
        # Get the actual button (might be wrapped in Container for gradient)
        actual_button = self.login_button
        if isinstance(self.login_button, ft.Container) and hasattr(self.login_button.content, 'disabled'):
            actual_button = self.login_button.content
        
        # Set attributes if provided
        if disabled is not None and hasattr(actual_button, 'disabled'):
            actual_button.disabled = disabled
        if text is not None and hasattr(actual_button, 'text'):
            actual_button.text = text

    def view(self, page: ft.Page):
        # Reset loading state when view is called (e.g., after logout)
        self.is_loading = False
        self.error_text.value = ""
        
        def handle_login(e):
            # Prevent multiple clicks
            if self.is_loading:
                print("[LOGIN] Login already in progress, ignoring click")
                return
            
            self.is_loading = True
            self.error_text.value = ""
            
            # Disable button
            self._set_button_state(disabled=True, text="Bejelentkezés...")
            page.update()
            
            def login_process():
                import time
                loading = None
                try:
                    print("[LOGIN] Starting login...")
                    print(f"[LOGIN] Username: {self.username.value.strip()}")
                    # Login now returns both token and user_info, avoiding slow validate_session call
                    try:
                        print("[LOGIN] Calling auth_service.login()...")
                        token, user_info = auth_service.login(self.username.value.strip(), self.password.value)
                        print(f"[LOGIN] Token received: {token[:20]}...")
                        print("[LOGIN] User info received from login, no need to validate session")
                    except Exception as login_error:
                        print(f"[LOGIN] Login error: {login_error}")
                        print(f"[LOGIN] Error type: {type(login_error)}")
                        import traceback
                        traceback.print_exc()
                        # Re-raise to be caught by outer exception handler
                        raise
                    
                    # Only show loading screen if login and validation were successful
                    loading = LoadingScreen(page, duration=2.0, on_complete=None)
                    loading.show()
                    
                    # Wait for loading screen to finish (2 seconds)
                    time.sleep(2.0)
                    # Handle None or empty full_name properly
                    full_name = user_info.get("full_name")
                    username = user_info.get("username", "Felhasználó")
                    user_id = user_info.get("user_id")
                    must_change_password = user_info.get("must_change_password", False)
                    
                    # Debug: print what we got
                    print(f"[LOGIN] full_name from user_info: {repr(full_name)}")
                    print(f"[LOGIN] username from user_info: {repr(username)}")
                    print(f"[LOGIN] must_change_password: {must_change_password}")
                    
                    # Check if password change is required
                    if must_change_password:
                        print("[LOGIN] Password change required, showing dialog")
                        # Hide loading screen
                        if loading:
                            try:
                                loading.hide()
                            except:
                                pass
                        
                        # Show password change dialog (blocking)
                        def on_password_change_success():
                            """Called after successful password change"""
                            print("[LOGIN] Password changed successfully, continuing login")
                            # Refresh user info to get updated must_change_password status
                            user_info_updated = auth_service.validate_session(token)
                            if not user_info_updated.get("must_change_password", False):
                                # Password change successful, continue with login
                                full_name_updated = user_info_updated.get("full_name")
                                username_updated = user_info_updated.get("username", "Felhasználó")
                                user_full_name = full_name_updated if (full_name_updated and full_name_updated.strip()) else username_updated
                                
                                # Show welcome screen
                                welcome = WelcomeScreen(
                                    page, 
                                    user_full_name, 
                                    on_complete=None
                                )
                                welcome.show()
                                
                                # Wait for welcome screen to display
                                time.sleep(2.0)
                                
                                # Continue with login
                                print("[LOGIN] Welcome screen displayed, proceeding to login success")
                                self.on_login_success(token, user_info_updated)
                            else:
                                # Still requires password change (shouldn't happen)
                                page.snack_bar = ft.SnackBar(
                                    content=ft.Text(translator.get_text("auth.password_change_required")),
                                    bgcolor=DesignSystem.ERROR
                                )
                                page.snack_bar.open = True
                                page.update()
                        
                        # Show password change dialog on main thread
                        page.add_task(
                            lambda: self._show_password_change_dialog(page, user_id, on_password_change_success)
                        )
                        return  # Exit login_process, dialog will handle continuation
                    
                    # Use full_name if it exists and is not empty, otherwise use username
                    user_full_name = full_name if (full_name and full_name.strip()) else username
                    print(f"[LOGIN] Final user_full_name: {repr(user_full_name)}")
                    
                    # Show welcome screen after loading
                    # Note: welcome.show() is called from background thread, but it updates UI on main thread
                    # We'll pass the token and callback through to the welcome screen
                    welcome = WelcomeScreen(
                        page, 
                        user_full_name, 
                        on_complete=None  # We'll handle completion differently
                    )
                    welcome.show()
                    
                    # Wait for welcome screen to display (2 seconds)
                    time.sleep(2.0)
                    
                    # Now call on_login_success from the login thread with user_info
                    # This will call page.go() which should work from any thread in Flet
                    print("[LOGIN] Welcome screen displayed, proceeding to login success")
                    self.on_login_success(token, user_info)
                    
                except AuthenticationError as exc:
                    print(f"[LOGIN] AuthenticationError: {exc}")
                    # Stop loading screen if it was started
                    if loading:
                        try:
                            loading.hide()
                        except:
                            pass
                    
                    self.is_loading = False
                    message_map = {
                        "Invalid credentials": translator.get_text("auth.login.invalid_credentials"),
                        "User account is inactive": translator.get_text("auth.permissions.access_denied"),
                        "Session expired": translator.get_text("auth.permissions.access_denied"),
                    }
                    error_message = message_map.get(str(exc), translator.get_text("common.messages.error_occurred"))
                    
                    # Update UI - Flet allows page.update() from background thread
                    self.error_text.value = error_message
                    self._set_button_state(disabled=False, text=translator.get_text("auth.login.login_button"))
                    try:
                        page.update()
                    except Exception as update_error:
                        print(f"[LOGIN] Error updating page: {update_error}")
                        # Try using add_task as fallback
                        page.add_task(lambda: page.update())
                    
                except Exception as ex:
                    print(f"[LOGIN] Exception: {ex}")
                    import traceback
                    traceback.print_exc()
                    
                    # Stop loading screen if it was started
                    if loading:
                        try:
                            loading.hide()
                        except:
                            pass
                    
                    self.is_loading = False
                    error_message = translator.get_text("common.messages.error_occurred")
                    if "Lost connection" in str(ex) or "timeout" in str(ex).lower() or "OperationalError" in str(type(ex).__name__):
                        error_message = translator.get_text("common.messages.error_occurred") + " - Kapcsolati hiba. Kérjük próbálja újra."
                    elif "Invalid credentials" in str(ex):
                        error_message = translator.get_text("auth.login.invalid_credentials")
                    elif "User account is inactive" in str(ex):
                        error_message = translator.get_text("auth.permissions.access_denied")
                    
                    # Update UI - Use add_task to ensure it runs on main thread
                    def update_ui():
                        self.error_text.value = error_message
                        self._set_button_state(disabled=False, text=translator.get_text("auth.login.login_button"))
                        try:
                            page.update()
                        except Exception as update_error:
                            print(f"[LOGIN] Error updating page: {update_error}")
                    
                    page.add_task(update_ui)
            
            # Run login in thread to not block UI
            thread = threading.Thread(target=login_process, daemon=True)
            thread.start()

        # Create new button instance each time view is called to ensure clean state
        login_button_text = translator.get_text("auth.login.login_button")
        self.login_button = create_modern_button(
            text=login_button_text,
            on_click=handle_login,
            width=380,
            height=48,
            disabled=False,
            use_gradient=True,
            gradient_colors=[DesignSystem.EMERALD_500, DesignSystem.BLUE_500],
        )
        
        # Note: If button is wrapped in Container (gradient), we can't directly set attributes
        # The button is already created with correct text and disabled=False

        from ui.components.modern_components import create_modern_card
        
        # Ensure all required components are not None
        if self.username is None:
            self.username = create_modern_text_field(
                label=translator.get_text("auth.login.username_label"),
                value="admin",
                width=380,
            )
        if self.password is None:
            self.password = create_modern_text_field(
                label=translator.get_text("auth.login.password_label"),
                password=True,
                width=380,
            )
            if hasattr(self.password, 'can_reveal_password'):
                self.password.can_reveal_password = True
            self.password.value = "admin123"
        if self.error_text is None:
            self.error_text = ft.Text(value="", color="red")
        if self.login_button is None:
            self.login_button = create_modern_button(
                text=translator.get_text("auth.login.login_button"),
                on_click=handle_login,
                width=380,
                height=48,
                disabled=False,
            )
        
        # Build card controls list, filtering out None values
        card_controls = [
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.Icons.SECURITY, size=40, color=DesignSystem.EMERALD_500),
                        padding=ft.padding.all(DesignSystem.SPACING_4),
                        bgcolor=DesignSystem.EMERALD_100,
                        border_radius=DesignSystem.RADIUS_XL,
                    ),
                    ft.Text(
                        translator.get_text("auth.login.title"),
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=DesignSystem.TEXT_PRIMARY,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                padding=ft.padding.only(bottom=32),
            ),
            self.username,
            self.password,
            self.error_text,
            ft.Container(height=DesignSystem.SPACING_SM),
            self.login_button,
        ]
        # Filter out None values
        card_controls = [c for c in card_controls if c is not None]
        
        # Ensure card_controls Column is valid
        card_column = ft.Column(
            controls=card_controls,
            spacing=DesignSystem.SPACING_MD,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Ensure card_column is not None
        if card_column is None:
            card_column = ft.Column(
                controls=[ft.Text("Error: Could not create login form")],
                spacing=DesignSystem.SPACING_MD,
            )
        
        card = create_tailwind_card(
            content=card_column,
            padding=DesignSystem.SPACING_8,
            elevation=3,
            accent_color=DesignSystem.EMERALD_500,
            border_accent=True,
            use_gradient=True,
            gradient_colors=[DesignSystem.EMERALD_50, DesignSystem.BLUE_50],
        )
        
        # Ensure card is not None
        if card is None:
            card = ft.Container(
                content=ft.Text("Error loading login form"),
                padding=20,
            )
        
        card.width = 450

        # Create compliance footer (ensure it's not None)
        try:
            compliance_footer = create_compliance_footer()
            if compliance_footer is None:
                compliance_footer = ft.Container()  # Empty container as fallback
        except Exception as e:
            print(f"Error creating compliance footer: {e}")
            compliance_footer = ft.Container()  # Empty container as fallback
        
        # Load logo image - place BEFORE the card
        from pathlib import Path
        import sys
        import os
        
        # Get the correct path for both development and PyInstaller
        if getattr(sys, 'frozen', False):
            # Running as executable - use sys._MEIPASS for PyInstaller
            base_path = Path(sys._MEIPASS)
        else:
            # Running as script - use PROJECT_ROOT
            from config.app_config import PROJECT_ROOT
            base_path = PROJECT_ROOT
        
        logo_path = base_path / "Images" / "zedcmms_system.jpg"
        
        logo_container = ft.Container()  # Empty container by default
        if logo_path.exists():
            try:
                logo_image = ft.Image(
                    src=str(logo_path),
                    width=450,
                    fit=ft.ImageFit.CONTAIN,
                )
                logo_container = ft.Container(
                    content=logo_image,
                    padding=ft.padding.only(bottom=DesignSystem.SPACING_LG),
                )
            except Exception as e:
                print(f"Error loading logo: {e}")
                logo_container = ft.Container()  # Ensure it's not None
        else:
            # Try alternative paths
            alt_paths = [
                Path("Images") / "zedcmms_system.jpg",
                Path("zedcmms_system.jpg"),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    try:
                        logo_image = ft.Image(
                            src=str(alt_path),
                            width=450,
                            fit=ft.ImageFit.CONTAIN,
                        )
                        logo_container = ft.Container(
                            content=logo_image,
                            padding=ft.padding.only(bottom=DesignSystem.SPACING_LG),
                        )
                        break
                    except Exception as e:
                        print(f"Error loading logo from {alt_path}: {e}")
                        continue
        
        # Ensure card is not None
        if card is None:
            card = ft.Container(content=ft.Text("Error loading login form"), padding=20)
        
        # Build main column controls list, filtering out None values
        # Logo should be BETWEEN card and footer
        main_controls = [
            ft.Container(height=50),  # Space at top
            card,  # Login card first
            logo_container,  # Logo after card, before footer
            compliance_footer,
            ft.Container(expand=True),  # Push footer up
        ]
        # Filter out None values to prevent _build_add_commands errors
        main_controls = [c for c in main_controls if c is not None]
        
        # Ensure main_column is valid and doesn't contain None
        main_column = ft.Column(
            controls=main_controls,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Double-check: filter out None values from main_column.controls if any
        if hasattr(main_column, 'controls') and main_column.controls:
            main_column.controls = [c for c in main_column.controls if c is not None]
        
        result_container = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=DesignSystem.BG_PRIMARY,
            content=main_column,
        )
        
        # Ensure result_container.content is not None
        if result_container.content is None:
            result_container.content = ft.Column(
                controls=[ft.Text("Error: Could not create login layout")],
                spacing=0,
            )
        
        return result_container

    def _show_password_change_dialog(self, page: ft.Page, user_id: int, on_success):
        """Show password change dialog (called on main thread)"""
        dialog = PasswordChangeDialog(
            page=page,
            user_id=user_id,
            on_success=on_success,
            is_forced=True
        )
        dialog.show()
        
        # Note: The dialog is modal, so it will block until closed
        # The on_success callback will be called when password is changed
