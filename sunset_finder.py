import requests
from src.location_finder import Location

class SunsetFinder:
    def __init__(self):
        self.api_url = "https://api.sunrise-sunset.org/json"
    
    def fetch_sunset(self, location: Location):
        """
        Fetches sunset information for the given location
        Returns: Dictionary with sunset information or None if failed
        """
        try:
            params = {
                "lat": location.lat,
                "lng": location.lng,
                "formatted": 0  # Return ISO8601 time format
            }
            
            response = requests.get(self.api_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching sunset data: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception in fetch_sunset: {e}")
            return None
