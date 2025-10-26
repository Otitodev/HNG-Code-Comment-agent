from datetime import date
from sqlalchemy import Column, Integer, String, Date
from .db import Base

class DailyTip(Base):
    __tablename__ = "daily_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    tip = Column(String, nullable=False)
