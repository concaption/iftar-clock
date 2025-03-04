import requests
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, Optional
from src.location_finder import Location
from src.logger import logger

class SunsetFinder:
    def __init__(self):
        self.api_url = "https://api.sunrise-sunset.org/json"
        logger.info("SunsetFinder initialized")
    
    def fetch_sunset(self, location: Location, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches sunset information for the given location
        Args:
            location (Location): Location object with lat and lng attributes
            date (str, optional): Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dict: Dictionary with sunset information or None if failed
        """
        logger.info(f"Fetching sunset data for location: {location.lat}, {location.lng}, date: {date if date else 'today'}")
        try:
            params = {
                "lat": location.lat,
                "lng": location.lng,
                "formatted": 0,  # Return ISO8601 time format
                "date": date if date else "today"
            }
            
            # Add timezone if available
            if location.timezone:
                params["tzid"] = location.timezone
                
            logger.debug(f"Making API request with params: {params}")
            response = requests.get(self.api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Received sunset data: {data}")
                
                # Check if API returned success status
                if data.get("status") == "OK":
                    logger.info("Successfully fetched sunset data")
                    return data
                else:
                    logger.error(f"API error: {data.get('status')}")
                    return None
            else:
                logger.error(f"Error fetching sunset data: {response.status_code}")
                return None
        except Exception as e:
            logger.exception(f"Exception in fetch_sunset: {e}")
            return None
    
    def get_sunset_datetime(self, data: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract sunset time from API response and convert to datetime
        Args:
            data (Dict): API response data
            
        Returns:
            datetime: Sunset time as datetime object or None if failed
        """
        logger.debug("Extracting sunset datetime from API response")
        if data and "results" in data and "sunset" in data["results"]:
            sunset_str = data["results"]["sunset"]
            logger.debug(f"Raw sunset string: {sunset_str}")
            try:
                # Convert to datetime
                dt = datetime.fromisoformat(sunset_str.replace("Z", "+00:00"))
                
                # Check if timezone is specified in the response
                if "tzid" in data:
                    try:
                        # Try to use the timezone from the API response
                        tz = pytz.timezone(data["tzid"])
                        dt = dt.astimezone(tz)
                        logger.debug(f"Using timezone from API: {data['tzid']}")
                    except Exception as e:
                        logger.warning(f"Failed to use timezone from API: {e}")
                        # Fall back to local timezone
                        dt = dt.astimezone(datetime.now().astimezone().tzinfo)
                else:
                    # If no timezone in response, convert to local timezone
                    dt = dt.astimezone(datetime.now().astimezone().tzinfo)
                
                logger.info(f"Sunset time: {dt}")
                return dt
            except ValueError as e:
                logger.error(f"Error parsing sunset time: {e}")
        logger.error("Sunset time not found in response or invalid response format")
        return None
    
    def get_time_until_sunset(self, sunset_time: datetime) -> Optional[timedelta]:
        """
        Calculate time remaining until sunset
        Args:
            sunset_time (datetime): Sunset time
            
        Returns:
            timedelta: Time until sunset or None if sunset has passed
        """
        if sunset_time:
            now = datetime.now(sunset_time.tzinfo)
            time_diff = sunset_time - now
            if time_diff.total_seconds() > 0:
                logger.debug(f"Time until sunset: {time_diff}")
                return time_diff
            else:
                logger.debug("Sunset has already occurred today")
        return None
    
    def format_time_until_sunset(self, time_diff: timedelta) -> str:
        """
        Format time difference for display
        Args:
            time_diff (timedelta): Time difference
            
        Returns:
            str: Formatted time string
        """
        if not time_diff or time_diff.total_seconds() <= 0:
            return "---"
        
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        formatted_time = f"{int(hours):02d}:{int(minutes):02d}"
        logger.debug(f"Formatted time until sunset: {formatted_time}")
        return formatted_time
