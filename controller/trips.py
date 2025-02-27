from models.Trips import DbTrip
from models.Cars import DbCar
from sqlalchemy.orm.session import Session
from schemas.tripSchema import TripBase
from fastapi import HTTPException , status
import datetime
from sqlalchemy import  func 
from controller import cars

def trip_duration(departure_time: datetime, arrival_time: datetime):
    duration = arrival_time - departure_time
    duration_per_hours = duration.total_seconds() / 3600
    return round(duration_per_hours,2)

def trip_vaildation(db: Session, request: TripBase, car_id: int):
    #check the departure and arrival time
    if request.departure_time >= request.arrival_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= 'The arrival time should be after the departure time')
    
    #check the available seats if positive
    if request.available_adult_seats < 0 or request.available_children_seats < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= 'The number of the available seats should be a positive number')
    
    #check if the sum of adult seats and children seats is more than the car total seats
    car = db.query(DbCar).filter(DbCar.id == car_id).first()
    if (request.available_adult_seats + request.available_children_seats > car.total_seats):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= 'The number of adults seats and children seats should not be more the the total seats in your car')

    #check if the cost is positive
    if request.cost < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= 'The cost should be a positive number')
    

def create_trip(db: Session, request: TripBase, creator_id: int, car_id: int):
    
    #check if the user have the car that he wants to create a trip using it
    car = db.query(DbCar).filter(DbCar.id == car_id, DbCar.owner_id == creator_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'You do not have a car with car id {car_id}')

    #check the availability of the car
    if car.car_availability_status != "available":
       raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail= f'You can not add a trip with car id {car_id}, because the status of this car is not available. Turn it to available then try again.')
    
    trip_vaildation(db, request, car_id)

    #check if the user have a trip before with the same car and during the same time
    trip = db.query(DbTrip).filter(DbTrip.creator_id == creator_id, DbTrip.car_id == car_id, DbTrip.departure_time<=request.departure_time, DbTrip.arrival_time>=request.departure_time).first()
    if trip:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail= f'You can not add a trip with car id {car_id}, because you already have a trip that its id is {trip.id} with the same car during this time.')


    trip = DbTrip(
        creator_id = creator_id,
        car_id = car_id,
        departure_location = request.departure_location.lower(),
        destination_location = request.destination_location.lower(),
        departure_time = request.departure_time,
        arrival_time = request.arrival_time,
        available_adult_seats = request.available_adult_seats,
        available_children_seats = request.available_children_seats,
        cost = request.cost,
        duration = trip_duration(request.departure_time, request.arrival_time)
        )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

#update trip details
def update_trip(db: Session,request: TripBase, creator_id: int , trip_id: int):
    trip = db.query(DbTrip).filter(DbTrip.creator_id == creator_id, DbTrip.id == trip_id)
    if not trip.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'There is no trip with id {trip_id}')
    
    trip_vaildation(db, request, trip.first().car_id)

    #check if the user have a trip before with the same car and during the same time
    pervious_trip = db.query(DbTrip).filter(DbTrip.creator_id == creator_id, DbTrip.car_id == trip.first().car_id, DbTrip.id != trip_id, DbTrip.departure_time<=request.departure_time, DbTrip.arrival_time>=request.departure_time).first()
    if pervious_trip:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail= f'You can not update your trip with this time, because you already have a trip that its id is {pervious_trip.id} with the same car during this time.')


    trip.update({ 
        DbTrip.departure_location : request.departure_location.lower(),
        DbTrip.destination_location : request.destination_location.lower(),
        DbTrip.departure_time : request.departure_time,
        DbTrip.arrival_time : request.arrival_time,
        DbTrip.available_adult_seats : request.available_adult_seats,
        DbTrip.available_children_seats : request.available_children_seats,
        DbTrip.cost: request.cost,
        DbTrip.updated_at : func.now(),
        DbTrip.duration: trip_duration(request.departure_time, request.arrival_time)
        })
    db.commit()
    return 'Your trip details has been updated successfully!'

#delete trip
def delete_trip(db: Session, user_id: int, trip_id: int):
    trip = db.query(DbTrip).filter(DbTrip.id == trip_id, DbTrip.creator_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'There is no trip with id {trip_id}')
    
    db.delete(trip)
    db.commit()
    return 'Your trip has been removed successfully!'

#get all trips that are related to a user
def get_all_user_trips(db: Session, user_id: int):
   trips=  db.query(DbTrip).filter(DbTrip.creator_id == user_id).all()
   if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no trips found!')
   return trips

#search for trip
def search_trip(db: Session, departure_location: str, destination_location: str,
                departure_time: datetime, available_adult_seats: int, available_children_seats: int):
    trips=  db.query(DbTrip).filter(DbTrip.departure_location== departure_location.lower(),
                                    DbTrip.destination_location == destination_location.lower(),
                                    DbTrip.departure_time >= departure_time,
                                    DbTrip.available_adult_seats >= available_adult_seats,
                                    DbTrip.available_children_seats >= available_children_seats).all()
    if not trips:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There are no trips match your request!')
    return trips

#update trip status
def update_trip_status(db: Session, user_id: int , trip_id: int, trip_status: str):
    trip = db.query(DbTrip).filter(DbTrip.id == trip_id, DbTrip.creator_id == user_id)
    if not trip.first():
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f'There is no trip with id {trip_id}')
    
    trip.update({ 
       DbTrip.status : trip_status.lower()
       })
    car_id = trip.first().car_id

    car_status = ""
    if trip_status == "Ongoing":
        car_status = "in use"
        cars.update_car_availability_status(db, user_id, car_id , car_status)

    elif trip_status == "Cancelled" or trip_status == "Scheduled" or trip_status == "Completed":
        car_status = "available"
        cars.update_car_availability_status(db, user_id, car_id , car_status)
    db.commit()
    return f'Your trip status has been updated to {trip_status} and your car availability status has been updated to {car_status}'
    