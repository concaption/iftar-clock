import requests
import json
from dataclasses import dataclass

@dataclass
class Location:
    lat: float
    lng: float
    city: str
    country: str

class LocationFinder:
    def __init__(self):
        self.api_url = "https://ipapi.co/json/"
    
    def get_location(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                data = response.json()
                return Location(
                    lat=data.get('latitude'),
                    lng=data.get('longitude'),
                    city=data.get('city', 'Unknown'),
                    country=data.get('country_name', 'Unknown')
                )
            else:
                print(f"Error getting location: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception in get_location: {e}")
            return None
