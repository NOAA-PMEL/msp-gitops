# sampling-system/calculations/default.py
import logging
import numpy as np

logger = logging.getLogger(__name__)

async def calculate_true_wind_speed(self, relative_wind_speed=None, relative_wind_direction=None, platform_speed=None, platform_heading=None):
    """
    Calculates true wind speed based on apparent (relative) wind and platform vectors.
    Fully vectorized to support both streaming (scalars) and batch (arrays) processing.
    """
    # 1. Fail gracefully if pipeline dependencies haven't generated a value yet
    if any(v is None for v in [relative_wind_speed, relative_wind_direction, platform_speed, platform_heading]):
        return None
        
    try:
        # 2. Convert to numpy arrays, even if they are single scalars
        # np.atleast_1d ensures a single float 14.2 becomes array([14.2])
        rel_ws = np.atleast_1d(relative_wind_speed)
        rel_wd = np.atleast_1d(relative_wind_direction)
        p_speed = np.atleast_1d(platform_speed)
        p_heading = np.atleast_1d(platform_heading)

        # Note: If your platform_speed (SOG) is in km/h, convert it to m/s here:
        # p_speed_ms = p_speed / 3.6
        p_speed_ms = p_speed

        # 3. Convert apparent wind angle to radians 
        rel_wd_rad = np.radians(rel_wd)
        
        # 4. Calculate True Wind Speed using the Law of Cosines
        # TWS^2 = AWS^2 + SOG^2 - 2 * AWS * SOG * cos(Apparent Wind Angle)
        tws_squared = (rel_ws ** 2) + (p_speed_ms ** 2) - (2 * rel_ws * p_speed_ms * np.cos(rel_wd_rad))
        
        # 5. Use np.maximum(0, ...) to protect against negative zero floating point math errors
        tws_squared = np.maximum(0, tws_squared)
        true_wind_speed = np.sqrt(tws_squared)
        
        # 6. Round results for clean telemetry
        true_wind_speed = np.round(true_wind_speed, 2)
        
        # 7. Dynamically format the return type based on the input type
        if len(true_wind_speed) == 1 and not isinstance(relative_wind_speed, list):
            # Streaming context (return a pure python float)
            final_val = float(true_wind_speed[0])
        else:
            # Batch context (return a standard Python list of floats for JSON serialization)
            final_val = true_wind_speed.tolist()

        return {"true_wind_speed": final_val}
        
    except Exception as e:
        # self.logger is available because we pass 'self' from the sampling-system engine
        self.logger.error("Error calculating true wind speed", extra={"reason": str(e)})
        return None
    
async def calculate_true_wind_direction(self, relative_wind_speed=None, relative_wind_direction=None, platform_speed=None, platform_heading=None):
    """
    Calculates True Wind Direction (TWD) using vector subtraction of the 
    platform's motion from the apparent wind vector.
    """
    # 1. Validation: Ensure all Tier 1 inputs are available
    if any(v is None for v in [relative_wind_speed, relative_wind_direction, platform_speed, platform_heading]):
        return None
        
    try:
        # Convert to numpy arrays
        rel_ws = np.atleast_1d(relative_wind_speed)
        rel_wd = np.atleast_1d(relative_wind_direction)
        p_speed = np.atleast_1d(platform_speed)
        p_heading = np.atleast_1d(platform_heading)
        
        # 2. Unit Consistency: Convert Platform Speed (km/h) to m/s to match wind speed
        # Based on your platform_varmaps.json, platform_speed is in km/h.
        p_speed_ms = p_speed / 3.6 

        # 3. Trigonometric conversion (Apparent Wind Angle relative to Bow)
        rel_wd_rad = np.radians(rel_wd)
        
        # 4. Resolve True Wind components relative to the platform bow
        # True_X = Apparent_X - Platform_X (Platform_X relative to bow is 0)
        # True_Y = Apparent_Y - Platform_Y (Platform_Y relative to bow is SOG)
        tw_x = rel_ws * np.sin(rel_wd_rad)
        tw_y = (rel_ws * np.cos(rel_wd_rad)) - p_speed_ms
        
        # 5. Calculate True Wind Heading (angle relative to bow) using arctan2
        tw_heading_rel_bow = np.degrees(np.arctan2(tw_x, tw_y))
        
        # 6. Adjust for Platform Heading to get True Wind Direction relative to North
        # TWD = (Heading + Angle_Rel_Bow) mod 360
        true_wind_direction = (p_heading + tw_heading_rel_bow) % 360
        
        true_wind_direction = np.round(true_wind_direction, 2)
        
        # 7. Dynamically format the return type
        if len(true_wind_direction) == 1 and not isinstance(relative_wind_direction, list):
            final_val = float(true_wind_direction[0])
        else:
            final_val = true_wind_direction.tolist()
            
        return {"true_wind_direction": final_val}
        
    except Exception as e:
        self.logger.error("Error calculating true wind direction", extra={"reason": str(e)})
        return None