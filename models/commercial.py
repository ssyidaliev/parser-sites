from sqlalchemy import Column, String, Text

from settings.database import Base
from models.base_model import BaseModel


class Commercial(Base, BaseModel):
    brand = Column(String)
    model = Column(String)
    year_of_issue = Column(String)
    condition = Column(String)
    mileage = Column(String)
    color = Column(String)
    engine = Column(String)
    transmission_type = Column(String)
    drive_unit = Column(String)
    steerin_wheel = Column(String)
    customs = Column(String)
    availability = Column(String)
    exchange = Column(String)
    other = Column(Text)