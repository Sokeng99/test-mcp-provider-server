"""
Create placeholder icons for Teams app
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create teams-app directory if it doesn't exist
os.makedirs(".", exist_ok=True)

# Create color icon (192x192)
color_img = Image.new('RGB', (192, 192), color='#4A90E2')
draw = ImageDraw.Draw(color_img)

# Draw a simple "X" logo
draw.line([(40, 40), (152, 152)], fill='white', width=20)
draw.line([(152, 40), (40, 152)], fill='white', width=20)

# Draw circle around it
draw.ellipse([20, 20, 172, 172], outline='white', width=8)

color_img.save('color.png')
print("Created color.png (192x192)")

# Create outline icon (32x32)
outline_img = Image.new('RGBA', (32, 32), color=(255, 255, 255, 0))
draw = ImageDraw.Draw(outline_img)

# Draw a simple "X" logo in white
draw.line([(8, 8), (24, 24)], fill='white', width=3)
draw.line([(24, 8), (8, 24)], fill='white', width=3)

# Draw circle
draw.ellipse([4, 4, 28, 28], outline='white', width=2)

outline_img.save('outline.png')
print("Created outline.png (32x32)")

print("\nIcons created successfully!")
print("You can replace these with your own custom icons if desired.")
