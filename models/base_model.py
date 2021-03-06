from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime


class BaseModel:
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    title = Column(String)
    price = Column(String)
    phone_number = Column(String)
    city_of_sale = Column(String)
    description = Column(Text)
    country = Column(String, default='KG')
    is_read = Column(Boolean, default=False)
    created_at = Column(String)
    updated_at = Column(String)
