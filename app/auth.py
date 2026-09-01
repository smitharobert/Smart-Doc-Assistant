import bcrypt
import jwt
import os
from datetime import datetime,timedelta,timezone

SECRET_KEY=os.getenv("SECRET_KEY", "your-default-dev-key")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30


def verify_password(plain_password:str,hashed_password:str)->bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"),hashed_password.encode("utf-8"))

def hash_password(password:str)->str:
    salt=bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"),salt).decode("utf-8")

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM) 
    return encoded_jwt 
    
