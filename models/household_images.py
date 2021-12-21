from settings.database import Base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, String


class HouseHoldImage(Base):
    __tablename__ = 'household_images'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    household_id = Column(Integer, ForeignKey('household.id'))
    created_at = Column(String)
