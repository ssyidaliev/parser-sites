from settings.database import Base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, String


class RealEstateImage(Base):
    __tablename__ = 'real_estate_images'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    real_estate_id = Column(Integer, ForeignKey('real_estate.id'))
    created_at = Column(String)
