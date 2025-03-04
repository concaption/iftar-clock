import tkinter as tk
import tkinter.ttk as ttk
import random
import time
from datetime import datetime
import traceback
from src.sunset_calculator import SunsetCalculator
from src.logger import logger

class IftarApp:
    def __init__(self, root):
        logger.info("Starting Iftar Clock application")
        self.root = root
        self.root.title("Iftar Clock")
        
        # Make window slightly larger and more visible for debugging
        self.root.geometry("140x60")
        self.root.resizable(False, False)
        
        # Disable overrideredirect initially for debugging
        self.root.overrideredirect(False)  # Show window decorations during startup
        
        # Make sure window is visible and on top
        self.root.attributes("-topmost", True)
        self.root.lift()
        
        # Set background color to black
        self.root.configure(bg="black")
        
        # Add some debug output
        logger.info(f"Window ID: {self.root.winfo_id()}")
        logger.info(f"Window exists: {self.root.winfo_exists()}")
        logger.info(f"Window visibility: {self.root.winfo_ismapped()}")
        
        logger.debug("Creating UI")
        # Create UI
        self.create_ui()
        
        logger.debug("Positioning window")
        # Position window in bottom right
        self.position_window_bottom_right()
        
        # Initialize sunset calculator
        logger.debug("Initializing SunsetCalculator")
        try:
            self.sunset_calculator = SunsetCalculator()
            logger.info("SunsetCalculator initialized successfully")
        except Exception as e:
            logger.critical("Failed to initialize SunsetCalculator")
            logger.exception(str(e))
            self.show_error("Failed to initialize application")
            return
        
        # Get initial sunset data
        logger.info("Fetching initial sunset data")
        try:
            self.sunset_calculator.fetch_and_save_sunset()
            
            # Try to get and display the time immediately
            self.update_clock_immediately()
        except Exception as e:
            logger.error("Failed to fetch initial sunset data")
            logger.exception(str(e))
            self.time_var.set("ERROR")
            
        # Start timer to update display
        logger.debug("Starting update timer")
        self.start_timer()
        
        # Add right-click menu
        self.add_context_menu()
        
        logger.info("Application initialized successfully")
        
        # Force update
        self.root.update_idletasks()
        self.root.update()
        
        # Log some info about what's displayed
        logger.info(f"Current time display: {self.time_var.get()}")
        logger.info(f"Window geometry: {self.root.geometry()}")
        logger.info(f"Window mapped: {self.root.winfo_ismapped()}")
        logger.info(f"Window viewable: {self.root.winfo_viewable()}")
        
        # Wait a bit and then hide window decoration
        self.root.after(3000, self.enable_borderless_mode)
    
    def enable_borderless_mode(self):
        """Enable borderless window mode after initial display"""
        logger.info("Enabling borderless window mode")
        self.root.overrideredirect(True)
        self.root.update()
    
    def create_ui(self):
        """Create a simple UI showing only the countdown"""
        # Create a frame to contain everything
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label to show what this is
        self.title_label = tk.Label(
            main_frame,
            text="Iftar in",
            font=("Arial", 8),
            fg="#AAAAAA",
            bg="black",
            padx=5,
            # Fix the pady parameter - it needs to be a simple integer for Tkinter
            pady=5
        )
        self.title_label.pack(anchor=tk.W)
        
        # Countdown label with a large font
        self.time_var = tk.StringVar(value="--:--")
        self.time_label = tk.Label(
            main_frame,
            textvariable=self.time_var,
            font=("Consolas", 20, "bold"),
            fg="#00FF00",  # Green text like a digital clock
            bg="black",
            padx=5,
            pady=0
        )
        self.time_label.pack(anchor=tk.W)
        logger.debug("UI created")
    
    def position_window_bottom_right(self):
        """Position the window at the bottom right of the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = 140
        window_height = 60
        
        x = screen_width - window_width - 20
        y = screen_height - window_height - 60
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        logger.debug(f"Window positioned at {x},{y} (screen size: {screen_width}x{screen_height})")
    
    def update_clock_immediately(self):
        """Update the clock display right now"""
        try:
            time_str = self.sunset_calculator.format_remaining_time()
            self.time_var.set(time_str)
            logger.info(f"Initial clock value set to: {time_str}")
        except Exception as e:
            logger.exception("Error updating clock immediately")
            self.time_var.set("ERROR")
            
        # Force the UI to update
        self.root.update_idletasks()
    
    def start_timer(self):
        """Start timer to update clock every second"""
        try:
            self.update_clock()
        except Exception as e:
            logger.error("Error in update_clock")
            logger.exception(str(e))
            
        # Make sure timer keeps running
        self.root.after(1000, self.start_timer)  # Update every second
    
    def update_clock(self):
        """Update the countdown display"""
        logger.debug("Updating clock display")
        try:
            time_str = self.sunset_calculator.format_remaining_time()
            current_value = self.time_var.get()
            
            if time_str != current_value:
                logger.info(f"Updating clock from {current_value} to {time_str}")
            
            # Check if we need to update the title label (if showing tomorrow's time)
            if time_str.startswith("T "):
                self.title_label.config(text="Tomorrow's Iftar in")
                time_str = time_str[2:]  # Remove the T prefix for display
            else:
                self.title_label.config(text="Iftar in")
            
            self.time_var.set(time_str)
            
            # Change color if seconds are 0 (minute change)
            now = datetime.now()
            if now.second == 0:
                new_color = self.get_random_color()
                logger.debug(f"Changing color to {new_color}")
                self.time_label.config(fg=new_color)
            
            # Refetch sunset data every hour
            if now.minute == 0 and now.second == 0:
                logger.info("Hourly update: Fetching new sunset data")
                self.sunset_calculator.fetch_and_save_sunset()
                
            # Log periodically to show the app is running
            if now.second % 30 == 0:
                logger.info(f"Clock running: {now.strftime('%H:%M:%S')} - Iftar in: {time_str}")
                
            # Make sure the window is visible
            if now.second % 10 == 0 and not self.root.winfo_viewable():
                logger.warning("Window not visible, trying to make it visible")
                self.make_window_visible()
                
        except Exception as e:
            logger.error("Error updating clock")
            logger.exception(str(e))
            self.time_var.set("ERROR")
    
    def make_window_visible(self):
        """Attempt to make the window visible again"""
        try:
            self.root.deiconify()
            self.root.attributes('-topmost', True)
            self.root.update()
        except Exception as e:
            logger.error(f"Failed to make window visible: {e}")
    
    def get_random_color(self):
        """Generate a random bright color"""
        # Generate brighter colors by ensuring at least one component is high
        r = random.randint(128, 255)
        g = random.randint(128, 255)
        b = random.randint(128, 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def add_context_menu(self):
        """Add context menu on right-click"""
        logger.debug("Adding context menu")
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Refresh", command=self.refresh_data)
        menu.add_command(label="Toggle Border", command=self.toggle_border)
        menu.add_command(label="Show logs", command=self.show_logs)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.exit_app)
        
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        
        self.root.bind("<Button-3>", show_menu)  # Right click
        
        # Allow dragging the window
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)
    
    def toggle_border(self):
        """Toggle window border for debugging"""
        if self.root.overrideredirect():
            self.root.overrideredirect(False)
            logger.info("Window border enabled")
        else:
            self.root.overrideredirect(True)
            logger.info("Window border disabled")
        # Ensure window stays on top and visible
        self.make_window_visible()
    
    def start_move(self, event):
        logger.debug(f"Starting window move from {self.root.winfo_x()},{self.root.winfo_y()}")
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        logger.debug(f"Window moved to {self.root.winfo_x()},{self.root.winfo_y()}")
        self.x = None
        self.y = None
    
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def refresh_data(self):
        """Force refresh of sunset data"""
        logger.info("Manually refreshing sunset data")
        try:
            # Clear cached data
            self.sunset_calculator.sunsets = {}
            self.sunset_calculator.fetch_and_save_sunset()
            self.update_clock_immediately()  # Update clock right away
            logger.info("Manual refresh completed")
        except Exception as e:
            logger.error("Error during manual refresh")
            logger.exception(str(e))
            self.show_error("Failed to refresh data")
    
    def show_logs(self):
        """Show the log file"""
        logger.info("Showing log files")
        import os
        import subprocess
        import platform
        
        log_dir = os.path.join(os.path.expanduser('~'), '.iftar_clock')
        
        if platform.system() == 'Windows':
            os.startfile(log_dir)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', log_dir])
        else:  # Linux
            subprocess.call(['xdg-open', log_dir])
    
    def exit_app(self):
        """Exit the application"""
        logger.info("Application shutting down")
        self.root.destroy()
    
    def show_error(self, message):
        """Show error message"""
        logger.debug(f"Displaying error message: {message}")
        top = tk.Toplevel(self.root)
        top.title("Error")
        top.geometry("300x100")
        
        label = tk.Label(top, text=message, wraplength=280)
        label.pack(pady=10)
        
        button = tk.Button(top, text="OK", command=top.destroy)
        button.pack(pady=10)

def main():
    try:
        # Create the root window 
        root = tk.Tk()
        
        # Display a simple splash message while loading
        splash = tk.Toplevel(root)
        splash.title("Loading")
        splash.geometry("200x100")
        tk.Label(splash, text="Loading Iftar Clock...").pack(pady=20)
        splash.update()
        
        # Hide the main root window while loading
        root.withdraw()
        
        # Create our application
        app = IftarApp(root)
        
        # Close the splash screen
        splash.destroy()
        
        # Now show the main window
        root.deiconify()
        root.lift()
        
        logger.info("Entering main event loop")
        root.mainloop()
        logger.info("Application closed")
    except Exception as e:
        logger.critical("Unhandled exception in main")
        logger.exception(str(e))
        # Try to show a message box if possible
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"An unhandled error occurred: {str(e)}")
        except:
            pass

if __name__ == "__main__":
    main()
