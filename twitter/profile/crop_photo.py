#!/usr/bin/env python3
from PIL import Image

# Open the image
img = Image.open('/Users/djryan/.openclaw/media/inbound/file_8---e83c3dc8-4cb7-4246-b14a-6b026d04456e.jpg')

# Get dimensions
width, height = img.size
print(f"Original size: {width}x{height}")

# For a profile picture, we want to focus on the upper body/face
# Based on the photo, the person is centered horizontally
# Crop to a square focusing on the upper portion where the face is

# Calculate crop area for 400x400
# Center horizontally, focus on upper 60% of the image where face/upper body is
target_size = 400

# Start from about 15% from top (to include head) to 75% from top (upper body)
# This gives us a good face-centered crop
top_offset = int(height * 0.12)
bottom_offset = int(height * 0.72)
crop_height = bottom_offset - top_offset

# Center horizontally
left_offset = int((width - crop_height) / 2)
right_offset = left_offset + crop_height

# Crop to square first
square_crop = (left_offset, top_offset, right_offset, bottom_offset)
img_cropped = img.crop(square_crop)

# Resize to 400x400
img_final = img_cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)

# Save
img_final.save('/Users/djryan/git/guiltyfalcon/ai-portfolio/twitter/profile/profile_photo_400x400.jpg', 'JPEG', quality=95)
print(f"Saved cropped profile photo to /Users/djryan/git/guiltyfalcon/ai-portfolio/twitter/profile/profile_photo_400x400.jpg")
