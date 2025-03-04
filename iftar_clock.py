import tkinter as tk
from datetime import datetime, timedelta
import threading
import time
import json
import os
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import requests
from pathlib import Path

from src.location_finder import LocationFinder
from sunset_finder import SunsetFinder
from settings import Settings, load_settings, save_settings

class IftarClock:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("IftarClock")
        self.root.overrideredirect(True)  # No window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.8)  # Window transparency
        
        # Load settings
        self.settings = load_settings()
        
        # Create UI elements
        self.setup_ui()
        
        # Initialize location and sunset finder
        self.location_finder = LocationFinder()
        self.sunset_finder = SunsetFinder()
        
        # System tray setup
        self.setup_system_tray()
        
        # Set up dragging functionality
        self._drag_data = {"x": 0, "y": 0}
        self.frame.bind("<ButtonPress-1>", self.on_drag_start)
        self.frame.bind("<B1-Motion>", self.on_drag_motion)
        self.frame.bind("<Double-Button-1>", self.on_double_click)
        
        # Center window on screen
        self.reset_position()
        
        # Initialize sunset time
        self.sunset_time = None
        
        # Start timer for updating display
        self.running = True
        self.update_thread = threading.Thread(target=self.update_time)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Fetch sunset time
        self.fetch_and_save_sunset()

    def setup_ui(self):
        # Main frame
        self.frame = tk.Frame(
            self.root, 
            bg=self.settings["background_color"],
            padx=10,
            pady=10
        )
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Time display label
        self.time_label = tk.Label(
            self.frame,
            text="--:--:--",
            font=(self.settings["font_family"], self.settings["font_size"]),
            fg=self.settings["font_color"],
            bg=self.settings["background_color"]
        )
        self.time_label.pack()
        
        # Description label
        self.desc_label = tk.Label(
            self.frame,
            text=self.settings["description"],
            font=(self.settings["font_family"], self.settings["description_font_size"]),
            fg=self.settings["description_font_color"],
            bg=self.settings["background_color"]
        )
        
        if self.settings["show_description"]:
            self.desc_label.pack()
    
    def setup_system_tray(self):
        image = Image.open(os.path.join(os.path.dirname(__file__), "icon.png")) if os.path.exists(os.path.join(os.path.dirname(__file__), "icon.png")) else Image.new('RGB', (16, 16), color = (0, 0, 255))
        self.icon = pystray.Icon(
            "iftar_clock", 
            image, 
            "Iftar Clock",
            menu=pystray.Menu(
                item('Settings', self.open_settings),
                item('Reset Position', self.reset_position),
                item('Exit', self.exit_app)
            )
        )
        threading.Thread(target=self.icon.run).start()
    
    def open_settings(self, icon=None, item=None):
        self.root.deiconify()
        # In a real implementation, you would create a settings dialog here
        print("Settings dialog would open here")
    
    def reset_position(self, icon=None, item=None):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 180
        window_height = 100
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.deiconify()
    
    def exit_app(self, icon=None, item=None):
        self.running = False
        self.icon.stop()
        self.root.quit()
    
    def on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def on_drag_motion(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def on_double_click(self, event):
        self.fetch_and_save_sunset()
    
    def apply_settings(self):
        # Apply font settings
        self.time_label.config(
            font=(self.settings["font_family"], self.settings["font_size"]),
            fg=self.settings["font_color"],
            bg=self.settings["background_color"]
        )
        
        # Apply background settings
        self.frame.config(bg=self.settings["background_color"])
        self.root.attributes('-alpha', self.settings["opacity"])
        
        # Apply description settings
        self.desc_label.config(
            text=self.settings["description"],
            font=(self.settings["font_family"], self.settings["description_font_size"]),
            fg=self.settings["description_font_color"],
            bg=self.settings["background_color"]
        )
        
        if self.settings["show_description"]:
            self.desc_label.pack()
        else:
            self.desc_label.pack_forget()
    
    def fetch_and_save_sunset(self):
        try:
            location = self.location_finder.get_location()
            if location:
                sunset_response = self.sunset_finder.fetch_sunset(location)
                if sunset_response and sunset_response["status"] == "OK":
                    # Parse the UTC time string
                    sunset_str = sunset_response["results"]["sunset"]
                    self.sunset_time = datetime.strptime(sunset_str, "%Y-%m-%dT%H:%M:%S%z")
                    print(f"Sunset time set to: {self.sunset_time}")
        except Exception as e:
            print(f"Error fetching sunset time: {e}")
    
    def get_remaining_time(self):
        if not self.sunset_time:
            return "--:--:--"
        
        now = datetime.now(self.sunset_time.tzinfo)
        
        if now > self.sunset_time:
            # If after sunset, show 0
            return "00:00:00"
        else:
            # Calculate time remaining
            remaining = self.sunset_time - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def update_time(self):
        while self.running:
            time_str = self.get_remaining_time()
            # Update label in the main thread
            self.root.after(0, lambda: self.time_label.config(text=time_str))
            time.sleep(1)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = IftarClock()
    app.run()
