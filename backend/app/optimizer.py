from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import pandas as pd
import numpy as np
from datetime import timedelta
from .utils.iata_codes import city_to_iata
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
DATA_DIR = os.path.join(BASE_DIR, "data")
df_dist = pd.read_csv(os.path.join(DATA_DIR, "distances.csv"))
df_flight = pd.read_csv(os.path.join(DATA_DIR, "flight_prices.csv"))
# df_hotel = pd.read_csv(os.path.join(DATA_DIR, "hotel_prices.csv"))

"""
cities is the list of cities, with the origin at the 0 index, prices is a 2D list of prices 
between cities, with prices[i][j] being the cost from city i to city j, with the origin at index 0
"""
def city_order_finder(cities, prices, origin):
    manager = pywrapcp.RoutingIndexManager(len(cities), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(prices[from_node][to_node])
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH) 
    search_parameters.time_limit.FromSeconds(30)
    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return None, None
    
    index = routing.Start(0)
    route = [origin]
    total_cost = 0
    while not routing.IsEnd(index):
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        node_index = manager.IndexToNode(index)
        if not routing.IsEnd(index):
            route.append(cities[node_index])
        total_cost += routing.GetArcCostForVehicle(previous_index, index, 0)
    route.append(origin)
    return route, total_cost

def dist_and_dur_matrices(cities):
    distance_matrix = np.zeros((len(cities), len(cities)), dtype=float)
    for i, origin in enumerate(cities):
        for j, destination in enumerate(cities):
            if i == j:
                distance_matrix[i][j] = 0.0
            else:
                df_leg = df_dist[(df_dist['origin'] == origin) & (df_dist['destination'] == destination)]
                if not df_leg.empty:
                    distance_matrix[i][j] = int(round(df_leg['distance_km'].values[0]))
                else:
                    distance_matrix[i][j] = float('inf')  
    return distance_matrix


def search_flight_df(origin, destination, date, df):
    date = pd.to_datetime(date)
    flight_row = df[
        (df['departure_dt'].dt.date == date.date()) &
        (df['origin'] == city_to_iata.get(origin)) &
        (df['destination'] == city_to_iata.get(destination))
    ]
    if not flight_row.empty:
        min_cost = flight_row['price'].min()
        print(f"Flight found from {origin} to {destination} on {date.date()} at cost {min_cost}")
        return min_cost
    return None

def optimal_time(start_time_window, end_time_window, cities, origin, nights):
    start_time_window = pd.to_datetime(start_time_window)
    end_time_window = pd.to_datetime(end_time_window)
    df_flight['departure_dt'] = pd.to_datetime(df_flight['departure'])
    
    best_cost = float('inf')
    best_start_date = None
    best_route = None
    
    print("Calculating distance matrix...")
    dist_matrix = dist_and_dur_matrices(cities)
    print("Finding optimal city order...")
    route, total_distance = city_order_finder(cities, dist_matrix, origin)
    print("Optimal route found:", route)
    
    city_to_index = {city: n for city, n in zip(cities, nights)}
    trip_length = sum(nights)
    best_route = route
    for i in range((end_time_window - start_time_window).days - trip_length):
        print(f"Evaluating start date: {(start_time_window + timedelta(days=i)).strftime('%Y-%m-%d')}")
        curr_cost = 0
        start_date = (start_time_window + timedelta(days=i))
        to_date = start_date 
        back_date = start_date + timedelta(trip_length)
    
        to_cost = search_flight_df(origin, route[1], to_date, df_flight)
        curr_cost += to_cost if to_cost is not None else float('inf')

        curr_date = (start_time_window + timedelta(days=i))
        for idx, city in enumerate(route[1:-2], start=1):
            print(f"Visiting city: {city}")
            stay_nights = city_to_index[city]
            to_date = curr_date + timedelta(stay_nights)

            leg_cost = search_flight_df(city, route[idx+1], to_date, df_flight)
            curr_cost += leg_cost if leg_cost is not None else float('inf')
            curr_date = to_date
            
            # for night in range(stay_nights):
            #     curr_date = start_date + timedelta(days=night)
            #     hotel_row = df_hotel[
            #         (pd.to_datetime(df_hotel['date']) == str(curr_date)) & 
            #         (df_hotel['city'] == city_to_iata(cities[i]))
            #     ]
            #     if not hotel_row.empty:
            #         curr_cost += hotel_row['price'].min()
            #     else:
            #         return None
        
        back_cost = search_flight_df(route[-2], origin, back_date, df_flight)
        curr_cost += back_cost if back_cost is not None else float('inf')

        print(f"Current cost for start date {start_date}: {round(curr_cost, 2)}")
        print("-----------------------------------")
        if curr_cost < best_cost:
            best_cost = curr_cost
            best_start_date = start_date
        
    return best_start_date, best_route, best_cost