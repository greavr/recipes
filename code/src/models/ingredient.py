from sqlalchemy import Column, Integer, String, Text, Float
from .database import Base

class ingredient(Base):
    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    notes = Column(Text)
    quantity = Column(Float)