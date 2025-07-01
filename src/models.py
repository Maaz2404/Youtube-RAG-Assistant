from sqlalchemy import Column, Integer, String, Boolean, DateTime,func,text
from database import Base, engine
import datetime

class Transcript(Base):
    __tablename__ = 'transcripts'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)  # For anonymous users
    user_id = Column(String, nullable=True)      # For logged-in users
    video_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(),nullable=False)
    is_saved = Column(Boolean, server_default=text('false'),nullable=False)
    video_title = Column(String, nullable=False)
    channel_name = Column(String, nullable=False)
    
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
   
    
Base.metadata.create_all(bind=engine)
print("Tables created!")    