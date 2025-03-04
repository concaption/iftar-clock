import os
import json
from datetime import datetime, timedelta
import pytz
from typing import Dict, Optional
from src.location_finder import LocationFinder, Location
from src.sunset_finder import SunsetFinder
from src.logger import logger

class SunsetCalculator:
    def __init__(self):
        logger.info("Initializing SunsetCalculator")
        self.sunset = None
        self.sunsets = {}
        self.data_file = os.path.join(os.path.expanduser('~'), 'iftar_clock.json')
        logger.debug(f"Data file path: {self.data_file}")
        
        self.location_finder = LocationFinder()
        self.sunset_finder = SunsetFinder()
        
        # Load cached sunset data
        self.load_data()
    
    def get_remaining_time(self) -> Optional[timedelta]:
        """Get time remaining until sunset"""
        logger.debug("Getting remaining time until sunset")
        
        # If we have a current sunset time, check if it's still valid
        if self.sunset:
            try:
                # Ensure we have timezone info
                if self.sunset.tzinfo is None:
                    logger.warning("Sunset time has no timezone info, assuming local timezone")
                    local_tz = datetime.now().astimezone().tzinfo
                    self.sunset = self.sunset.replace(tzinfo=local_tz)
                
                now = datetime.now(self.sunset.tzinfo)
                
                # Debug timezone information
                logger.debug(f"Current time: {now}, Sunset time: {self.sunset}")
                logger.debug(f"Current timezone: {now.tzinfo}, Sunset timezone: {self.sunset.tzinfo}")
                
                # Check if sunset is from today
                if self.sunset.date() == now.date():
                    time_diff = self.sunset - now
                    if time_diff.total_seconds() > 0:
                        logger.debug(f"Time remaining until today's sunset: {time_diff}")
                        return time_diff
                    else:
                        logger.debug("Today's sunset has already passed")
                else:
                    # If sunset is not from today, it's either from yesterday or tomorrow
                    if self.sunset.date() < now.date():
                        logger.debug("Sunset time is from a previous day, needs refresh")
                    else:
                        logger.debug("Sunset time is from a future day, checking if it's tomorrow")
                        tomorrow = now + timedelta(days=1)
                        if self.sunset.date() == tomorrow.date():
                            if (now.hour >= 20):  # After 8 PM, start showing tomorrow's time
                                logger.debug("After 8 PM, showing tomorrow's sunset time")
                                time_diff = self.sunset - now
                                logger.debug(f"Time until tomorrow's sunset: {time_diff}")
                                return time_diff
                        
                # If we get here, we need to refresh the sunset time
                logger.debug("Need to refresh sunset data")
                self.fetch_todays_sunset()
                
                # Check again with fresh data
                if self.sunset and self.sunset.date() == now.date():
                    time_diff = self.sunset - now
                    if time_diff.total_seconds() > 0:
                        logger.debug(f"After refresh, time remaining: {time_diff}")
                        return time_diff
            
            except Exception as e:
                logger.error(f"Error calculating remaining time: {e}")
                logger.exception("Detailed error calculating time")
        
        # If we don't have a sunset time or it's not valid, fetch it
        else:
            logger.debug("No sunset time set, fetching it now")
            self.fetch_todays_sunset()
            
            # Try again with the newly fetched sunset time
            if self.sunset:
                now = datetime.now(self.sunset.tzinfo)
                time_diff = self.sunset - now
                if time_diff.total_seconds() > 0:
                    logger.debug(f"After initial fetch, time remaining: {time_diff}")
                    return time_diff
        
        # If all else fails
        logger.warning("Could not determine valid remaining time")
        return None
    
    def fetch_todays_sunset(self):
        """Fetch today's sunset time specifically"""
        logger.info("Fetching today's sunset time")
        # Get location
        location = self.location_finder.get_current_location()
        if location:
            # Get today's sunset data
            today = datetime.now().strftime('%Y-%m-%d')
            logger.debug(f"Requesting sunset for date: {today}")
            
            sunset_data = self.sunset_finder.fetch_sunset(location, date=today)
            if sunset_data:
                sunset_time = self.sunset_finder.get_sunset_datetime(sunset_data)
                if sunset_time:
                    # Save to cache
                    today_key = str(datetime.now().timetuple().tm_yday)
                    self.sunsets[today_key] = sunset_time.isoformat()
                    self.sunset = sunset_time
                    logger.info(f"Updated today's sunset time: {self.sunset}")
                    
                    # Check if we need to show today's time or fetch tomorrow's
                    now = datetime.now(sunset_time.tzinfo)
                    if sunset_time < now:
                        logger.info("Today's sunset has already passed, fetching tomorrow's")
                        
                        # If today's sunset already passed, get tomorrow's
                        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                        tomorrow_data = self.sunset_finder.fetch_sunset(location, date=tomorrow)
                        if tomorrow_data:
                            tomorrow_sunset = self.sunset_finder.get_sunset_datetime(tomorrow_data)
                            if tomorrow_sunset:
                                tomorrow_key = str((datetime.now() + timedelta(days=1)).timetuple().tm_yday)
                                self.sunsets[tomorrow_key] = tomorrow_sunset.isoformat()
                                
                                # Only use tomorrow's time after 8 PM
                                if now.hour >= 20:
                                    self.sunset = tomorrow_sunset
                                    logger.info(f"After 8 PM, using tomorrow's sunset: {self.sunset}")
                                else:
                                    logger.info(f"Stored tomorrow's sunset: {tomorrow_sunset}")
                    
                    self.save_data()
                    return True
        
        logger.error("Failed to fetch today's sunset time")
        return False
    
    def is_sunset_already_got(self) -> bool:
        """Check if we already have sunset data for today"""
        today_key = str(datetime.now().timetuple().tm_yday)  # Day of year
        logger.debug(f"Checking if sunset data exists for day {today_key}")
        
        if today_key in self.sunsets:
            try:
                sunset_str = self.sunsets[today_key]
                logger.debug(f"Found cached sunset time: {sunset_str}")
                
                # Verify the cached time is valid
                try:
                    dt = datetime.fromisoformat(sunset_str)
                    
                    # Ensure dt has timezone info
                    if dt.tzinfo is None:
                        # If no timezone, assume local timezone
                        local_tz = datetime.now().astimezone().tzinfo
                        dt = dt.replace(tzinfo=local_tz)
                        
                    now = datetime.now(dt.tzinfo)
                    
                    # Check if the cached sunset time is for today
                    if dt.date() == now.date():
                        # It's today's sunset
                        self.sunset = dt
                        
                        # If sunset already passed and it's evening, check for tomorrow's sunset
                        if dt < now and now.hour >= 20:
                            tomorrow_key = str((now + timedelta(days=1)).timetuple().tm_yday)
                            if tomorrow_key in self.sunsets:
                                try:
                                    tomorrow_sunset = datetime.fromisoformat(self.sunsets[tomorrow_key])
                                    self.sunset = tomorrow_sunset
                                    logger.info(f"After 8 PM, using cached tomorrow's sunset: {self.sunset}")
                                except Exception as e:
                                    logger.error(f"Error parsing tomorrow's sunset: {e}")
                        else:
                            logger.info(f"Using cached today's sunset: {self.sunset}")
                        
                        return True
                    else:
                        # Cached sunset is not for today, we need a refresh
                        logger.warning("Cached sunset time is not for today")
                        return False
                        
                except Exception as e:
                    logger.error(f"Error parsing cached sunset time: {e}")
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing cached sunset time: {e}")
        
        logger.debug("No valid sunset data for today")
        return False
    
    def fetch_and_save_sunset(self):
        """Fetch sunset time if not already cached"""
        logger.info("Fetching and saving sunset data")
        if not self.is_sunset_already_got():
            # Get today's sunset
            self.fetch_todays_sunset()
        else:
            logger.info("Using cached sunset data")
            
            # Make sure we have the right sunset time
            now = datetime.now()
            if self.sunset and self.sunset.date() != now.date():
                logger.warning("Cached sunset date doesn't match today, refreshing")
                self.fetch_todays_sunset()
    
    def load_data(self):
        """Load cached sunset data from file"""
        logger.debug(f"Loading sunset data from {self.data_file}")
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.sunsets = json.load(f)
                    logger.info(f"Loaded {len(self.sunsets)} sunset records")
                    
                    # Verify and clean up data
                    self._validate_sunset_data()
            else:
                logger.info("No cached data file exists yet")
        except Exception as e:
            logger.exception(f"Error loading sunset data: {e}")
            self.sunsets = {}
    
    def _validate_sunset_data(self):
        """Validate and clean up sunset data"""
        to_remove = []
        for day, sunset_str in self.sunsets.items():
            try:
                dt = datetime.fromisoformat(sunset_str)
                # Keep the data if it's valid
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid sunset time for day {day}: {sunset_str}")
                to_remove.append(day)
        
        # Remove invalid entries
        for day in to_remove:
            del self.sunsets[day]
            
        if to_remove:
            logger.info(f"Removed {len(to_remove)} invalid sunset records")
            self.save_data()
    
    def save_data(self):
        """Save sunset data to file"""
        logger.debug(f"Saving sunset data to {self.data_file}")
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.sunsets, f)
            logger.info(f"Saved {len(self.sunsets)} sunset records")
        except Exception as e:
            logger.exception(f"Error saving sunset data: {e}")
    
    def format_remaining_time(self) -> str:
        """Format remaining time for display"""
        try:
            remaining = self.get_remaining_time()
            if remaining and remaining.total_seconds() > 0:
                hours, remainder = divmod(remaining.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_time = f"{int(hours):02d}:{int(minutes):02d}"
                
                # Add info about whether this is today or tomorrow
                if self.sunset and self.sunset.date() > datetime.now().date():
                    logger.debug("Showing time for tomorrow's sunset")
                    formatted_time = "T " + formatted_time  # Prefix with T for tomorrow
                
                logger.debug(f"Formatted remaining time: {formatted_time}")
                return formatted_time
            else:
                # Force a refresh if time is invalid
                logger.warning("Invalid remaining time, refreshing data")
                self.fetch_todays_sunset()
                
                # Try again after refresh
                remaining = self.get_remaining_time()
                if remaining and remaining.total_seconds() > 0:
                    hours, remainder = divmod(remaining.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    formatted_time = f"{int(hours):02d}:{int(minutes):02d}"
                    
                    # Add info about whether this is today or tomorrow
                    if self.sunset and self.sunset.date() > datetime.now().date():
                        formatted_time = "T " + formatted_time  # Prefix with T for tomorrow
                        
                    logger.debug(f"After refresh, formatted time: {formatted_time}")
                    return formatted_time
                
                logger.error("Failed to get valid time after refresh")
        except Exception as e:
            logger.exception(f"Error formatting remaining time: {e}")
        
        logger.debug("Using placeholder time string")
        return "--:--"
