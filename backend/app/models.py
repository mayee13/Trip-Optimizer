from pydantic import BaseModel
from typing import Optional, List

class TripRequest(BaseModel):
    origin: str
    cities: List[str]
    start_date: str
    end_date: str

class TripResponse(BaseModel):
    order_of_cities: List[str]
    total_cost: float
    day_plan: List[str]