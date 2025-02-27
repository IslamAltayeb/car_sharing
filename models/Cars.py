from config.db_connect import Base
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from models.Users import DbUser


class DbCar(Base):
    __tablename__ ='cars'
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    model = Column(String)
    year = Column(Integer)
    total_seats = Column(Integer)
    smoking_allowed = Column(Boolean)
    wifi_available = Column(Boolean)
    air_conditioning = Column(Boolean)
    pet_friendly = Column(Boolean)
    car_status = Column(String, default="pending") # Pending , approved , rejected by admin
    car_availability_status = Column(String , default="available")  # available , booked , in use , unavailable
    user = relationship("DbUser", back_populates='cars')
    trip = relationship("DbTrip", back_populates="car")
