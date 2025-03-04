import tkinter as tk
from tkinter import ttk, colorchooser
from settings import load_settings, save_settings

class SettingsWindow:
    def __init__(self, parent=None, callback=None):
        self.parent = parent
        self.callback = callback
        self.settings = load_settings()
        
        # Create settings window
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Iftar Clock Settings")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.appearance_tab = ttk.Frame(self.notebook)
        self.description_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.appearance_tab, text="Appearance")
        self.notebook.add(self.description_tab, text="Description")
        
        # Populate tabs
        self.setup_appearance_tab()
        self.setup_description_tab()
        
        # Create buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def setup_appearance_tab(self):
        frame = ttk.LabelFrame(self.appearance_tab, text="Font & Color")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Font family
        ttk.Label(frame, text="Font Family:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.font_family = ttk.Combobox(frame, values=["Arial", "Helvetica", "Times", "Courier"])
        self.font_family.set(self.settings["font_family"])
        self.font_family.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Font size
        ttk.Label(frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.font_size = ttk.Spinbox(frame, from_=8, to=72)
        self.font_size.set(self.settings["font_size"])
        self.font_size.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Font color
        ttk.Label(frame, text="Font Color:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.font_color_frame = ttk.Frame(frame)
        self.font_color_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.font_color = tk.Label(self.font_color_frame, text="      ", bg=self.settings["font_color"])
        self.font_color.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.font_color_frame, text="Change...", 
                   command=lambda: self.choose_color("font_color")).pack(side=tk.LEFT)
        
        # Background color
        ttk.Label(frame, text="Background Color:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.bg_color_frame = ttk.Frame(frame)
        self.bg_color_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.bg_color = tk.Label(self.bg_color_frame, text="      ", bg=self.settings["background_color"])
        self.bg_color.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.bg_color_frame, text="Change...", 
                   command=lambda: self.choose_color("background_color")).pack(side=tk.LEFT)
        
        # Opacity
        ttk.Label(frame, text="Opacity:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.opacity = ttk.Scale(frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL)
        self.opacity.set(self.settings["opacity"])
        self.opacity.grid(row=4, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
    
    def setup_description_tab(self):
        frame = ttk.LabelFrame(self.description_tab, text="Description Text")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show description
        self.show_description = tk.BooleanVar(value=self.settings["show_description"])
        ttk.Checkbutton(frame, text="Show Description", variable=self.show_description).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Description text
        ttk.Label(frame, text="Text:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.description = ttk.Entry(frame, width=30)
        self.description.insert(0, self.settings["description"])
        self.description.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Description font size
        ttk.Label(frame, text="Font Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_font_size = ttk.Spinbox(frame, from_=8, to=24)
        self.desc_font_size.set(self.settings["description_font_size"])
        self.desc_font_size.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Description font color
        ttk.Label(frame, text="Font Color:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_color_frame = ttk.Frame(frame)
        self.desc_color_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.desc_color = tk.Label(self.desc_color_frame, text="      ", bg=self.settings["description_font_color"])
        self.desc_color.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.desc_color_frame, text="Change...", 
                   command=lambda: self.choose_color("description_font_color")).pack(side=tk.LEFT)
    
    def choose_color(self, setting_key):
        current_color = self.settings[setting_key]
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.settings[setting_key] = color
            if setting_key == "font_color":
                self.font_color.config(bg=color)
            elif setting_key == "background_color":
                self.bg_color.config(bg=color)
            elif setting_key == "description_font_color":
                self.desc_color.config(bg=color)
    
    def save_settings(self):
        # Update settings from UI
        self.settings["font_family"] = self.font_family.get()
        self.settings["font_size"] = int(self.font_size.get())
        self.settings["opacity"] = float(self.opacity.get())
        self.settings["show_description"] = self.show_description.get()
        self.settings["description"] = self.description.get()
        self.settings["description_font_size"] = int(self.desc_font_size.get())
        
        # Save to file
        save_settings(self.settings)
        
        # Call callback if provided
        if self.callback:
            self.callback(self.settings)
        
        self.window.destroy()
    
    def run(self):
        if not self.parent:
            self.window.mainloop()

if __name__ == "__main__":
    # For testing
    settings_window = SettingsWindow()
    settings_window.run()
