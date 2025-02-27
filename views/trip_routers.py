from schemas.tripSchema import TripBase, TripDisplay
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db_connect import get_db
from controller import trips
from typing import List
from datetime import datetime
from enum import Enum

router = APIRouter(
    prefix="/trips",
    tags=['trips']
)

class trip_status(str, Enum):
    scheduled = "Scheduled"
    ongoing = "Ongoing"
    completed = "Completed"
    cancelled = "Cancelled"

#create a trip
@router.post('/create_trip/{user_id}/{car_id}',  response_model=TripDisplay)
def create_trip( req:TripBase,user_id: int, car_id: int, db: Session= Depends(get_db)):
    return trips.create_trip(db, req, user_id, car_id)

#update a trip
@router.put('/update_trip/{user_id}/{trip_id}')
def update_trip( req:TripBase,user_id: int, trip_id: int, db: Session= Depends(get_db)):
    return trips.update_trip(db, req, user_id, trip_id)

#get all trips that are related to a user
@router.get('/get_all_trips/{user_id}', response_model=List[TripDisplay])
def get_all_user_trips(user_id: int, db: Session=Depends(get_db)):
    return trips.get_all_user_trips(db, user_id)

#search trip
@router.get('/search_trip/', response_model=List[TripDisplay])
def searsh_trip(departure_location: str, destination_location: str, departure_time: datetime,
                 available_adult_seats: int, available_children_seats: int  , db: Session=Depends(get_db)):
    return trips.search_trip(db, departure_location, destination_location, departure_time, available_adult_seats, available_children_seats)

#update_trip_status
@router.put('/update_status/{user_id}/{trip_id}')
def update_trip_status(user_id: int, trip_id: int, status: trip_status, db: Session=Depends(get_db)):
    return trips.update_trip_status(db, user_id, trip_id, status.value)

#delete trip
@router.delete('/delete_trip/{user_id}/{trip_id}')
def delete_trip(user_id: int, trip_id: int, db: Session=Depends(get_db)):
    return trips.delete_trip(db, user_id, trip_id)