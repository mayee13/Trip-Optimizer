from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="city_distance_app", timeout=10)

def get_distance(origin, destination):
    try:
        origin_loc = geolocator.geocode(origin)
        dest_loc = geolocator.geocode(destination)
        
        if not origin_loc or not dest_loc:
            print(f"Could not find coordinates for: {origin} or {destination}")
            return None
        
        distance_km = geodesic(
            (origin_loc.latitude, origin_loc.longitude),
            (dest_loc.latitude, dest_loc.longitude)
        ).km
        print(f"Distance from {origin} to {destination}: {distance_km:.2f} km")
        return {
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km
        }
    except Exception as e:
        print(f"Distance calculation error: {e}")
        return None