import math
import logging

logger = logging.getLogger(__name__)

async def calculate_relative_wind_direction_from_fixed(self, wind_direction=None):
    """
    Converts a 0-360 degree wind direction into a -180 to 180 relative scale.
    0 is the reference point (bow of the ship).
    """
    if wind_direction is None:
        return None
        
    try:
        # Shift scale from 0-360 to -180 to 180
        relative_dir = (wind_direction + 180) % 360 - 180
        
        return {"relative_wind_direction": round(relative_dir, 2)}
    except Exception as e:
        self.logger.error("Error calculating relative wind direction", extra={"reason": str(e)})
        return None

async def calculate_true_wind_speed(self, relative_wind_speed=None, relative_wind_direction=None, platform_speed=None, platform_heading=None):
    """
    Calculates true wind speed using standard Earth-relative U/V vectors.
    """
    # 1. Fail gracefully if pipeline dependencies haven't generated a value yet
    if any(v is None for v in [relative_wind_speed, relative_wind_direction, platform_speed, platform_heading]):
        return None
        
    try:
        # 2. Convert to radians
        head_rad = math.radians(platform_heading)
        awa_rad = math.radians(relative_wind_direction)
        awd_rad = head_rad + awa_rad
        
        # 3. Apparent wind vector (TOWARDS)
        u_aw = -relative_wind_speed * math.sin(awd_rad)
        v_aw = -relative_wind_speed * math.cos(awd_rad)
        
        # 4. Ship vector (TOWARDS)
        u_ship = platform_speed * math.sin(head_rad)
        v_ship = platform_speed * math.cos(head_rad)
        
        # 5. True wind vector (TOWARDS)
        u_tw = u_aw + u_ship
        v_tw = v_aw + v_ship
        
        true_wind_speed = math.sqrt(u_tw**2 + v_tw**2)
        
        return {"true_wind_speed": round(true_wind_speed, 2)}
    except Exception as e:
        self.logger.error("Error calculating true wind speed", extra={"reason": str(e)})
        return None

async def calculate_true_wind_direction(self, relative_wind_speed=None, relative_wind_direction=None, platform_speed=None, platform_heading=None):
    """
    Calculates True Wind Direction (TWD) using standard Earth-relative U/V vectors.
    """
    # 1. Validation: Ensure all Tier 1 inputs are available
    if any(v is None for v in [relative_wind_speed, relative_wind_direction, platform_speed, platform_heading]):
        return None
        
    try:
        # 2. Convert to radians
        head_rad = math.radians(platform_heading)
        awa_rad = math.radians(relative_wind_direction)
        awd_rad = head_rad + awa_rad
        
        # 3. Apparent wind vector (TOWARDS)
        u_aw = -relative_wind_speed * math.sin(awd_rad)
        v_aw = -relative_wind_speed * math.cos(awd_rad)
        
        # 4. Ship vector (TOWARDS)
        u_ship = platform_speed * math.sin(head_rad)
        v_ship = platform_speed * math.cos(head_rad)
        
        # 5. True wind vector (TOWARDS)
        u_tw = u_aw + u_ship
        v_tw = v_aw + v_ship
        
        # 6. True wind direction (FROM)
        twd_rad = math.atan2(-u_tw, -v_tw)
        true_wind_direction = (math.degrees(twd_rad) + 360) % 360
        
        return {"true_wind_direction": round(true_wind_direction, 2)}
    except Exception as e:
        self.logger.error("Error calculating true wind direction", extra={"reason": str(e)})
        return None