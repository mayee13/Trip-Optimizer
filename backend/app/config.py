import os
from dotenv import load_dotenv

load_dotenv()

# Amadeus API credentials
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Travel date window
START_DATE = "2025-10-01"
END_DATE   = "2025-10-15"

# Testing trips
trips = {
    "Trip1": {
        "cities": ["Seattle", "London", "Paris", "Brussels", "Amsterdam"],
        "nights": [2, 2, 2, 2] 
    },
    "Trip2": {
        "cities": ["Seattle", "Milan", "Venice", "Florence", "Rome", "Athens", "Santorini"],
        "nights": [2, 2, 2, 2, 2, 2]
    },
    "Trip3": {
        "cities": ["Seattle", "Berlin", "Prague", "Budapest", "Vienna", "Zurich"],
        "nights": [2, 2, 2, 2, 2]
    },
    "Trip4": {
        "cities": ["Seattle", "Madrid", "Barcelona", "Seville", "Lisbon"],
        "nights": [2, 2, 2, 2]
    },
}