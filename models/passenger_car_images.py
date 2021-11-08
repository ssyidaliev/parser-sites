from settings.database import Base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime


class PassengerCarImage(Base):
    __tablename__ = 'passenger_car_images'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    passenger_car_id = Column(Integer, ForeignKey('passenger_car.id'))
    created_at = Column(DateTime)
