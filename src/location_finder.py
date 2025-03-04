import requests
from dataclasses import dataclass
from typing import Optional, Tuple
from src.logger import logger

@dataclass
class Location:
    lat: float
    lng: float
    city: str = "Unknown"
    country: str = "Unknown"
    timezone: str = ""
    
    @classmethod
    def from_lat_lng_string(cls, lat_lng: str):
        """Create Location from a 'lat,lng' formatted string"""
        logger.debug(f"Creating Location from lat_lng string: {lat_lng}")
        if lat_lng and "," in lat_lng:
            parts = lat_lng.split(",")
            if len(parts) == 2:
                try:
                    location = cls(
                        lat=float(parts[0].strip()), 
                        lng=float(parts[1].strip()),
                        city="", 
                        country=""
                    )
                    logger.debug(f"Created Location: lat={location.lat}, lng={location.lng}")
                    return location
                except ValueError as e:
                    logger.error(f"Error parsing lat_lng string: {e}")
        logger.error(f"Invalid lat_lng string format: {lat_lng}")
        return None

class LocationFinder:
    def __init__(self):
        self.api_url = "https://ipapi.co"
        logger.info("LocationFinder initialized")
    
    def get_lat_lng(self) -> Optional[str]:
        """
        Get latitude,longitude string from the API
        Returns: String in format "lat,lng" or None if failed
        """
        logger.debug("Fetching lat/lng from API")
        try:
            logger.debug(f"Making request to {self.api_url}/latlong")
            response = requests.get(f"{self.api_url}/latlong")
            if response.status_code == 200:
                result = response.text.strip()
                logger.info(f"Successfully got lat/lng: {result}")
                return result
            else:
                logger.error(f"Error getting lat/lng: {response.status_code}")
                return None
        except Exception as e:
            logger.exception(f"Exception in get_lat_lng: {e}")
            return None
    
    def get_current_location(self) -> Optional[Location]:
        """
        Get full location information for current IP
        Returns: Location object or None if failed
        """
        logger.info("Getting current location")
        # First try to get lat,lng
        lat_lng = self.get_lat_lng()
        if lat_lng:
            # Then get full location information
            try:
                logger.debug(f"Making request to {self.api_url}/json/")
                response = requests.get(f"{self.api_url}/json/")
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Received location data: {data}")
                    location = Location(
                        lat=float(data.get('latitude', 0)),
                        lng=float(data.get('longitude', 0)),
                        city=data.get('city', 'Unknown'),
                        country=data.get('country_name', 'Unknown'),
                        timezone=data.get('timezone', '')
                    )
                    logger.info(f"Location found: {location.city}, {location.country} ({location.lat}, {location.lng})")
                    return location
                else:
                    logger.warning(f"Error response from API: {response.status_code}")
                    # Fallback to just creating a location from the lat,lng
                    logger.info("Falling back to lat/lng only location")
                    return Location.from_lat_lng_string(lat_lng)
            except Exception as e:
                logger.exception(f"Exception in get_current_location: {e}")
                # Fallback to just creating a location from the lat,lng
                logger.info("Falling back to lat/lng only location due to exception")
                return Location.from_lat_lng_string(lat_lng)
        logger.error("Failed to get location")
        return None
