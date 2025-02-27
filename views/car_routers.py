from fastapi import APIRouter , Depends
from schemas.carSchema import CarBase , CarDisplay
from sqlalchemy.orm import Session
from config.db_connect import get_db
from controller import cars
from typing import List
from enum import Enum

router = APIRouter(
prefix='/Cars',
tags=['Cars']
)

class car_availability(str, Enum):
    available = "Available"
    unavailable = "Unavailable"

#create car for a user
@router.post('/create/{user_id}', response_model=CarDisplay)
def create_car(request: CarBase ,user_id: int, db: Session=Depends(get_db)):
    return cars.create_car(db, request, user_id)

#get all cars that are related to a user
@router.get('/get/{user_id}', response_model=List[CarDisplay])
def get_all_user_cars(user_id: int, db: Session=Depends(get_db)):
    return cars.get_all_user_cars(db, user_id)

#update car that is related to a user
@router.put('/update/{user_id}/{car_id}')
def update_user_car(request: CarBase, user_id: int, car_id: int, db: Session=Depends(get_db)):
    return cars.update_user_car(db, user_id, car_id, request)


#update car availability status
@router.put('/update_availability/{user_id}/{car_id}')
def update_car_availability_status(user_id: int, car_id: int, status: car_availability,db: Session=Depends(get_db)):
    return cars.update_car_availability_status(db, user_id, car_id, status.value)

#delete car that is related to a user
@router.delete('/delete/{user_id}/{car_id}')
def delete_user_car(user_id: int, car_id: int, db: Session=Depends(get_db)):
    return cars.delete_user_car(db, user_id, car_id)