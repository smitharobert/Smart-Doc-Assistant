from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
import os
from app.database import engine, SessionLocal
from app import models
from app.auth import SECRET_KEY, ALGORITHM, hash_password, verify_password, create_access_token
from app.core.document_processor import DocumentProcessor
from app.core.rag_engine import RagEngine

models.Base.metadata.create_all(bind=engine)
os.makedirs("uploads", exist_ok=True)

app = FastAPI()
processor = DocumentProcessor()
engine_rag = RagEngine()

class UserCreate(BaseModel):
    email: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token(data={"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/upload")
def upload(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and Word files are supported")
    
    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    
    if file.filename.endswith(".pdf"):
        text = processor.extract_text_from_pdf(filepath)
    else:
        text = processor.extract_text_from_docx(filepath)
        
    chunks = processor.chunk_text(text)
    
    collection_name = f"user_{current_user.id}_collection"
    engine_rag.add_documents(chunks, collection_name)
    
    new_doc = models.Document(filename=file.filename, filepath=filepath, user_id=current_user.id)
    db.add(new_doc)
    db.commit()
    
    return {"message": "File uploaded and indexed successfully"}

@app.get("/")
def home():
    return {"message": "AI document processor API"}
@app.post("/search")
def search_document(query: str, current_user: models.User = Depends(get_current_user)):
    collection_name = f"user_{current_user.id}_collection"
    answer = engine_rag.answer_question(query, collection_name)
    return {"answer": answer}

