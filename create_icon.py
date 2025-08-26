#!/usr/bin/env python3
"""
Icon Generator for Windows File Manager
Creates a simple icon file for the executable.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_file_manager_icon():
        """Create a simple file manager icon"""
        
        # Create a 256x256 image with a blue background
        size = 256
        img = Image.new('RGBA', (size, size), (0, 120, 215, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a folder icon
        folder_color = (255, 255, 255, 255)  # White
        
        # Folder base
        folder_points = [
            (size * 0.2, size * 0.3),   # Top left
            (size * 0.3, size * 0.25),  # Tab left
            (size * 0.4, size * 0.25),  # Tab right
            (size * 0.8, size * 0.25),  # Top right
            (size * 0.8, size * 0.8),   # Bottom right
            (size * 0.2, size * 0.8),   # Bottom left
        ]
        draw.polygon(folder_points, fill=folder_color)
        
        # Draw some file icons inside the folder
        file_color = (200, 200, 200, 255)  # Light gray
        
        # File 1
        file1_points = [
            (size * 0.3, size * 0.4),
            (size * 0.7, size * 0.4),
            (size * 0.7, size * 0.5),
            (size * 0.3, size * 0.5),
        ]
        draw.rectangle(file1_points, fill=file_color)
        
        # File 2
        file2_points = [
            (size * 0.3, size * 0.55),
            (size * 0.65, size * 0.55),
            (size * 0.65, size * 0.65),
            (size * 0.3, size * 0.65),
        ]
        draw.rectangle(file2_points, fill=file_color)
        
        # File 3
        file3_points = [
            (size * 0.3, size * 0.7),
            (size * 0.6, size * 0.7),
            (size * 0.6, size * 0.75),
            (size * 0.3, size * 0.75),
        ]
        draw.rectangle(file3_points, fill=file_color)
        
        # Save as ICO file
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        
        for icon_size in icon_sizes:
            resized_img = img.resize(icon_size, Image.Resampling.LANCZOS)
            icon_images.append(resized_img)
        
        # Save as ICO
        icon_images[0].save('file_manager.ico', format='ICO', sizes=[(size[0], size[1]) for size in icon_sizes])
        
        print("✓ File manager icon created: file_manager.ico")
        return True
        
    if __name__ == "__main__":
        create_file_manager_icon()
        
except ImportError:
    print("Pillow not available, skipping icon creation")
    # Create a simple text-based icon file
    with open('file_manager.ico', 'w') as f:
        f.write("Icon placeholder - install Pillow for proper icon generation")
    print("Created placeholder icon file")
except Exception as e:
    print(f"Error creating icon: {e}")
    # Create a simple text-based icon file
    with open('file_manager.ico', 'w') as f:
        f.write("Icon placeholder - error in icon generation")
    print("Created placeholder icon file")