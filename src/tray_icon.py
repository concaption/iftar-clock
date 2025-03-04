import os
import sys
import threading
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem as item
import tkinter as tk
from src.logger import logger

class TrayIconApp:
    def __init__(self, app_instance):
        self.app = app_instance
        self.root = self.app.root
        self.time_var = self.app.time_var
        
        # Create the icon
        self.create_icon()
        
        # Start the icon in a separate thread
        self.tray_thread = threading.Thread(target=self.run_tray_icon)
        self.tray_thread.daemon = True
        self.tray_thread.start()
        
        logger.info("Tray icon initialized")
    
    def create_icon(self):
        """Create a tray icon with a custom icon image"""
        logger.debug("Creating system tray icon")
        
        # Create a simple icon with the current time
        self.icon = self.create_time_icon("--:--")
        
        # Create the menu
        self.menu = (
            item('Show/Hide Window', self.toggle_window),
            item('Refresh Data', self.app.refresh_data),
            item('Show Logs', self.app.show_logs),
            item('Exit', self.exit_app)
        )
        
        # Create the tray icon
        self.tray_icon = pystray.Icon("iftar_clock", self.icon, "Iftar Clock", self.menu)
        
        # Update the icon every 30 seconds
        self.root.after(30000, self.update_icon)
    
    def create_time_icon(self, time_text):
        """Create an icon image with the current countdown time"""
        # Create a blank image for icon (64x64 with transparent background)
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Add a circle background
        draw.ellipse((0, 0, 64, 64), fill=(0, 0, 0, 255))
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw the time text
        text_width = draw.textlength(time_text, font=font)
        text_x = (64 - text_width) / 2
        draw.text((text_x, 20), time_text, font=font, fill=(0, 255, 0, 255))
        
        return image
    
    def update_icon(self):
        """Update the tray icon with the current time"""
        try:
            # Get the current countdown time
            time_text = self.time_var.get()
            
            # Update the icon
            new_icon = self.create_time_icon(time_text)
            self.tray_icon.icon = new_icon
            
            logger.debug(f"Updated tray icon with time: {time_text}")
            
            # Schedule next update
            if self.root.winfo_exists():  # Check if root still exists
                self.root.after(30000, self.update_icon)
        except Exception as e:
            logger.error(f"Error updating tray icon: {e}")
    
    def run_tray_icon(self):
        """Run the tray icon in a separate thread"""
        try:
            logger.info("Starting system tray icon")
            self.tray_icon.run()
        except Exception as e:
            logger.error(f"Error running tray icon: {e}")
    
    def toggle_window(self):
        """Show or hide the main window"""
        if self.root.winfo_viewable():
            self.root.withdraw()  # Hide window
            logger.info("Window hidden")
        else:
            self.root.deiconify()  # Show window
            self.root.lift()  # Bring to front
            self.root.attributes('-topmost', True)  # Keep on top
            self.root.update()
            logger.info("Window shown")
    
    def exit_app(self):
        """Exit the application"""
        logger.info("Exiting application from tray icon")
        self.tray_icon.stop()
        self.root.destroy()
