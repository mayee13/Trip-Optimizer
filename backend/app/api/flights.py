from .client import amadeus
from amadeus import ResponseError

def search_flights_day(origin, dest, date):
    date = date.strftime("%Y-%m-%d")
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=date,
            adults=1,
            currencyCode='USD'
        )
        print(f"Received response for {origin}->{dest} on {date}")
        return response.data
    except ResponseError as e:
        print(f"Flight search error {origin}->{dest} on {date}: {e}")
        return []

def search_flights_days_range(origin, dest, start_date, end_date):
    try:
        response = amadeus.shopping.flight_dates.get(
            origin=origin,
            destination=dest,
            departureDate=f"{start_date},{end_date}",
            adults=1,
            currency="USD"
        )
        return response.data
    except ResponseError as e:
        print(f"Flight search error: {e}")
        return []