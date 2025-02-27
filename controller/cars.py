from sqlalchemy.orm.session import Session
from schemas.carSchema import CarBase
from models.Cars import DbCar
from fastapi import HTTPException , status
import requests
import datetime

def car_validation(request: CarBase):
     #Check car model by calling api from interent which has all cars models
    response = requests.get("https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json")
    car_models = response.json()
    valid_cars= []
    for i in range(0 , len(car_models.get("Results"))):
         valid_cars.append(car_models.get("Results")[i].get("MakeName"))

    if request.model.upper() not in valid_cars:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f'Model car {request.model} is not a valid model')

    # Check if the year is a 4 digit number within a valid range
    current_year = datetime.datetime.now().year
    if not (1900 <= request.year <= current_year):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"Invalid year {request.year}. Must be between 1900 and the current year.")

    if not (1 <= request.total_seats <= 7):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"Invalid total seats {request.total_seats}. Must be between 1 and 7")
    
#create car
def create_car(db: Session, request: CarBase , user_id: int):

    car_validation(request)

    new_car=DbCar(
        model = request.model,
        year = request.year,
        total_seats = request.total_seats,
        smoking_allowed = request.smoking_allowed,
        wifi_available = request.wifi_available,
        air_conditioning = request.air_conditioning,
        pet_friendly = request.pet_friendly,
        owner_id = user_id
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car

#get all cars that are related to a user
def get_all_user_cars(db: Session, user_id: int):
   cars=  db.query(DbCar).filter(DbCar.owner_id == user_id).all()
   if not cars:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no cars found!')
   return cars

#update car details
def update_user_car(db: Session, user_id: int , car_id: int, request: CarBase):
    car = db.query(DbCar).filter(DbCar.id == car_id, DbCar.owner_id == user_id)
    if not car.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'There is no car with id {car_id}')
    
    car_validation(request)

    car.update({ 
        DbCar.model : request.model,
        DbCar.year : request.year,
        DbCar.total_seats : request.total_seats,
        DbCar.smoking_allowed : request.smoking_allowed,
        DbCar.wifi_available : request.wifi_available,
        DbCar.air_conditioning : request.air_conditioning,
        DbCar.pet_friendly : request.pet_friendly,
        DbCar.owner_id : user_id
        })
    db.commit()
    return 'Your car information has been updated successfully!'

#delete car
def delete_user_car(db: Session, user_id: int, car_id: int):
    car = db.query(DbCar).filter(DbCar.id == car_id, DbCar.owner_id == user_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'There is no car with id {car_id}')
    
    db.delete(car)
    db.commit()
    return 'Your car has been removed successfully!'

#update car availability status
def update_car_availability_status(db: Session, user_id: int , car_id: int, car_status: str):
    car = db.query(DbCar).filter(DbCar.id == car_id, DbCar.owner_id == user_id)
    if not car.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'There is no car with id {car_id}')
    
    car.update({ 
       DbCar.car_availability_status : car_status.lower()
        })
    db.commit()
    return f'Your car availability status has been updated successfully to {car_status}'