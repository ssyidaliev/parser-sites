from sqlalchemy import Column, DateTime, Integer, String
from settings.database import Base


class LoggingRecord(Base):
    __tablename__ = 'logging_record'

    id = Column(Integer, primary_key=True, unique=True)
    log = Column(String)
    log_name = Column(String)
    log_status = Column(String)
    created_at = Column(DateTime)
