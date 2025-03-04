import sys
import os
import traceback

# Try to import and initialize our logger first
try:
    from src.logger import logger
    logger.info("Starting iftar-clock application")
except Exception as ex:
    print(f"Failed to initialize logger: {ex}")
    print(traceback.format_exc())
    sys.exit(1)

# Try to run the application
try:
    import tkinter as tk
    from src.iftar_app import main
    
    # Print some environment information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Tkinter version: {tk.TkVersion}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    if __name__ == "__main__":
        main()
except Exception as e:
    logger.critical("Fatal error in main script")
    logger.exception(str(e))
    
    # Try to show a message box if possible
    try:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"A fatal error occurred: {str(e)}")
    except:
        # If even that fails, print to console
        print(f"FATAL ERROR: {str(e)}")
        print(traceback.format_exc())
