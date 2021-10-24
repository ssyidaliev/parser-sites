from sqlalchemy import Column, String

from settings.database import Base
from models.base_model import BaseModel


class Spare(Base, BaseModel):
    brand = Column(String)
    model = Column(String)
    condition = Column(String)
    availability = Column(String)
