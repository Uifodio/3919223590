#!/usr/bin/env python3
"""
Simple test for ModernButton
"""

import tkinter as tk

class ModernButton(tk.Canvas):
    """Modern animated button with hover effects"""
    
    def __init__(self, parent, text, command=None, icon=None, **kwargs):
        # Extract custom parameters
        hover_bg = kwargs.pop('hover_bg', '#4e4e52')
        pressed_bg = kwargs.pop('pressed_bg', '#2e2e32')
        text_color = kwargs.pop('text_color', '#d4d4d4')
        
        super().__init__(parent, **kwargs)
        self.text = text
        self.command = command
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        
        # Colors
        self.normal_bg = kwargs.get('bg', '#3e3e42')
        self.hover_bg = hover_bg
        self.pressed_bg = pressed_bg
        self.text_color = text_color
        
        print("ModernButton created successfully")

def test_button():
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        btn = ModernButton(root, text="Test", command=None, 
                          bg='#3e3e42', hover_bg='#4e4e52',
                          pressed_bg='#2e2e32', text_color='#d4d4d4')
        print("✓ Button created successfully")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    test_button()