from sqlalchemy import Column, String, Text, LargeBinary, DateTime, Integer, ForeignKey
from settings.database import Base
from models.base_model import BaseModel


class PassengerCar(Base, BaseModel):
    __tablename__ = 'passenger_car'

    brand = Column(String)
    model = Column(String)
    year_of_issue = Column(String)
    body_type = Column(String)
    mileage = Column(String)
    color = Column(String)
    engine = Column(String)
    transmission_type = Column(String)
    drive_unit = Column(String)
    steering_wheel = Column(String)
    condition = Column(String)
    customs = Column(String)
    availability = Column(String)
    exchange = Column(String)
    other = Column(Text)
