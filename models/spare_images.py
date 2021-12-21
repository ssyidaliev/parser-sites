from settings.database import Base
from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, String


class SpareImage(Base):
    __tablename__ = 'spare_images'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    spare_id = Column(Integer, ForeignKey('spare.id'))
    created_at = Column(String)
