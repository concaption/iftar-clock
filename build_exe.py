"""
Build script to convert the Iftar Clock application into an executable file.
This script uses PyInstaller to create a standalone Windows executable.
"""

import os
import sys
import shutil
import subprocess
import platform

def main():
    print("Iftar Clock - Build Executable")
    print("------------------------------\n")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller is not installed. Installing it now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.")
        except Exception as e:
            print(f"Failed to install PyInstaller: {e}")
            print("Please install it manually using: pip install pyinstaller")
            input("\nPress Enter to exit...")
            return
    
    # Create the build directory if it doesn't exist
    os.makedirs("build", exist_ok=True)
    
    # Create icon file if it doesn't exist
    icon_path = create_icon()
    
    # Build the application
    print("\nBuilding executable with PyInstaller...")
    cmd = [
        "pyinstaller",
        "--name=IftarClock",
        f"--icon={icon_path}",
        "--windowed",  # No console window
        "--onefile",   # Single executable file
        "--noconfirm", # Overwrite existing build
        "--add-data", f"LICENSE{os.pathsep}.",  # Include license file
        "--clean",     # Clean PyInstaller cache
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild completed successfully!")
        
        # Copy the executable to the root directory for easy access
        src_path = os.path.join("dist", "IftarClock.exe")
        dst_path = "IftarClock.exe"
        shutil.copy2(src_path, dst_path)
        print(f"\nExecutable copied to: {os.path.abspath(dst_path)}")
        
    except Exception as e:
        print(f"\nBuild failed: {e}")
    
    print("\nDone. If successful, you can now run IftarClock.exe")
    input("\nPress Enter to exit...")

def create_icon():
    """Create an icon for the application if one doesn't exist"""
    icon_path = os.path.join("build", "iftar_clock_icon.ico")
    
    if os.path.exists(icon_path):
        return icon_path
        
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        print("Creating application icon...")
        
        # Create a 256x256 image with a transparent background
        img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a circle background
        draw.ellipse((16, 16, 240, 240), fill=(0, 0, 0, 255), outline=(0, 180, 0, 255), width=5)
        
        # Try to load a font or use default
        try:
            font = ImageFont.truetype("arial.ttf", 96)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        time_text = "18:00"
        center_x = 128
        center_y = 128
        
        # Get text size
        try:
            text_width = draw.textlength(time_text, font=font)
            text_x = center_x - text_width / 2
        except AttributeError:  # For older Pillow versions
            text_width, text_height = draw.textsize(time_text, font=font)
            text_x = center_x - text_width / 2
            
        draw.text((text_x, center_y - 60), time_text, font=font, fill=(0, 255, 0, 255))
        
        # Add "Iftar" text below
        try:
            small_font = ImageFont.truetype("arial.ttf", 36)
        except:
            small_font = ImageFont.load_default()
            
        iftar_text = "Iftar"
        try:
            iftar_width = draw.textlength(iftar_text, font=small_font)
            iftar_x = center_x - iftar_width / 2
        except AttributeError:  # For older Pillow versions
            iftar_width, iftar_height = draw.textsize(iftar_text, font=small_font)
            iftar_x = center_x - iftar_width / 2
            
        draw.text((iftar_x, center_y + 20), iftar_text, font=small_font, fill=(200, 200, 200, 255))
        
        # Save as .ico file
        img.save(icon_path, format="ICO")
        print(f"Icon created at: {icon_path}")
        return icon_path
        
    except ImportError:
        print("Could not create icon: Pillow library not installed.")
        print("Using default icon.")
        return None
    except Exception as e:
        print(f"Error creating icon: {e}")
        return None

if __name__ == "__main__":
    main()
