"""
Modern welcome screen komponens animációval
Informatív, designos, modern üdvözlő képernyő
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
import threading
from typing import Callable
from datetime import datetime
from services.context_service import get_app_context
from localization.translator import translator
from ui.components.modern_components import (
    DesignSystem,
    create_modern_card,
    create_modern_badge,
)


class WelcomeScreen:
    """Modern welcome screen animációval"""
    
    def __init__(self, page: ft.Page, user_name: str, on_complete: Callable = None):
        self.page = page
        # Debug: log what we received
        print(f"[WELCOME] Received user_name: {repr(user_name)}")
        # Ensure user_name is not None or empty
        default_user = translator.get_text("auth.welcome.default_user") if hasattr(translator, 'get_text') else "Felhasználó"
        if not user_name or not user_name.strip():
            print(f"[WELCOME] user_name is None or empty, using '{default_user}'")
            user_name = default_user
        self.user_name = user_name.split()[0] if user_name else default_user  # First name only
        self.full_name = user_name.strip() if user_name else default_user
        print(f"[WELCOME] Final full_name: {repr(self.full_name)}")
        self.on_complete = on_complete
        
        # Get user context for additional info
        try:
            ctx = get_app_context()
            self.user_role = ctx.role if ctx else None
            self.username = ctx.username if ctx else None
        except:
            self.user_role = None
            self.username = None
    
    def _get_job_title(self, role_name: str) -> str:
        """Convert role name to localized job title"""
        if not role_name:
            return "-"
        
        # Get localized job title from translations
        try:
            if hasattr(translator, '_translations') and hasattr(translator, 'get_current_language'):
                current_lang = translator.get_current_language()
                translations = translator._translations.get(current_lang, {})
                # Navigate to job_titles
                job_titles = translations.get("auth", {}).get("welcome", {}).get("job_titles", {})
                # Try to find role name with spaces/dashes replaced
                role_key = role_name.replace(" ", "_").replace("-", "_")
                if role_key in job_titles:
                    return job_titles[role_key]
                # Also try original role name
                if role_name in job_titles:
                    return job_titles[role_name]
        except:
            pass
        
        # Fallback to hardcoded mapping if translation fails
        # This mapping is language-aware based on current language
        current_lang = translator.get_current_language() if hasattr(translator, 'get_current_language') else "hu"
        if current_lang == "hu":
            role_to_title = {
                "Developer": "Fejlesztő",
                "Manager": "Felsővezető",
                "Műszakvezető - Karbantartó": "Karbantartási műszakvezető",
                "Műszakvezető - Termelés": "Termelési műszakvezető",
                "Karbantartó": "Karbantartó",
            }
        else:  # English
            role_to_title = {
                "Developer": "Developer",
                "Manager": "Executive",
                "Műszakvezető - Karbantartó": "Maintenance Shift Supervisor",
                "Műszakvezető - Termelés": "Production Shift Supervisor",
                "Karbantartó": "Maintenance Technician",
            }
        
        # Return mapped title or original role name if not found
        return role_to_title.get(role_name, role_name)
        
    def build(self):
        """Build the welcome screen"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M")
        date_str = current_time.strftime("%Y. %B %d.") if translator.get_current_language() == "hu" else current_time.strftime("%B %d, %Y")
        
        # Animated success icon with pulse effect
        success_icon = ft.Container(
            content=ft.Stack([
                # Outer glow circle
                ft.Container(
                    width=120,
                    height=120,
                    border_radius=60,
                    bgcolor=f"{DesignSystem.SUCCESS}20",
                    animate_opacity=ft.Animation(1500, ft.AnimationCurve.EASE_IN_OUT),
                    opacity=0.5,
                ),
                # Inner icon
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.CHECK_CIRCLE,
                        size=80,
                        color=DesignSystem.SUCCESS,
                    ),
                    width=120,
                    height=120,
                    alignment=ft.alignment.center,
                ),
            ]),
            opacity=0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
            scale=ft.Scale(0.3),
        )
        
        # Welcome text with animation
        welcome_text = ft.Text(
            translator.get_text("auth.welcome.title") if hasattr(translator, 'get_text') else "Üdvözlünk,",
            size=36,
            weight=ft.FontWeight.W_700,
            color=DesignSystem.TEXT_PRIMARY,
            opacity=0,
            animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
        )
        
        # User full name with animation
        name_text = ft.Text(
            self.full_name,  # Show full name instead of first name only
            size=48,  # Slightly smaller to fit longer names
            weight=ft.FontWeight.W_700,
            color=DesignSystem.PRIMARY,
            opacity=0,
            animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        )
        
        # Job title (role) with animation
        job_title = self._get_job_title(self.user_role)
        job_title_prefix = translator.get_text("auth.welcome.job_title_prefix") if hasattr(translator, 'get_text') else "Jelenlegi munkahelyi besorolásod:"
        job_title_text = ft.Text(
            f"{job_title_prefix} {job_title}" if job_title != "-" else "",
            size=18,
            weight=ft.FontWeight.W_500,
            color=DesignSystem.TEXT_SECONDARY,
            opacity=0,
            animate_opacity=ft.Animation(900, ft.AnimationCurve.EASE_OUT),
        )
        
        # Success message
        success_text = ft.Text(
            translator.get_text("auth.welcome.success") if hasattr(translator, 'get_text') else "Sikeresen bejelentkezve",
            size=20,
            color=DesignSystem.TEXT_SECONDARY,
            opacity=0,
            animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_OUT),
        )
        
        # Info cards container
        info_cards = ft.Row([
            # Date card
            ft.Container(
                content=create_modern_card(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=32, color=DesignSystem.PRIMARY),
                        ft.Container(height=12),
                        ft.Text(
                            date_str,
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            translator.get_text("auth.welcome.date") if hasattr(translator, 'get_text') else "Dátum",
                            size=12,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=DesignSystem.SPACING_LG,
                ),
                width=180,
                height=140,
            ),
            # Time card
            ft.Container(
                content=create_modern_card(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ACCESS_TIME, size=32, color=DesignSystem.SECONDARY),
                        ft.Container(height=12),
                        ft.Text(
                            time_str,
                            size=24,
                            weight=ft.FontWeight.W_700,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            translator.get_text("auth.welcome.time") if hasattr(translator, 'get_text') else "Idő",
                            size=12,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=DesignSystem.SPACING_LG,
                ),
                width=180,
                height=140,
            ),
            # Role card
            ft.Container(
                content=create_modern_card(
                    content=ft.Column([
                        ft.Icon(ft.Icons.BADGE, size=32, color=DesignSystem.WARNING),
                        ft.Container(height=12),
                        ft.Text(
                            self._get_job_title(self.user_role),
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=DesignSystem.TEXT_PRIMARY,
                        ),
                        ft.Text(
                            translator.get_text("auth.welcome.role") if hasattr(translator, 'get_text') else "Szerepkör",
                            size=12,
                            color=DesignSystem.TEXT_SECONDARY,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=DesignSystem.SPACING_LG,
                ),
                width=180,
                height=140,
            ),
        ], spacing=DesignSystem.SPACING_MD, alignment=ft.MainAxisAlignment.CENTER)
        
        info_cards.opacity = 0
        info_cards.animate_opacity = ft.Animation(1200, ft.AnimationCurve.EASE_OUT)
        
        # Loading indicator (animated dots)
        loading_dots = ft.Row([
            ft.Container(
                width=8,
                height=8,
                border_radius=4,
                bgcolor=DesignSystem.PRIMARY,
                animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
                opacity=0.3,
            ),
            ft.Container(
                width=8,
                height=8,
                border_radius=4,
                bgcolor=DesignSystem.PRIMARY,
                animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
                opacity=0.3,
            ),
            ft.Container(
                width=8,
                height=8,
                border_radius=4,
                bgcolor=DesignSystem.PRIMARY,
                animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
                opacity=0.3,
            ),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        
        loading_dots.opacity = 0
        loading_dots.animate_opacity = ft.Animation(1500, ft.AnimationCurve.EASE_OUT)
        
        return ft.Container(
            expand=True,
            bgcolor=DesignSystem.BG_PRIMARY,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[DesignSystem.BG_PRIMARY, DesignSystem.PRIMARY_LIGHT],
            ),
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Column(
                        controls=[
                            success_icon,
                            ft.Container(height=40),
                            welcome_text,
                            name_text,
                            ft.Container(height=8),
                            job_title_text,
                            ft.Container(height=16),
                            success_text,
                            ft.Container(height=48),
                            info_cards,
                            ft.Container(height=32),
                            loading_dots,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Container(expand=True),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
    
    def show(self):
        """Show welcome screen with animations"""
        welcome_view = self.build()
        self.page.controls.clear()
        self.page.add(welcome_view)
        self.page.update()
        
        # Find controls for animation
        container = self.page.controls[0] if self.page.controls else None
        if not container:
            if self.on_complete:
                self.on_complete()
            return
        
        success_icon = None
        welcome_text = None
        name_text = None
        job_title_text = None
        success_text = None
        info_cards = None
        loading_dots = None
        
        def find_controls(control):
            nonlocal success_icon, welcome_text, name_text, job_title_text, success_text, info_cards, loading_dots
            if isinstance(control, ft.Text):
                if "Üdvözlünk" in control.value or (hasattr(translator, 'get_text') and translator.get_text("auth.welcome.title") in control.value):
                    welcome_text = control
                elif control.value == self.full_name or control.value == self.user_name:
                    name_text = control
                elif (hasattr(translator, 'get_text') and translator.get_text("auth.welcome.job_title_prefix") in control.value) or "Jelenlegi munkahelyi besorolásod" in control.value or "Current job classification" in control.value:
                    job_title_text = control
                elif "Sikeresen" in control.value or (hasattr(translator, 'get_text') and translator.get_text("auth.welcome.success") in control.value):
                    success_text = control
            elif isinstance(control, ft.Container):
                if hasattr(control, 'content') and isinstance(control.content, ft.Stack):
                    success_icon = control
                if hasattr(control.content, 'controls'):
                    for c in control.content.controls:
                        find_controls(c)
            elif isinstance(control, ft.Row) and len(control.controls) > 0:
                # Check if it's info cards (has 3 cards) or loading dots (has 3 small containers)
                if len(control.controls) == 3:
                    first_item = control.controls[0]
                    if isinstance(first_item, ft.Container) and hasattr(first_item, 'content'):
                        if isinstance(first_item.content, ft.Column) and len(first_item.content.controls) > 0:
                            if isinstance(first_item.content.controls[0], ft.Icon):
                                info_cards = control
                            elif isinstance(first_item.content.controls[0], ft.Container) and first_item.content.controls[0].width == 8:
                                loading_dots = control
            if hasattr(control, 'controls'):
                for c in control.controls:
                    find_controls(c)
        
        find_controls(container)
        
        # Animate elements with staggered timing
        import time
        
        def animate_sequence():
            time.sleep(0.1)  # Small delay before starting
            
            # 1. Icon appears with scale
            if success_icon:
                success_icon.opacity = 1.0
                success_icon.scale = ft.Scale(1.0)
                self.page.update()
                time.sleep(0.2)
            
            # 2. Welcome text
            if welcome_text:
                welcome_text.opacity = 1.0
                self.page.update()
                time.sleep(0.2)
            
            # 3. Name with scale
            if name_text:
                name_text.opacity = 1.0
                name_text.scale = ft.Scale(1.0)
                self.page.update()
                time.sleep(0.2)
            
            # 3.5. Job title
            if job_title_text:
                job_title_text.opacity = 1.0
                self.page.update()
                time.sleep(0.15)
            
            # 4. Success text
            if success_text:
                success_text.opacity = 1.0
                self.page.update()
                time.sleep(0.3)
            
            # 5. Info cards
            if info_cards:
                info_cards.opacity = 1.0
                self.page.update()
                time.sleep(0.2)
            
            # 6. Loading dots
            if loading_dots:
                loading_dots.opacity = 1.0
                # Animate dots with wave effect
                for i, dot in enumerate(loading_dots.controls):
                    def animate_dot(d, delay):
                        time.sleep(delay)
                        d.opacity = 1.0
                        self.page.update()
                        time.sleep(0.4)
                        d.opacity = 0.3
                        self.page.update()
                    threading.Thread(target=lambda d=dot, delay=i*0.2: animate_dot(d, delay), daemon=True).start()
                self.page.update()
        
        # Start animation sequence
        threading.Thread(target=animate_sequence, daemon=True).start()
        
        # Schedule completion callback after delay
        def delayed_complete():
            import time
            time.sleep(2.0)  # Show welcome screen for 2 seconds
            if self.on_complete:
                print("[WELCOME] Calling on_complete callback after delay")
                try:
                    self.on_complete()
                    print("[WELCOME] on_complete callback executed successfully")
                except Exception as ex:
                    print(f"[WELCOME] Error in on_complete: {ex}")
                    import traceback
                    traceback.print_exc()
        
        thread = threading.Thread(target=delayed_complete, daemon=True)
        thread.start()
