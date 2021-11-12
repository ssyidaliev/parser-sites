from settings.database import Base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime


class CommercialImage(Base):
    __tablename__ = 'commercial_images'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    commercial_id = Column(Integer, ForeignKey('commercial.id'))
    created_at = Column(DateTime)
