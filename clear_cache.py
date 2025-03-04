"""
Utility script to clear the cached sunset data
Run this if you're experiencing issues with incorrect times
"""

import os
import sys
import json
from datetime import datetime

def main():
    print("Iftar Clock - Cache Cleaner")
    print("--------------------------")
    
    cache_file = os.path.join(os.path.expanduser('~'), 'iftar_clock.json')
    
    if os.path.exists(cache_file):
        print(f"Cache file found: {cache_file}")
        
        # Try to read and display current cached data
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                print(f"\nCurrent cache contains {len(data)} entries:")
                for day, sunset in data.items():
                    try:
                        dt = datetime.fromisoformat(sunset)
                        print(f"  Day {day}: {sunset} ({dt.strftime('%Y-%m-%d %H:%M:%S %Z')})")
                    except:
                        print(f"  Day {day}: {sunset} (Invalid format)")
        except Exception as e:
            print(f"Error reading cache: {e}")
        
        # Ask for confirmation before clearing
        confirm = input("\nDo you want to clear the cache? (y/N): ")
        
        if confirm.lower() == 'y':
            try:
                # Backup existing file
                backup_file = cache_file + f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                with open(cache_file, 'r') as src:
                    with open(backup_file, 'w') as dst:
                        dst.write(src.read())
                
                # Write empty cache
                with open(cache_file, 'w') as f:
                    json.dump({}, f)
                
                print(f"\nCache cleared successfully!")
                print(f"Backup saved to: {backup_file}")
            except Exception as e:
                print(f"Error clearing cache: {e}")
        else:
            print("Operation cancelled")
    else:
        print(f"No cache file found at {cache_file}")
    
    print("\nDone. The next time you run Iftar Clock, it will fetch fresh sunset data.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
