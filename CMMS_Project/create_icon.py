"""
Create a simple icon file for the CMMS application
This script generates a basic .ico file using PIL/Pillow
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_icon():
    """Create a simple icon file"""
    icon_path = Path("icon.ico")
    
    # Create images for different sizes
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Create a new image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a blue rounded rectangle background
        margin = size // 8
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=size // 6,
            fill=(59, 130, 246, 255)  # Blue color
        )
        
        # Draw "C" letter in white
        try:
            # Try to use a font if available
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        text = "C"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Convert to RGB for ICO format (ICO doesn't support RGBA well)
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
        images.append(rgb_img)
    
    # Save as ICO file
    images[0].save(
        icon_path,
        format='ICO',
        sizes=[(s, s) for s in sizes]
    )
    
    print(f"[OK] Icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    try:
        create_icon()
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("Note: PIL/Pillow is required. Install with: pip install Pillow")
        print("Creating placeholder icon file...")
        # Create a minimal placeholder
        Path("icon.ico").touch()
        print("[OK] Placeholder icon.ico created (you may want to replace it with a proper icon)")

