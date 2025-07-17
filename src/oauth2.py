from jose import JWTError, jwt
from datetime import datetime, timedelta,timezone
from fastapi import Depends, HTTPException, status
from schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

def verify_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=int(id))
        return token_data.id
    except JWTError:
        raise credentials_exception
    
def get_current_user(token:str = Depends(oauth2_scheme)):
      credentials_exception = HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Could not validate credentials",
          headers={"WWW-Authenticate": "Bearer"},
      )
      return verify_token(token, credentials_exception)
  


from fastapi import Request

def get_optional_current_user(request: Request):
    auth: str = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return verify_token(token, credentials_exception)
    except HTTPException:
        return None