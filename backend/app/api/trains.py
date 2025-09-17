from .client import amadeus
from amadeus import ResponseError

# NOTE: this function does not work
# Search for trains on a specific day
def search_trains_day(origin, dest, date):
    try:
        response = amadeus.rails.offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=date,
            adults=1,
            currencyCode='USD'
        )
        return response.data
    except ResponseError as e:
        print(f"Train search error: {e}")
        return []