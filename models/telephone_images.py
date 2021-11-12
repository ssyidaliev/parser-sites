from settings.database import Base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime


class TelephoneImage(Base):
    __tablename__ = 'telephone_images'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    telephone_id = Column(Integer, ForeignKey('telephone.id'))
    created_at = Column(DateTime)
