from .client import amadeus
from amadeus import ResponseError

def search_activities(city_code, radius=10):
    city_response = amadeus.reference_data.locations.get(subType='CITY', keyword=city_code)
    if not city_response.data:
        print(f"City not found for code: {city_code}")
        return []
    
    city = city_response.data[0]
    lat, lon = city['geoCode']['latitude'], city['geoCode']['longitude']

    try:
        response = amadeus.shopping.activities.get(
            latitude=lat,
            longitude=lon,
            radius=radius,
            currencyCode='USD',
        )
        return response.data
    except ResponseError as e:
        print(f"Activity search error: {e}")
        return []
    