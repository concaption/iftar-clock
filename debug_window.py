"""
Debug script to check if Tkinter is working properly.
Run this script to see if basic Tkinter functionality works on your system.
"""

import tkinter as tk
import sys
import platform
import os

def main():
    # Print system info
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Tkinter version: {tk.TkVersion}")
    print(f"Current directory: {os.getcwd()}")
    
    # Create root window
    root = tk.Tk()
    root.title("Debug Window")
    root.geometry("300x200")
    
    # Add a label
    label = tk.Label(root, text="If you can see this, Tkinter is working!")
    label.pack(pady=20)
    
    # Add info labels
    info_text = f"Python: {sys.version}\nTkinter: {tk.TkVersion}\nPlatform: {platform.platform()}"
    info_label = tk.Label(root, text=info_text, justify=tk.LEFT)
    info_label.pack(pady=10)
    
    # Add a button that closes the window
    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=10)
    
    # Start the main loop
    print("Starting Tkinter main loop...")
    root.mainloop()
    print("Window closed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
