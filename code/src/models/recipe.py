from sqlalchemy import Column, Integer, String, ARRAY, JSON, Boolean, Text, DateTime
import models as ingredient
from .database import Base

class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, index=True)
    Title = Column(String, index=True)
    description = Column(Text)
    time = Column(String)
    Category = Column(String)
    Yield = Column(String)
    Source = Column(JSON)
    Active = Column(Boolean, default=True)
    Directions = Column(ARRAY(String))
    Ingredients = Column(ARRAY(ingredient))
    CreatedDate = Column(DateTime)