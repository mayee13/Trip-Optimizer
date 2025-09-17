from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import pandas as pd
import numpy as np
from datetime import timedelta
from .utils.iata_codes import city_to_iata
import os
import pandas as pd
# from services.data_load import search_trip

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # folder where optimizer.py lives
DATA_DIR = os.path.join(BASE_DIR, "data")
df_dist = pd.read_csv(os.path.join(DATA_DIR, "distances.csv"))
df_flight = pd.read_csv(os.path.join(DATA_DIR, "flight_prices.csv"))
# df_hotel = pd.read_csv(os.path.join(DATA_DIR, "hotel_prices.csv"))


# cities is the list of cities, with the origin at the 0 index
# prices is a 2D list of prices between cities, with prices[i][j] being the cost from city i to city j, with the origin at index 0
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

# def price_generator(start_date, cities, trip_length_days):
#     start_dt = pd.to_datetime(start_date)
#     end_dt = start_dt + timedelta(days=trip_length_days)
#     df_trip = df_prices[
#         (pd.to_datetime(df_prices['datetime']) >= start_dt) & 
#         (pd.to_datetime(df_prices['datetime']) <= end_dt) & 
#         (df_prices['origin'].isin(cities)) & 
#         (df_prices['destination'].isin(cities))
#     ]

#     prices = np.zeros((len(cities), len(cities)), dtype=float)

#     for i, origin in enumerate(cities):
#         for j, destination in enumerate(cities):
#             if origin == destination:
#                 prices[i][j] = 0
#             else:
#                 df_leg = df_trip[(df_trip['origin'] == origin) & (df_trip['destination'] == destination)]
#                 if not df_leg.empty:
#                     prices[i][j] = df_leg['price'].mean()
#                 else:
#                     prices[i][j] = float('inf')
#     return prices

def dist_and_dur_matrices(cities):
    distance_matrix = np.zeros((len(cities), len(cities)), dtype=float)
    # duration_matrix = np.zeros((len(cities), len(cities)), dtype=float)
    for i, origin in enumerate(cities):
        for j, destination in enumerate(cities):
            if i == j:
                distance_matrix[i][j] = 0.0
                # duration_matrix[i][j] = 0.0   
            else:
                df_leg = df_dist[(df_dist['origin'] == origin) & (df_dist['destination'] == destination)]
                if not df_leg.empty:
                    distance_matrix[i][j] = int(round(df_leg['distance_km'].values[0]))
                    # duration_matrix[i][j] = df_leg['duration_min'].values[0]
                else:
                    distance_matrix[i][j] = float('inf')  
                    # duration_matrix[i][j] = float('inf')
    return distance_matrix


def optimal_time(start_time_window, end_time_window, cities, origin, nights):
    start_time_window = pd.to_datetime(start_time_window)
    end_time_window = pd.to_datetime(end_time_window)
    df_flight['departure_dt'] = pd.to_datetime(df_flight['departure'])
    # result = search_trip(cities, start_time_window, end_time_window)
    # print(result)
    
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
        
        flight_row_to = df_flight[
            (df_flight['departure_dt'].dt.date == to_date.date()) &
            (df_flight['origin'] == city_to_iata.get(origin)) &
            (df_flight['destination'] == city_to_iata.get(route[1]))
        ]
        if not flight_row_to.empty:
            print(f"Flight found for {origin} to {route[1]} on {to_date.date()} at cost {flight_row_to['price'].min()}")
            curr_cost += flight_row_to['price'].min()
        else:
            print(f"No flight found for {origin} to {route[1]} on {to_date.date()}")
            continue
        
        curr_date = (start_time_window + timedelta(days=i))
        for idx, city in enumerate(route[1:-2], start=1):
            print(f"Visiting city: {city}")
            from_city = city_to_iata.get(city)
            to_city = city_to_iata.get(route[idx+1])
            stay_nights = city_to_index[city]
            to_date = curr_date + timedelta(stay_nights)
            df_leg = df_flight[
                (df_flight['departure_dt'].dt.date == to_date.date()) &
                (df_flight['origin'] == from_city) &
                (df_flight['destination'] == to_city)
            ]
            if not df_leg.empty:
                curr_cost += df_leg['price'].min()
                print(f"Flight found for {city} to {route[idx+1]} on {to_date.date()} at cost {df_leg['price'].min()}")
            else:
                print(f"No flight found for {city} to {route[idx+1]} on {to_date.date()}")
                curr_cost = float('inf')
                break
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
        
        flight_row_back = df_flight[
            (df_flight['departure_dt'].dt.date == back_date.date()) &
            (df_flight['origin'] == city_to_iata.get(route[-2])) &
            (df_flight['destination'] == city_to_iata.get(origin))
        ]
        if not flight_row_back.empty:
            print(f"Flight found for {route[-2]} to {origin} on {back_date.date()} at cost {flight_row_back['price'].min()}")
            curr_cost += flight_row_back['price'].min()
        else:
            print(f"No flight found for {route[-2]} to {origin} on {back_date.date()}")
            continue
        print(f"Current cost for start date {start_date}: {curr_cost}")
        print("-----------------------------------")
        if curr_cost < best_cost:
            best_cost = curr_cost
            best_start_date = start_date
        
    return best_start_date, best_route, best_cost