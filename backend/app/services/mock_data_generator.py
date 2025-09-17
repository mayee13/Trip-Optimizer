import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Trips
trips = {
    "Trip1": {
        "cities": ["Seattle", "London", "Paris", "Brussels", "Amsterdam"],
        "nights": [2, 2, 2, 2]  # example values
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

# Generate time window: April 1 – June 15, every 12 hours
start = datetime(2025, 4, 1, 6, 0)
end = datetime(2025, 6, 30, 23, 59)
times = [start + timedelta(hours=12*i) for i in range(int((end-start).days*2))]

data = []
for trip, cities in trips.items():
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                for t in times:
                    base_price = random.randint(100, 800) if "Seattle" not in (cities[i], cities[j]) else random.randint(600, 1200)
                    fluctuation = int(50 * np.sin((t.day + t.hour/24) * np.pi/7))  # weekly-ish wave
                    price = base_price + fluctuation + random.randint(-30, 30)
                    data.append([t.isoformat(), cities[i], cities[j], max(50, price)])

df = pd.DataFrame(data, columns=["datetime","origin","destination","price"])
df.to_csv("data/mock_prices.csv", index=False)
