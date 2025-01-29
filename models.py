from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    # appid = Column(Integer, unique=True, index=True) # Can maybe be the same as id
    name = Column(String, index=True)