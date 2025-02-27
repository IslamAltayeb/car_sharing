
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime , func , Float
from enum import Enum
from sqlalchemy.orm import relationship
from config.db_connect import Base
import datetime
class DbTrip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    car_id = Column(Integer, ForeignKey('cars.id', ondelete="CASCADE"))
    departure_location= Column(String)  
    destination_location= Column(String)
    departure_time = Column(DateTime) 
    arrival_time = Column(DateTime, nullable=True)
    duration = Column(Float)
    available_adult_seats = Column(Integer)
    available_children_seats = Column(Integer)
    cost = Column(Float)
    passengers_count = Column(Integer, default=0)
    status = Column(String, default="scheduled") # scheduled, ongoing, completed, or cancelled
    created_at = Column(String, default=func.now()) 
    updated_at = Column(String, nullable=True)

    user = relationship("DbUser", back_populates="trip")
    car = relationship("DbCar", back_populates="trip")
    trip_booked = relationship("DbBooking", back_populates="trip")