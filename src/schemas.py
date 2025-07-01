from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from fastapi import Depends


class TranscriptRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    query: str = Field(..., description="User query related to the video transcript")
    
    
class UserCredentials(BaseModel):
     email: EmailStr = Field(..., description="User email")
     password: str = Field(..., description="User password")   
     
     
class UserOut(BaseModel):
    id: int
    email: EmailStr
    

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of the token, usually 'bearer'")
    
class TokenData(BaseModel):
    id:Optional[int] = None         
    
class TranscriptOut(BaseModel):
    video_id:str
    video_title:str
    channel_name:str
    
    class Config:
        from_attributes = True
        