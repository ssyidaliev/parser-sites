from sqlalchemy import Column, String, Text, Integer

from settings.database import Base
from models.base_model import BaseModel


class RealEstate(Base, BaseModel):
    __tablename__ = 'real_estate'

    type_of_sentence = Column(String)
    house_type = Column(String)
    purpose = Column(String)
    series = Column(String)
    floor = Column(String)
    count_room = Column(String)
    square = Column(String)
    square_area = Column(String)
    condition = Column(String)
    appliances = Column(String)
    furniture = Column(String)
    repair = Column(String)
    term = Column(String)
    deposit = Column(String)
    animal = Column(String)
    possibilities = Column(String)
    additionally = Column(Text)
    stone_throw = Column(Text)
