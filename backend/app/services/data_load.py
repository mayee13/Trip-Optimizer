from ..api.flights import search_flights_day
# from api.trains import search_trains_day
from ..api.distances import get_distance
from ..api.hotels import search_hotels
import pandas as pd
from ..utils.iata_codes import city_to_iata
from ..utils.city_codes import city_to_code
from datetime import timedelta
from ..config import START_DATE, END_DATE
import os
import pandas as pd
import time

# Get path to project root (two levels up from services/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

def normalize_flights_offer(offer):
    if not offer:
        return None
    try:
        seg = offer['itineraries'][0]['segments'][0]
        return {
            "type": "flight",
            "origin": seg["departure"]["iataCode"],
            "destination": seg["arrival"]["iataCode"],
            "departure": seg["departure"]["at"],
            "arrival": seg["arrival"]["at"],
            "carrier": seg.get("carrierCode", offer.get("validatingCarrierCodes", [""])[0]),
            "price": offer["price"]["total"]
        }
    except (KeyError, IndexError):
        return None

def normalize_hotel_offer(offer):
    if not offer:
        return None
    try:
        hotel_info = offer.get("hotel", {})
        hotel_id = hotel_info.get("hotelId", "")
        hotel_name = hotel_info.get("name", "")
        city_code = hotel_info.get("cityCode", "")

        # We'll flatten each individual nightly offer
        offers = []
        for o in offer.get("offers", []):
            check_in = o.get("checkInDate")
            check_out = o.get("checkOutDate")
            price = o.get("price", {})
            total_price = price.get("total", "")
            currency = price.get("currency", "")

            offers.append({
                "type": "hotel",
                "origin": city_code,
                "destination": city_code,
                "departure": check_in,   
                "arrival": check_out,    
                "carrier": hotel_name,  
                "price": total_price,
                "currency": currency,
                "hotelId": hotel_id
            })
        return offers
    except (KeyError, IndexError):
        return None

def load_dist_matrix(cities):
    distances = []
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i == j:
                continue
            dist = get_distance(cities[i], cities[j])
            if dist:
                distances.append(dist)
    df_dist = pd.DataFrame(distances)
    df_dist.to_csv(os.path.join(DATA_DIR, "distances.csv"), index=False)

def load_flight_prices(cities, start_date=START_DATE, end_date=END_DATE):
    flight_prices = []
    current_date = pd.to_datetime(start_date)

    for _ in range((end_date - start_date).days):
        for i in range(len(cities)):
            for j in range(len(cities)):
                if i == j: 
                    continue

                origin = city_to_iata.get(cities[i])
                destination = city_to_iata.get(cities[j])

                if not origin or not destination:
                    print(f"Invalid IATA code for {cities[i]} or {cities[i+1]}")
                    return None
                
                flight_offers = search_flights_day(origin, destination, current_date)
                time.sleep(0.1)  # To respect API rate limits
                for f in flight_offers:
                    norm = normalize_flights_offer(f)
                    if norm:
                        flight_prices.append(norm)

        current_date += timedelta(days=1)

    df_flight = pd.DataFrame(flight_prices)
    df_flight.to_csv(os.path.join(DATA_DIR, "flight_prices.csv"), index=False)

def load_hotel_prices(cities, start_date=START_DATE, end_date=END_DATE):
    hotel_prices = []
    current_date = pd.to_datetime(start_date)

    for _ in range((end_date - start_date).days):
        for city in cities:
            destination = city_to_code.get(city)
            if not destination:
                print(f"Invalid city code for {city}")
                return None

            hotel_offers = search_hotels(destination, current_date, current_date + timedelta(days=1))
            time.sleep(0.1)  # To respect API rate limits
            for h in hotel_offers:
                norms = normalize_hotel_offer(h)
                if norms:
                    hotel_prices.extend(norms)

        current_date += timedelta(days=1)

    df_hotels = pd.DataFrame(hotel_prices)
    df_hotels.to_csv(os.path.join(DATA_DIR, "hotel_prices.csv"), index=False)

# this is an expensive function so it should only be called one trip at a time
def search_trip(cities, start_date=START_DATE, end_date=END_DATE):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    load_dist_matrix(cities)
    load_flight_prices(cities, start_date, end_date)
    # load_hotel_prices(cities, start_date, end_date)
    return {"status": "Data load complete"}