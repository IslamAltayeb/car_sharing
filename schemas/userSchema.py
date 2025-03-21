from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class Booking(BaseModel):
    booking_id: int
    status : str
    class Config():
        orm_mode = True
# Review inside userDisplay
class Review(BaseModel):
    rating: int
    text_description: str
    class Config():
        orm_mode = True

class Trip(BaseModel):
    departure_location: str  
    destination_location: str
    departure_time : datetime
    arrival_time: datetime | None = None
    available_adult_seats: int
    available_children_seats: int
    cost: float
    passengers_count : int | None = None
    status : str
    class Config():
        orm_mode = True

class Car(BaseModel):
    model : str
    year : int
    total_seats : int
    smoking_allowed : bool
    wifi_available : bool
    air_conditioning : bool
    pet_friendly : bool
    car_availability_status: str | None = None
    class Config():
        orm_mode = True

class UserBase(BaseModel): 
    username: str
    email: str
    password: str
    about: str
    phone_number: str
    is_admin: bool = 0

class userDisplay(BaseModel):
    id:int
    user_name: str
    email: EmailStr
    is_admin: bool = 0
    about: str | None = None
    avatar: str | None = None
    phone_number: str | None = None
    left_reviews: List[Review] = []
    received_reviews: List[Review] = []
    cars: List[Car] = []
    trip: List[Trip] = []
    trip_booked: List[Booking] = []
    average_rating: Optional[float] = None  
    reviews_received_count: Optional[int] = None

class UserUpdateResponse(BaseModel): 
    id: int
    user_name: str
    email: EmailStr
    about: Optional[str] = None
    phone_number: Optional[str] = None
    is_admin: bool = False
    avatar: str | None = None

    class Config:
        from_attributes = True



    class Config():
        from_attributes = True
        json_encoders = {"password": lambda v: None}

    

       



