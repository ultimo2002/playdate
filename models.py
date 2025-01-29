from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    # appid = Column(Integer, unique=True, index=True) # Can maybe be the same as id
    name = Column(String, index=True)

# one for each category in the Steam API to link to the apps
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class AppDetails(Base):
    __tablename__ = "app_details"

    app_id = Column(Integer, ForeignKey("apps.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
