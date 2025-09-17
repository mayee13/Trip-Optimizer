from .client import amadeus
from amadeus import ResponseError

# NOTE: This function does not work, may need to switch to another API. 
def search_hotels(city_code, check_in_date, check_out_date):
    check_in_date = check_in_date.strftime("%Y-%m-%d")
    check_out_date = check_out_date.strftime("%Y-%m-%d")
    try:
        response = amadeus.shopping.hotel_offers_search.get(
            cityCode=city_code,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=1,
            # roomQuantity=1,
        )
        print(f"Received hotel response for {city_code} on {check_in_date}->{check_out_date}")
        return response.data
    except ResponseError as e:
        print(f"Hotel search error for {city_code} on {check_in_date}->{check_out_date}: {e}")
        return []