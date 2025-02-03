from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    # appid = Column(Integer, unique=True, index=True) # Can maybe be the same as id
    name = Column(String, index=True)

    player_count = Column(Integer, index=True)
    platform = Column(String, index=True)
    developer = Column(String, index=True)

# one for each category in the Steam API to link to the apps
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)

class AppCategory(Base):
    __tablename__ = "app_categories"

    app_id = Column(Integer, ForeignKey("apps.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
