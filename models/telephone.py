from sqlalchemy import Column, String
from models.base_model import BaseModel
from settings.database import Base


class Telephone(Base, BaseModel):
    __tablename__ = 'telephone'

    model = Column(String)
    condition = Column(String)
    memory = Column(String)
    ram = Column(String)
    color = Column(String)
    additionally = Column(String)
    delivery = Column(String)
