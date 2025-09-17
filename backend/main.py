import sys
# from fastapi import FastAPI
from app.config import trips, START_DATE, END_DATE
from app.services.data_load import search_trip

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "Trip Optimizer Backend is running"}

# @app.get("/search_trip/{trip_name}")
# def run_search_trip(trip_name: str):
#     if trip_name not in trips:
#         return {"error": f"Trip '{trip_name}' not found in config"}
#     cities = trips[trip_name]
#     result = search_trip(cities, START_DATE, END_DATE)
#     return {"message": f"Completed {trip_name}", "details": result}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <TripName>")
        print(f"Available trips: {list(trips.keys())}")
        sys.exit(1)

    trip_name = sys.argv[1]
    if trip_name not in trips:
        print(f"Error: Trip '{trip_name}' not found in config")
        print(f"Available trips: {list(trips.keys())}")
        sys.exit(1)

    cities = trips[trip_name]["cities"]
    nights = trips[trip_name]["nights"]

    # Uncomment this block to load data
    # print(f"Running {trip_name}...")
    # result = search_trip(cities, START_DATE, END_DATE)
    # print(result)

    # This block actually calculates the optimal trip start date and route
    from app.optimizer import optimal_time
    print("Calculating optimal time and route...")
    best_start_date, best_route, best_cost = optimal_time(START_DATE, END_DATE, cities, cities[0], nights)
    print(f"Optimal start date: {best_start_date}, route: {best_route}, cost: {best_cost}")
