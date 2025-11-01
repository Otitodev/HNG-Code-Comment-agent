from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from .db import Base

class DailyTip(Base):
    __tablename__ = "daily_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    tip = Column(String, nullable=False)
    language = Column(String, nullable=True)  # Programming language for the tip

class CodeRequest(Base):
    __tablename__ = "code_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # IP or session ID
    code_snippet = Column(Text, nullable=False)
    detected_language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserLanguagePreference(Base):
    __tablename__ = "user_language_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    primary_language = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
