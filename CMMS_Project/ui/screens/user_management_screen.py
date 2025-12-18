"""
User Management Screen
Allows Manager role to create, edit, delete users and reset passwords
"""
import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
from services import user_service, context_service
from utils.permissions import can_manage_users
from config.roles import DEFAULT_PASSWORD
from localization.translator import translator
from ui.components.modern_components import (
    create_modern_button,
    create_modern_card,
    create_modern_text_field,
    create_modern_dropdown,
    create_modern_date_field,
    create_modern_dialog,
    create_modern_badge,
    create_vibrant_badge,
    create_modern_icon_button,
    create_modern_table,
    create_empty_state_card,
    DesignSystem,
)
from ui.components.modern_card import (
    create_tailwind_card,
    create_info_card,
)
from ui.components.confirmation_dialogs import create_delete_confirmation_dialog


class UserManagementScreen:
    """Screen for managing users (Manager role only)"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.main_column = None  # Store reference to main column for direct updates
        
        # User list - initialize early
        self.users_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )

        # Inline new-user panel (fallback if dialog fails)
        self._inline_error = ft.Text(color="red", size=12, visible=False)
        # Create explicit field instances to read values directly
        self._inline_username_field = create_modern_text_field(label="Felhasználónév", hint_text="pl. nagy.janos", width=250)
        self._inline_fullname_field = create_modern_text_field(label="Teljes név", hint_text="pl. Nagy János", width=250)
        self._inline_phone_field = create_modern_text_field(label="Telefonszám", hint_text="pl. +36 30 123 4567", width=250)
        self._inline_email_field = create_modern_text_field(label="Email (opcionális)", hint_text="pl. nagy.janos@example.com", width=250)
        self._inline_profile_field = create_modern_text_field(label="Profilkép URL (opcionális)", hint_text="Kép URL vagy fájl elérési út", width=520)

        self._inline_panel = ft.Container(
            visible=False,
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text("Új felhasználó (inline) / New User (inline)", weight=ft.FontWeight.BOLD),
                    ft.Row(controls=[
                        self._inline_username_field,
                        self._inline_fullname_field,
                    ]),
                    ft.Row(controls=[
                        self._inline_phone_field,
                        self._inline_email_field,
                    ]),
                    self._inline_profile_field,
                    self._inline_error,
                    ft.Row(controls=[
                        ft.ElevatedButton("Létrehozás", on_click=self._create_user_inline),
                        ft.TextButton("Panel elrejtése", on_click=lambda e: self._toggle_new_user_panel(False)),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=8,
            ),
        )

        # Inline action panel (fallback for edit/reset/delete)
        self._selected_user = None
        self._action_mode = None  # 'edit' | 'reset' | 'delete'
        self._action_username_field = create_modern_text_field(label="Felhasználónév / Username", width=250)
        self._action_fullname_field = create_modern_text_field(label="Teljes név / Full Name", width=250)
        self._action_phone_field = create_modern_text_field(label="Telefonszám / Phone", width=250)
        self._action_email_field = create_modern_text_field(label="Email", width=300)
        self._action_role_dropdown = create_modern_dropdown(label="Szerepkör / Role", width=300, options=[])
        self._action_vacation_days_field = create_modern_text_field(label="Szabadság napok / Vacation Days", width=250, hint_text="20")
        self._action_shift_type_dropdown = create_modern_dropdown(label="Műszak típus / Shift Type", width=250, options=[
            ft.dropdown.Option("single", "Egy műszak / Single"),
            ft.dropdown.Option("double", "Két műszak / Double"),
            ft.dropdown.Option("triple", "Három műszak / Triple"),
        ])
        self._action_shift_start_time_field = create_modern_text_field(label="Kezdés / Start Time", width=120, hint_text="06:00")
        self._action_shift_end_time_field = create_modern_text_field(label="Vég / End Time", width=120, hint_text="14:00")
        self._action_error = ft.Text(color="red", size=12, visible=False)
        self._action_info = ft.Text(color="blue", size=12, visible=False)

        # Prebuild rows so we can toggle visibility later
        self._action_buttons_row = ft.Row(
            controls=[
                ft.ElevatedButton("Mentés / Save", on_click=self._action_save),
                ft.ElevatedButton("Jelszó visszaállítás / Reset Password", on_click=self._prepare_reset_confirm),
                ft.ElevatedButton("Törlés / Delete", on_click=self._prepare_delete_confirm, bgcolor=DesignSystem.ERROR, color="#FFFFFF"),
                ft.TextButton("Bezárás / Close", on_click=lambda e: self._toggle_action_panel(False)),
            ],
            alignment=ft.MainAxisAlignment.END,
        )

        self._confirm_row = ft.Row(
            controls=[
                ft.ElevatedButton("Megerősítés / Confirm", on_click=self._confirm_action, bgcolor=DesignSystem.SUCCESS, color="#FFFFFF"),
                ft.TextButton("Mégse / Cancel", on_click=self._cancel_confirm),
            ],
            alignment=ft.MainAxisAlignment.END,
            visible=False,
        )

        self._action_panel = ft.Container(
            visible=False,
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text("Művelet panel / Action panel", weight=ft.FontWeight.BOLD),
                    ft.Row(controls=[self._action_username_field, self._action_fullname_field]),
                    ft.Row(controls=[self._action_phone_field, self._action_email_field]),
                    ft.Row(controls=[self._action_role_dropdown]),
                    ft.Divider(),
                    ft.Text("Szabadság és Műszak / Vacation and Shift", weight=ft.FontWeight.BOLD),
                    ft.Row(controls=[self._action_vacation_days_field]),
                    ft.Row(controls=[self._action_shift_type_dropdown]),
                    ft.Row(controls=[self._action_shift_start_time_field, self._action_shift_end_time_field]),
                    self._action_info,
                    self._action_error,
                    # Normal action buttons
                    self._action_buttons_row,
                    # Confirm row for reset/delete
                    self._confirm_row,
                ],
                spacing=8,
            ),
        )
        
        # Check permissions (using context, not user object)
        if not can_manage_users():
            self.page.go("/dashboard")
            return
        
        # Load users
        self._load_users()

    def _force_rerender(self):
        """Force rerender - _load_users() already handles the update"""
        # Reload users - this updates self.users_list.controls and calls page.update()
        self._load_users()
    
    def _load_users(self):
        """Load all users from database and update the list"""
        users = user_service.list_all_users()
        try:
            print(f"[UI] _load_users: fetched {len(users)} users")
        except Exception:
            pass
        
        # Clear and rebuild user list
        # Use clear() and extend() to ensure proper refresh (like vacation_screen does)
        self.users_list.controls.clear()
        
        for user in users:
            self.users_list.controls.append(self._build_user_card(user))
        
        # Force update of ListView and page immediately
        if self.page:
            # Update the page - this will refresh the ListView as well
            # Since users_list is a reference in main_column, updating the page should refresh it
            self.page.update()
            
            # Also try to update the ListView directly if possible
            # This ensures immediate visual refresh
            try:
                if hasattr(self.users_list, 'update'):
                    self.users_list.update()
            except Exception:
                pass  # ListView.update() might not be available in all Flet versions
    
    def _build_user_card(self, user):
        """Build a card for a single user"""
        from config.roles import ROLE_DEVELOPER
        
        is_developer = user.role.name == ROLE_DEVELOPER

        # Explicit handlers to instrument clicks with feedback
        def _on_edit_click(e, u=user):
            try:
                print(f"[UI] Edit clicked for user: {u.username}")
            except Exception:
                pass
            try:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.button_edit_clicked")))
                self.page.snack_bar.open = True
                self.page.update()
            except Exception:
                pass
            self._edit_user(u)

        def _on_reset_click(e, u=user):
            try:
                print(f"[UI] Reset password clicked for user: {u.username}")
            except Exception:
                pass
            try:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.button_reset_clicked")))
                self.page.snack_bar.open = True
                self.page.update()
            except Exception:
                pass
            self._reset_password(u)

        def _on_delete_click(e, u=user):
            try:
                print(f"[UI] Delete clicked for user: {u.username}")
            except Exception:
                pass
            try:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.button_delete_clicked")))
                self.page.snack_bar.open = True
                self.page.update()
            except Exception:
                pass
            self._delete_user(u)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON, size=40),
                            title=ft.Text(
                                user.full_name or user.username,
                                size=16,
                                weight=ft.FontWeight.W_600,
                            ),
                            subtitle=ft.Column(
                                controls=[
                                    ft.Text(f"Felhasználónév: {user.username}", size=12),
                                    ft.Text(f"Telefonszám: {user.phone or 'N/A'}", size=12),
                                    ft.Text(f"Email: {user.email or 'N/A'}", size=12),
                                    ft.Text(f"Szerepkör / Role: {user.role.name}", size=12),
                                    ft.Text(
                                        "⚠ Jelszó megváltoztatása kötelező / Must change password",
                                        size=11,
                                        color="orange700",
                                    ) if user.must_change_password else ft.Container(height=0),
                                    # Show default password hint when reset is required
                                    (ft.Text(
                                        f"Alapértelmezett jelszó / Default password: {DEFAULT_PASSWORD}",
                                        size=11,
                                        color="orange700",
                                    ) if user.must_change_password else ft.Container(height=0)),
                                ],
                                spacing=2,
                            ),
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Szerkesztés / Edit",
                                    on_click=_on_edit_click,
                                    disabled=is_developer,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.LOCK_RESET,
                                    tooltip="Jelszó visszaállítása / Reset Password",
                                    on_click=_on_reset_click,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Törlés / Delete",
                                    icon_color="red",
                                    on_click=_on_delete_click,
                                    disabled=is_developer,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=5,
                ),
                padding=10,
            ),
        )
    
    def _create_user_dialog(self):
        """Show dialog to create new user"""
        # Quick feedback to confirm click handler is firing
        try:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.dialog_opening")))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            pass
        try:
            print("[UI] create_user_dialog: start")
        except Exception:
            pass
        username_field = create_modern_text_field(label="Felhasználónév / Username", width=300)
        full_name_field = create_modern_text_field(
            label="Teljes név / Full Name *", 
            width=300,
            hint_text="pl. Nagy János"
        )
        phone_field = create_modern_text_field(
            label="Telefonszám / Phone", 
            width=300,
            hint_text="pl. +36 30 123 4567"
        )
        email_field = create_modern_text_field(
            label="Email (opcionális / optional)", 
            width=300,
            hint_text="pl. nagy.janos@example.com"
        )
        
        # Profile picture field (optional, base64 or file path)
        profile_pic_field = create_modern_text_field(
            label="Profilkép URL (opcionális / optional)",
            width=300,
            hint_text="Kép URL vagy fájl elérési út",
        )
        
        # Get roles safely (guard against service errors)
        try:
            roles = user_service.list_roles()
            print(f"[UI] create_user_dialog: roles fetched count={len(roles)}")
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Hiba a szerepkörök lekérésekor: {str(ex)}") ,
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
            roles = []
            try:
                print(f"[UI] create_user_dialog: roles fetch error: {ex}")
            except Exception:
                pass
        from config.roles import ROLE_DEVELOPER
        
        # Filter out Developer role (only system should have it)
        available_roles = [r for r in roles if getattr(r, 'name', None) != ROLE_DEVELOPER]
        
        role_dropdown = create_modern_dropdown(
            label="Szerepkör / Role",
            width=300,
            options=[ft.dropdown.Option(r.name) for r in available_roles] if available_roles else [],
            value=(available_roles[0].name if available_roles else None),
        )
        
        # Vacation and shift schedule fields
        vacation_days_field = create_modern_text_field(
            label="Szabadság napok / Vacation Days",
            width=300,
            hint_text="20",
            value="20",
        )
        
        shift_type_dropdown = create_modern_dropdown(
            label="Műszak típus / Shift Type",
            width=300,
            options=[
                ft.dropdown.Option("single", "Egy műszak / Single"),
                ft.dropdown.Option("double", "Két műszak / Double"),
                ft.dropdown.Option("triple", "Három műszak / Triple"),
            ],
            value="single",
        )
        
        shift_start_time_field = create_modern_text_field(
            label="Kezdés / Start Time",
            width=140,
            hint_text="06:00",
            value="06:00",
        )
        
        shift_end_time_field = create_modern_text_field(
            label="Vég / End Time",
            width=140,
            hint_text="14:00",
            value="14:00",
        )
        
        # Show/hide time fields based on shift type
        def on_shift_type_change(e):
            is_single = e.control.value == "single"
            shift_start_time_field.visible = is_single
            shift_end_time_field.visible = is_single
            self.page.update()
        
        shift_type_dropdown.on_change = on_shift_type_change
        
        info_text = ft.Text(
            f"Alapértelmezett jelszó: {DEFAULT_PASSWORD}\n"
            "A felhasználónak első bejelentkezéskor meg kell változtatnia a jelszót.",
            size=11,
            color="blue",
            italic=True,
        )
        
        error_text = ft.Text(color="red", size=12, visible=False)
        
        def on_create(e):
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
                return
            
            try:
                # Parse vacation days
                try:
                    vacation_days = int(vacation_days_field.value or "20")
                except (ValueError, TypeError):
                    vacation_days = 20
                
                # Get shift values and convert to database format
                shift_type_raw = shift_type_dropdown.value
                # Convert "double" -> "4_shift", "triple" -> "3_shift" for database
                if shift_type_raw == "double":
                    shift_type = "4_shift"
                elif shift_type_raw == "triple":
                    shift_type = "3_shift"
                else:
                    shift_type = shift_type_raw  # "single" stays as is
                
                shift_start = shift_start_time_field.value if shift_type == "single" else None
                shift_end = shift_end_time_field.value if shift_type == "single" else None
                
                user = user_service.create_user(
                    username=username_field.value,
                    password=DEFAULT_PASSWORD,
                    full_name=full_name_field.value,
                    phone=phone_field.value or None,
                    email=email_field.value or None,
                    profile_picture=profile_pic_field.value or None,
                    role_name=role_dropdown.value,
                    vacation_days_per_year=vacation_days,
                    shift_type=shift_type,
                    shift_start_time=shift_start,
                    shift_end_time=shift_end,
                )
                
                if user:
                    dialog.open = False
                    self.page.update()
                    
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Felhasználó létrehozva. Alapértelmezett jelszó: {DEFAULT_PASSWORD}"),
                        bgcolor=DesignSystem.SUCCESS,
                    )
                    self.page.snack_bar.open = True
                    
                    self._load_users()
                else:
                    error_text.value = "Felhasználó létrehozása sikertelen / User creation failed"
                    error_text.visible = True
                    self.page.update()
            except Exception as ex:
                error_text.value = f"Hiba / Error: {str(ex)}"
                error_text.visible = True
                self.page.update()
        
        # Build dialog inside try to catch UI errors
        try:
            print("[UI] create_user_dialog: building dialog")
            dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(translator.get_text("users.create_user_title")),
            content=ft.Column(
                controls=[
                    username_field,
                    full_name_field,
                    phone_field,
                    email_field,
                    profile_pic_field,
                    role_dropdown,
                    ft.Divider(),
                    ft.Text("Szabadság és Műszak / Vacation and Shift", weight=ft.FontWeight.BOLD, size=14),
                    vacation_days_field,
                    shift_type_dropdown,
                    ft.Row(controls=[shift_start_time_field, shift_end_time_field], spacing=20),
                    ft.Divider(),
                    info_text,
                    error_text,
                ],
                tight=False,
                spacing=10,
                width=400,
                height=600,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Mégse / Cancel", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Létrehozás / Create", on_click=on_create),
            ],
            )
            
            # Modern Flet way: use page.open() instead of page.dialog + page.update()
            try:
                self.page.open(dialog)
                print("[UI] create_user_dialog: dialog opened using page.open()")
            except AttributeError:
                # Fallback to old method if page.open() doesn't exist
                print("[UI] create_user_dialog: page.open() not available, using fallback")
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
                print("[UI] create_user_dialog: dialog opened using fallback")
            except Exception as open_error:
                print(f"[UI] create_user_dialog: Error opening dialog: {open_error}")
                # Try fallback
                try:
                    self.page.dialog = dialog
                    dialog.open = True
                    self.page.update()
                    print("[UI] create_user_dialog: Fallback successful")
                except Exception as fallback_error:
                    print(f"[UI] create_user_dialog: Fallback also failed: {fallback_error}")
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Dialógus hiba: {str(ex)}"),
                bgcolor=DesignSystem.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
            try:
                print(f"[UI] create_user_dialog: dialog error: {ex}")
            except Exception:
                pass
            # Fallback: minimal dialog to verify rendering
            try:
                fallback = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Új felhasználó"),
                    content=ft.Text("Egyszerű teszt dialógus"),
                    actions=[ft.TextButton("Bezárás", on_click=lambda e: setattr(fallback, 'open', False) or self.page.update())],
                )
                self.page.dialog = fallback
                fallback.open = True
                self.page.update()
                print("[UI] create_user_dialog: fallback dialog opened")
            except Exception as ex2:
                try:
                    print(f"[UI] create_user_dialog: fallback failed: {ex2}")
                except Exception:
                    pass

    def _on_new_user_click(self, e):
        """Handler for New User button click with explicit logging and feedback"""
        try:
            print("[UI] New User button clicked")
        except Exception:
            pass
        try:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.button_clicked")))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            pass
        # Try dialog and also show inline panel as fallback so user can proceed
        try:
            self._create_user_dialog()
        except Exception:
            pass
        # Always reveal inline panel to ensure functionality
        self._toggle_new_user_panel(True)

    def _toggle_new_user_panel(self, show: bool):
        """Show/hide inline new user form as a fallback"""
        self._inline_panel.visible = show
        self.page.update()

    def _create_user_inline(self, e):
        """Create user from inline form (fallback)"""
        # Read values directly from field instances
        username = (self._inline_username_field.value or "").strip()
        full_name = (self._inline_fullname_field.value or "").strip()
        phone = (self._inline_phone_field.value or None)
        email = (self._inline_email_field.value or None)
        profile = (self._inline_profile_field.value or None)

        self._inline_error.visible = False
        if not username:
            self._inline_error.value = "Felhasználónév kötelező"
            self._inline_error.visible = True
            self.page.update()
            return
        if not full_name:
            self._inline_error.value = "Teljes név kötelező"
            self._inline_error.visible = True
            self.page.update()
            return

        try:
            from config.roles import DEFAULT_PASSWORD, ROLE_DEVELOPER
            # Choose a sensible default role (first non-developer), fallback to first
            try:
                roles = user_service.list_roles()
                available = [r for r in roles if getattr(r, 'name', None) != ROLE_DEVELOPER]
                default_role_name = (available[0].name if available else (roles[0].name if roles else None))
            except Exception:
                default_role_name = None

            if not default_role_name:
                self._inline_error.value = translator.get_text("errors.role_not_found", role_name="")
                self._inline_error.visible = True
                self.page.update()
                return

            created = user_service.create_user(
                username=username,
                password=DEFAULT_PASSWORD,
                full_name=full_name,
                phone=phone or None,
                email=email or None,
                profile_picture=profile or None,
                role_name=default_role_name,
            )
            if created:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.user_created")), bgcolor=DesignSystem.SUCCESS)
                self.page.snack_bar.open = True
                self._toggle_new_user_panel(False)
                # Load users and update immediately
                self._load_users()
                # Optional: force re-render of current view
                try:
                    print("[UI] _create_user_inline: user created, reloading list")
                except Exception:
                    pass
            else:
                self._inline_error.value = "Létrehozás sikertelen"
                self._inline_error.visible = True
                self.page.update()
        except Exception as ex:
            self._inline_error.value = f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"
            self._inline_error.visible = True
            self.page.update()
    
    def _edit_user(self, user):
        """Show dialog to edit user"""
        # Fallback: open inline panel
        try:
            self._open_action_panel(user, mode='edit')
            return
        except Exception:
            pass
        try:
            print(f"[UI] _edit_user: opening dialog for {user.username}")
        except Exception:
            pass
        try:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.edit_dialog_opening")))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            pass
        email_field = create_modern_text_field(label="Email", value=user.email or "", width=300)
        
        # Get all roles
        roles = user_service.list_roles()
        from config.roles import ROLE_DEVELOPER
        
        available_roles = [r for r in roles if r.name != ROLE_DEVELOPER]
        
        role_dropdown = create_modern_dropdown(
            label="Szerepkör / Role",
            width=300,
            options=[ft.dropdown.Option(r.name) for r in available_roles],
            value=user.role.name,
        )
        
        error_text = ft.Text(color="red", size=12, visible=False)
        
        def on_save(e):
            error_text.visible = False
            
            try:
                # Update email
                user.email = email_field.value or None
                
                # Update role if changed
                if role_dropdown.value != user.role.name:
                    user_service.update_user_role(user.id, role_dropdown.value)
                
                dialog.open = False
                self.page.update()
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("users.user_updated")),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                
                self._load_users()
            except Exception as ex:
                error_text.value = f"Hiba / Error: {str(ex)}"
                error_text.visible = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Felhasználó szerkesztése / Edit User: {user.username}"),
            content=ft.Column(
                controls=[
                    ft.Text(f"Felhasználónév / Username: {user.username}", size=14),
                    email_field,
                    role_dropdown,
                    error_text,
                ],
                tight=True,
                spacing=15,
            ),
            actions=[
                ft.TextButton("Mégse / Cancel", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Mentés / Save", on_click=on_save),
            ],
        )
        
        self.page.dialog = dialog
        # Update page before opening to ensure dialog binding
        self.page.update()
        dialog.open = True
        self.page.update()
    
    def _reset_password(self, user):
        """Reset user password to default"""
        # Fallback: open inline panel reset
        try:
            self._open_action_panel(user, mode='reset')
            return
        except Exception:
            pass
        try:
            print(f"[UI] _reset_password: opening confirm for {user.username}")
        except Exception:
            pass
        try:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.reset_confirm")))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            pass
        def on_confirm(e):
            try:
                user_service.reset_user_password(user.id)
                
                dialog.open = False
                self.page.update()
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(
                        f"Jelszó visszaállítva: {DEFAULT_PASSWORD}\n"
                        f"A felhasználónak meg kell változtatnia jelszavát a következő bejelentkezéskor."
                    ),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                
                self._load_users()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba / Error: {str(ex)}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(translator.get_text("users.reset_password_title")),
            content=ft.Text(
                f"Biztosan vissza szeretné állítani {user.username} jelszavát?\n"
                f"Az új jelszó: {DEFAULT_PASSWORD}\n\n"
                f"Are you sure you want to reset password for {user.username}?\n"
                f"New password: {DEFAULT_PASSWORD}"
            ),
            actions=[
                ft.TextButton("Mégse / Cancel", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Visszaállítás / Reset", on_click=on_confirm),
            ],
        )
        
        self.page.dialog = dialog
        self.page.update()
        dialog.open = True
        self.page.update()
    
    def _delete_user(self, user):
        """Delete user after confirmation"""
        # Fallback: open inline panel delete
        try:
            self._open_action_panel(user, mode='delete')
            return
        except Exception:
            pass
        try:
            print(f"[UI] _delete_user: opening confirm for {user.username}")
        except Exception:
            pass
        
        def on_confirm(e):
            try:
                ctx = context_service.get_app_context()
                user_service.anonymize_user(user.id, anonymized_by_user_id=ctx.user_id if ctx.is_authenticated() else None)
                
                try:
                    self.page.close(confirmation_dialog)
                except:
                    confirmation_dialog.open = False
                    self.page.update()
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(translator.get_text("users.anonymize_success")),
                    bgcolor=DesignSystem.SUCCESS,
                )
                self.page.snack_bar.open = True
                
                self._load_users()
            except Exception as ex:
                try:
                    self.page.close(confirmation_dialog)
                except:
                    confirmation_dialog.open = False
                self.page.update()
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Hiba / Error: {str(ex)}"),
                    bgcolor=DesignSystem.ERROR,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Build summary data
        summary_data = {
            "name": user.full_name or user.username,
            "username": user.username,
            "email": user.email or "-",
            "role": user.role or "-",
        }
        
        warning_message = "Ez a művelet nem visszavonható! A felhasználó adatai anonymizálva lesznek. / This action cannot be undone! User data will be anonymized."
        
        confirmation_dialog = create_delete_confirmation_dialog(
            page=self.page,
            title=translator.get_text("users.anonymize_user_title") if hasattr(translator, 'get_text') else "Felhasználó törlése / Delete User",
            summary_data=summary_data,
            on_confirm=on_confirm,
            warning_message=warning_message,
        )
        
        try:
            self.page.open(confirmation_dialog)
        except:
            self.page.dialog = confirmation_dialog
            confirmation_dialog.open = True
            self.page.update()
        
        # Old dialog code kept for reference but not used
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(translator.get_text("users.anonymize_user_title")),
            content=ft.Text(translator.get_text("users.anonymize_user_confirm", username=user.username)),
            actions=[
                ft.TextButton(translator.get_text("common.buttons.cancel"), on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton(
                    translator.get_text("users.anonymize_user_title"),
                    on_click=on_confirm,
                    bgcolor=DesignSystem.ERROR,
                    color="#FFFFFF",
                ),
            ],
        )
        
        self.page.dialog = dialog
        self.page.update()
        dialog.open = True
        self.page.update()
    
    def build(self):
        """Build the user management screen"""
        # Load users immediately when building the screen (like worksheet screen does)
        # This ensures users are listed immediately when navigating to this page
        self._load_users()
        
        # Store reference to main column for direct updates
        self.main_column = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Felhasználók kezelése / User Management",
                            size=24,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.ElevatedButton(
                            "Új felhasználó / New User",
                            icon=ft.Icons.ADD,
                            on_click=self._on_new_user_click,
                        ),
                        ft.OutlinedButton(
                            "Frissítés / Refresh",
                            icon=ft.Icons.REFRESH,
                            on_click=lambda e: self._load_users(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Inline fallback panel below header
                self._inline_panel,
                # Inline action panel for edit/reset/delete
                self._action_panel,
                ft.Divider(),
                self.users_list,
            ],
            expand=True,
            spacing=10,
        )
        return self.main_column

    def _open_action_panel(self, user, mode: str):
        """Prepare and show inline action panel for user operations."""
        self._selected_user = user
        self._action_mode = mode
        self._action_error.visible = False
        # Prefill fields
        self._action_username_field.value = user.username or ""
        self._action_fullname_field.value = user.full_name or ""
        self._action_phone_field.value = user.phone or ""
        self._action_email_field.value = user.email or ""
        # Vacation and shift fields
        self._action_vacation_days_field.value = str(user.vacation_days_per_year or 20)
        # Convert database format to dropdown format: "3_shift" -> "triple", "4_shift" -> "double"
        shift_type_for_dropdown = user.shift_type or "single"
        if shift_type_for_dropdown == "3_shift":
            shift_type_for_dropdown = "triple"
        elif shift_type_for_dropdown == "4_shift":
            shift_type_for_dropdown = "double"
        self._action_shift_type_dropdown.value = shift_type_for_dropdown
        self._action_shift_start_time_field.value = user.shift_start_time or ""
        self._action_shift_end_time_field.value = user.shift_end_time or ""
        # Load roles for dropdown
        try:
            roles = user_service.list_roles()
            from config.roles import ROLE_DEVELOPER
            options = [ft.dropdown.Option(r.name) for r in roles if r.name != ROLE_DEVELOPER]
            self._action_role_dropdown.options = options
            self._action_role_dropdown.value = user.role.name if user.role.name != ROLE_DEVELOPER else (options[0].text if options else None)
        except Exception:
            self._action_role_dropdown.options = []
            self._action_role_dropdown.value = None

        # Button & info visibility according to mode
        is_edit = (mode == 'edit')
        self._action_username_field.visible = is_edit
        self._action_fullname_field.visible = is_edit
        self._action_phone_field.visible = is_edit
        self._action_email_field.visible = is_edit
        self._action_role_dropdown.visible = is_edit
        # Vacation and shift fields
        self._action_vacation_days_field.visible = is_edit
        self._action_shift_type_dropdown.visible = is_edit
        self._action_shift_start_time_field.visible = is_edit
        self._action_shift_end_time_field.visible = is_edit
        self._action_info.visible = False
        self._confirm_row.visible = False
        self._action_buttons_row.visible = True
        if mode == 'reset':
            self._action_info.value = "Biztosan visszaállítod a jelszót az alapértelmezettre?"
            self._action_info.visible = True
            self._confirm_row.visible = True
            self._action_buttons_row.visible = False
        elif mode == 'delete':
            self._action_info.value = "Biztosan törlöd a felhasználót? A művelet nem vonható vissza!"
            self._action_info.visible = True
            self._confirm_row.visible = True
            self._action_buttons_row.visible = False
        # Show panel
        self._action_panel.visible = True
        self.page.update()

    def _toggle_action_panel(self, show: bool):
        self._action_panel.visible = show
        self.page.update()

    def _action_save(self, e):
        if self._action_mode != 'edit' or not self._selected_user:
            return
        self._action_error.visible = False
        try:
            # Collect values
            new_username = (self._action_username_field.value or "").strip()
            new_fullname = (self._action_fullname_field.value or "").strip()
            new_phone = (self._action_phone_field.value or "").strip()
            new_email = (self._action_email_field.value or "").strip()
            new_role = self._action_role_dropdown.value

            # Basic validation
            if not new_username:
                raise Exception("Felhasználónév kötelező")
            if not new_fullname:
                raise Exception("Teljes név kötelező")

            # Collect vacation and shift values
            try:
                vacation_days = int(self._action_vacation_days_field.value or "20")
            except (ValueError, TypeError):
                vacation_days = 20
            
            shift_type_raw = self._action_shift_type_dropdown.value
            # Convert "double" -> "4_shift", "triple" -> "3_shift" for database
            if shift_type_raw == "double":
                shift_type = "4_shift"
            elif shift_type_raw == "triple":
                shift_type = "3_shift"
            else:
                shift_type = shift_type_raw  # "single" stays as is
            
            shift_start_time = self._action_shift_start_time_field.value or None
            shift_end_time = self._action_shift_end_time_field.value or None
            
            # Update via service (including vacation and shift)
            user_service.update_user_details(
                user_id=self._selected_user.id,
                username=new_username,
                full_name=new_fullname,
                phone=new_phone or None,
                email=new_email or None,
                role_name=new_role,
                vacation_days_per_year=vacation_days,
                shift_type=shift_type,
                shift_start_time=shift_start_time if shift_type == "single" else None,
                shift_end_time=shift_end_time if shift_type == "single" else None,
            )
            
            # Also update shift schedule if shift type is set
            if shift_type:
                from services.shift_service import set_user_shift_schedule
                from datetime import datetime
                try:
                    set_user_shift_schedule(
                        user_id=self._selected_user.id,
                        shift_type=shift_type,
                        start_time=shift_start_time if shift_type == "single" else None,
                        end_time=shift_end_time if shift_type == "single" else None,
                        effective_from=datetime.now(),
                    )
                except Exception as shift_ex:
                    # Log but don't fail the whole update
                    logger.warning(f"Error updating shift schedule: {shift_ex}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.user_updated")), bgcolor=DesignSystem.SUCCESS)
            self.page.snack_bar.open = True
            self._toggle_action_panel(False)
            self._load_users()
        except Exception as ex:
            self._action_error.value = f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"
            self._action_error.visible = True
            self.page.update()

    def _prepare_reset_confirm(self, e):
        if not self._selected_user:
            return
        self._open_action_panel(self._selected_user, mode='reset')

    def _prepare_delete_confirm(self, e):
        if not self._selected_user:
            return
        self._open_action_panel(self._selected_user, mode='delete')

    def _confirm_action(self, e):
        if not self._selected_user or self._action_mode not in ('reset', 'delete'):
            return
        try:
            if self._action_mode == 'reset':
                user_service.reset_user_password(self._selected_user.id)
                from config.roles import DEFAULT_PASSWORD
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Jelszó visszaállítva: {DEFAULT_PASSWORD}"), bgcolor=DesignSystem.SUCCESS)
            elif self._action_mode == 'delete':
                ctx = context_service.get_app_context()
                user_service.anonymize_user(self._selected_user.id, anonymized_by_user_id=ctx.user_id if ctx.is_authenticated() else None)
                self.page.snack_bar = ft.SnackBar(content=ft.Text(translator.get_text("users.user_deleted")), bgcolor=DesignSystem.SUCCESS)
            self.page.snack_bar.open = True
            self._toggle_action_panel(False)
            self._load_users()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"{translator.get_text('common.messages.error_occurred')}: {str(ex)}"), bgcolor=DesignSystem.ERROR)
            self.page.snack_bar.open = True
            self.page.update()

    def _cancel_confirm(self, e):
        # Return to edit mode or just close confirmation
        self._confirm_row.visible = False
        self._action_buttons_row.visible = True
        self._action_info.visible = False
        self.page.update()
