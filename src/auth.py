from fastapi import Depends, HTTPException, status,APIRouter
from database import get_db
from sqlalchemy.orm import Session
from schemas import UserCredentials,UserOut
from models import User
from utils import verify_password
from oauth2 import create_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"])

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(user_credentials.username == User.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")

    if not verify_password(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_token(data={"user_id": user.id})
    
    return {"access_token" : access_token, "token_type":"bearer"}