"""
Password Change Dialog Component
Reusable dialog for changing user passwords with validation
"""
import flet as ft
from services import user_service


class PasswordChangeDialog:
    """Dialog for changing user password with double-entry validation"""
    
    def __init__(self, page: ft.Page, user_id: int, on_success=None, is_forced=False):
        """
        Initialize password change dialog
        
        Args:
            page: Flet page instance
            user_id: ID of user changing password
            on_success: Callback function on successful password change
            is_forced: Whether this is a forced password change (hides cancel)
        """
        self.page = page
        self.user_id = user_id
        self.on_success = on_success
        self.is_forced = is_forced
        
        # Password fields
        self.current_password_field = ft.TextField(
            label="Jelenlegi jelszó / Current Password" if not is_forced else "Új jelszó / New Password",
            password=True,
            can_reveal_password=True,
            autofocus=True,
            width=400,
        )
        
        self.new_password_field = ft.TextField(
            label="Új jelszó / New Password" if not is_forced else "Jelszó megerősítése / Confirm Password",
            password=True,
            can_reveal_password=True,
            width=400,
        )
        
        self.confirm_password_field = ft.TextField(
            label="Jelszó megerősítése / Confirm Password" if not is_forced else "",
            password=True,
            can_reveal_password=True,
            width=400,
            visible=not is_forced,
        )
        
        # Error message
        self.error_text = ft.Text(
            color="red",
            size=12,
            visible=False,
        )
        
        # Build dialog
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Jelszó megváltoztatása kötelező / Password Change Required" if is_forced 
                else "Jelszó megváltoztatása / Change Password"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Az első bejelentkezéshez vagy jelszó visszaállítás után meg kell változtatnia jelszavát.\n"
                        "After first login or password reset, you must change your password.",
                        size=12,
                        color="#F57C00",
                    ) if is_forced else ft.Container(),
                    ft.Divider() if is_forced else ft.Container(height=0),
                    self.current_password_field,
                    self.new_password_field,
                    self.confirm_password_field,
                    self.error_text,
                ],
                tight=True,
                spacing=15,
            ),
            actions=[
                ft.TextButton(
                    "Mégse / Cancel",
                    on_click=self._on_cancel,
                    visible=not is_forced,
                ),
                ft.ElevatedButton(
                    "Jelszó megváltoztatása / Change Password",
                    on_click=self._on_submit,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def show(self):
        """Show the dialog"""
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _show_error(self, message: str):
        """Display error message"""
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()
    
    def _hide_error(self):
        """Hide error message"""
        self.error_text.visible = False
        self.page.update()
    
    def _on_cancel(self, e):
        """Handle cancel button"""
        self.dialog.open = False
        self.page.update()
    
    def _on_submit(self, e):
        """Handle password change submission"""
        self._hide_error()
        
        # Get field values
        if self.is_forced:
            # For forced change, only need new password + confirm
            new_password = self.current_password_field.value
            confirm_password = self.new_password_field.value
            current_password = None
        else:
            current_password = self.current_password_field.value
            new_password = self.new_password_field.value
            confirm_password = self.confirm_password_field.value
        
        # Validation
        if not new_password:
            self._show_error("Új jelszó megadása kötelező / New password is required")
            return
        
        if len(new_password) < 6:
            self._show_error("A jelszónak legalább 6 karakter hosszúnak kell lennie / Password must be at least 6 characters")
            return
        
        if new_password != confirm_password:
            self._show_error("A jelszavak nem egyeznek / Passwords do not match")
            return
        
        # Verify current password if not forced change
        if not self.is_forced:
            if not current_password:
                self._show_error("Jelenlegi jelszó megadása kötelező / Current password is required")
                return
            
            # Verify current password matches
            if not user_service.verify_user_password(self.user_id, current_password):
                self._show_error("A jelenlegi jelszó helytelen / Current password is incorrect")
                return
        
        # Change password
        try:
            success = user_service.change_password(self.user_id, new_password)
            if success:
                # Close dialog
                self.dialog.open = False
                self.page.update()
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Jelszó sikeresen megváltoztatva / Password changed successfully"),
                    bgcolor="green",
                )
                self.page.snack_bar.open = True
                self.page.update()
                
                # Call success callback
                if self.on_success:
                    self.on_success()
            else:
                self._show_error("Jelszó megváltoztatása sikertelen / Password change failed")
        except Exception as ex:
            self._show_error(f"Hiba történt / Error: {str(ex)}")
