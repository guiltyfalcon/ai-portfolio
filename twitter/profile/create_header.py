#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont

# Create Twitter header: 1500x500px
width, height = 1500, 500
img = Image.new('RGB', (width, height), color='#0A0A0A')  # Black background
draw = ImageDraw.Draw(img)

# Try to use a default font, fall back to default if not available
try:
    # Try common font paths
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_large = None
    font_medium = None
    
    for font_path in font_paths:
        try:
            font_large = ImageFont.truetype(font_path, 72)
            font_medium = ImageFont.truetype(font_path, 36)
            break
        except:
            continue
    
    if font_large is None:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
except Exception as e:
    print(f"Font error: {e}")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()

# Text: "BetBrain AI" in white, large
text_main = "BetBrain AI"
# Text: "Data-Driven NBA Picks" in green (#00FF88)
text_sub = "Data-Driven NBA Picks"

# Get text bounding boxes
bbox_main = draw.textbbox((0, 0), text_main, font=font_large)
bbox_sub = draw.textbbox((0, 0), text_sub, font=font_medium)

text_main_width = bbox_main[2] - bbox_main[0]
text_sub_width = bbox_sub[2] - bbox_sub[0]

# Center the text
x_main = (width - text_main_width) // 2
x_sub = (width - text_sub_width) // 2

# Position: main text at 30% from top, subtitle at 55% from top
y_main = int(height * 0.30)
y_sub = int(height * 0.55)

# Draw main text in white
draw.text((x_main, y_main), text_main, fill='#FFFFFF', font=font_large)

# Draw subtitle in green
draw.text((x_sub, y_sub), text_sub, fill='#00FF88', font=font_medium)

# Add brain emoji - we'll use a simple representation or skip if can't render
# For simplicity, let's add it as text
try:
    draw.text((x_main + text_main_width + 20, y_main), "🧠", fill='#FFFFFF', font=font_large)
except:
    pass  # Skip emoji if font doesn't support it

# Save
img.save('/Users/djryan/git/guiltyfalcon/ai-portfolio/twitter/profile/header_1500x500.png', 'PNG')
print("Header graphic created: /Users/djryan/git/guiltyfalcon/ai-portfolio/twitter/profile/header_1500x500.png")
