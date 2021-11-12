from sqlalchemy import Column, String
from models.base_model import BaseModel
from settings.database import Base


class Household(Base, BaseModel):
    __tablename__ = 'household'

    condition = Column(String)
    additionally = Column(String)
    delivery = Column(String)
