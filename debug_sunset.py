"""
Debug script to specifically test sunset time calculation
Run this to check if the SunsetCalculator can get accurate times
"""

import sys
from datetime import datetime
from src.logger import logger
from src.location_finder import LocationFinder
from src.sunset_finder import SunsetFinder
from src.sunset_calculator import SunsetCalculator

def main():
    print("\n=== Iftar Clock Sunset Debug ===\n")
    print(f"Current time: {datetime.now()}")
    print(f"Current time (with tz): {datetime.now().astimezone()}")
    
    # Test location finder
    print("\nTesting Location Finder...")
    location_finder = LocationFinder()
    location = location_finder.get_current_location()
    
    if location:
        print(f"Location found: {location.city}, {location.country}")
        print(f"Coordinates: {location.lat}, {location.lng}")
        print(f"Timezone: {location.timezone}")
    else:
        print("Failed to find location")
    
    # Test sunset finder directly
    print("\nTesting Sunset Finder...")
    if location:
        sunset_finder = SunsetFinder()
        sunset_data = sunset_finder.fetch_sunset(location)
        
        if sunset_data:
            print(f"Got sunset data: Status = {sunset_data.get('status')}")
            sunset_time = sunset_finder.get_sunset_datetime(sunset_data)
            if sunset_time:
                print(f"Sunset time: {sunset_time}")
                print(f"Sunset time (ISO format): {sunset_time.isoformat()}")
                
                # Check if sunset is in the future
                now = datetime.now(sunset_time.tzinfo)
                time_diff = sunset_time - now
                
                if time_diff.total_seconds() > 0:
                    hours, remainder = divmod(time_diff.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    print(f"Time until sunset: {int(hours)}h {int(minutes)}m {int(seconds)}s")
                    print(f"Formatted: {int(hours):02d}:{int(minutes):02d}")
                else:
                    print("Sunset has already passed for today")
            else:
                print("Failed to get sunset time from data")
        else:
            print("Failed to fetch sunset data")
    
    # Test sunset calculator
    print("\nTesting Sunset Calculator...")
    try:
        calculator = SunsetCalculator()
        calculator.fetch_and_save_sunset()
        
        # Test remaining time
        remaining = calculator.get_remaining_time()
        if remaining:
            print(f"Time remaining: {remaining}")
            hours, remainder = divmod(remaining.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"Formatted time: {int(hours):02d}:{int(minutes):02d}")
        else:
            print("No remaining time found")
            
        formatted = calculator.format_remaining_time()
        print(f"Formatted time from calculator: {formatted}")
        
        # Dump saved data
        print("\nSaved sunset data:")
        for day, sunset in calculator.sunsets.items():
            print(f"Day {day}: {sunset}")
    except Exception as e:
        print(f"Error testing sunset calculator: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nDebug complete")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
