from amadeus import Client
from ..config import AMADEUS_API_KEY, AMADEUS_API_SECRET, GOOGLE_MAPS_API_KEY
import googlemaps

amadeus = Client(
    client_id=AMADEUS_API_KEY,
    client_secret=AMADEUS_API_SECRET,
    hostname="production"
)

google_maps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)