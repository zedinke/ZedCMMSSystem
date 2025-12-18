"""
Modern loading screen komponens animációval
"""

import flet as ft
# Compatibility for flet 0.23.2 - Icons are strings, not ft.Icons
if not hasattr(ft, 'Icons'):
    from utils.flet_icons import Icons
    ft.Icons = Icons
import asyncio
from typing import Callable


class LoadingScreen:
    """Modern loading screen animációval"""
    
    def __init__(self, page: ft.Page, duration: float = 5.0, on_complete: Callable = None):
        self.page = page
        self.duration = duration
        self.on_complete = on_complete
        self.progress = 0.0
        
    def build(self):
        """Build the loading screen"""
        # Animated progress indicator
        progress_ring = ft.ProgressRing(
            width=80,
            height=80,
            stroke_width=6,
            color="#6366F1",
            bgcolor="#E0E7FF",
        )
        
        # Animated dots
        dots_container = ft.Row(
            controls=[
                ft.Container(
                    width=12,
                    height=12,
                    border_radius=6,
                    bgcolor="#6366F1",
                    animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
                    opacity=0.3,
                ),
                ft.Container(
                    width=12,
                    height=12,
                    border_radius=6,
                    bgcolor="#6366F1",
                    animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
                    opacity=0.3,
                ),
                ft.Container(
                    width=12,
                    height=12,
                    border_radius=6,
                    bgcolor="#6366F1",
                    animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
                    opacity=0.3,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Logo/Icon with animation
        logo = ft.Container(
            content=ft.Icon(
                ft.Icons.SECURITY,
                size=64,
                color="#6366F1",
            ),
            animate_rotation=ft.Animation(2000, ft.AnimationCurve.LINEAR),
            rotate=ft.Rotate(0, ft.alignment.center),
        )
        
        # Text
        loading_text = ft.Text(
            "Betöltés...",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#1F2937",
        )
        
        subtitle_text = ft.Text(
            "Kérjük várjon",
            size=14,
            color="#6B7280",
        )
        
        return ft.Container(
            expand=True,
            bgcolor="#F8FAFC",
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Column(
                        controls=[
                            logo,
                            ft.Container(height=30),
                            progress_ring,
                            ft.Container(height=20),
                            loading_text,
                            ft.Container(height=8),
                            subtitle_text,
                            ft.Container(height=20),
                            dots_container,
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
    
    async def animate(self):
        """Animate the loading screen"""
        # Get controls
        controls = self.page.controls
        if not controls:
            return
        
        loading_container = controls[0] if controls else None
        if not loading_container:
            return
        
        # Find logo and dots
        logo = None
        dots = None
        
        def find_controls(control):
            nonlocal logo, dots
            if isinstance(control, ft.Container) and hasattr(control, 'content'):
                if isinstance(control.content, ft.Icon) and control.content.name == ft.Icons.SECURITY:
                    logo = control
                elif isinstance(control.content, ft.Row):
                    dots = control.content
                if hasattr(control.content, 'controls'):
                    for c in control.content.controls:
                        find_controls(c)
            elif hasattr(control, 'controls'):
                for c in control.controls:
                    find_controls(c)
        
        find_controls(loading_container)
        
        # Animate logo rotation
        if logo:
            for i in range(int(self.duration * 2)):
                logo.rotate = ft.Rotate(i * 180, ft.alignment.center)
                self.page.update()
                await asyncio.sleep(0.5)
        
        # Animate dots
        if dots and len(dots.controls) >= 3:
            for i in range(int(self.duration * 3)):
                for idx, dot in enumerate(dots.controls):
                    if isinstance(dot, ft.Container):
                        # Stagger animation
                        delay = (i * 3 + idx) % 3
                        dot.opacity = 0.3 + (0.7 if delay == 0 else 0)
                        self.page.update()
                await asyncio.sleep(0.33)
    
    def show(self):
        """Show loading screen - non-blocking"""
        loading_view = self.build()
        self.page.controls.clear()
        self.page.add(loading_view)
        self.page.update()
        
        # Start animation and timer in background
        import threading
        def run_animation():
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.animate())
            except Exception as e:
                print(f"[LOADING] Animation error: {e}")
            finally:
                try:
                    loop.close()
                except:
                    pass
        
        def run_timer():
            import time
            time.sleep(self.duration)
            self.fade_out()
        
        animation_thread = threading.Thread(target=run_animation, daemon=True)
        animation_thread.start()
        
        timer_thread = threading.Thread(target=run_timer, daemon=True)
        timer_thread.start()
    
    def hide(self):
        """Immediately hide the loading screen (for errors)"""
        if self.page.controls:
            # Clear the loading screen immediately
            self.page.controls.clear()
            self.page.update()
    
    def fade_out(self):
        """Fade out the loading screen"""
        if self.page.controls:
            container = self.page.controls[0]
            if isinstance(container, ft.Container):
                container.opacity = 1.0
                container.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_OUT)
                
                # Fade out
                for i in range(10):
                    container.opacity = 1.0 - (i / 10.0)
                    self.page.update()
                    import time
                    time.sleep(0.05)
        
        if self.on_complete:
            self.on_complete()

