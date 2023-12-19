from models import Startup

def center_coordinates(startups: list[Startup])->(float,float):
    # Find optimum lat and lon
    lats = [s.latitude for s in startups]
    lons = [s.longitude for s in startups]
    avg_lat = sum(lats)/len(lats)
    # Adjust for marker icon height
    adjusted_lat = avg_lat + (avg_lat * .002)
    avg_lon = sum(lons)/len(lons)
    default_lat = adjusted_lat
    default_lon = avg_lon
    
    return default_lat, default_lon