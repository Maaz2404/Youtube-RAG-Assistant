from fastapi import  FastAPI,HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from services.rag import run_rag_pipeline,move_embeddings,transcribe_and_store
from services.transcript_ops import create_temp_transcript
from dotenv import load_dotenv
from database import SessionLocal,get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from schemas import AskRequest, UserCredentials,TranscriptOut,TranscribeRequest
from models import User, Transcript
from utils import hash
from oauth2 import get_current_user,get_optional_current_user
from typing import List,Optional
import os
load_dotenv()


    
    

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", 
        "chrome-extension://cfjbklapkneciahbdkknmgplgjhfoafb"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to the YouTube Transcript API"}

@app.post("/transcribe")
def transcribe_video(request:TranscribeRequest,session_id: str,db: Session = Depends(get_db)):
    print(f"Received video ID: {request.video_id}")
    transcribe_and_store(request.video_id,db,session_id,request.video_title,request.channel_name)
    return {"message": "Transcription started successfully"}
@app.post("/ask" )
def ask_transcript(request: AskRequest,user_id: Optional[int] = Depends(get_optional_current_user),   db: Session = Depends(get_db)):
    id = request.video_id
    query = request.query
    if (id != ""):
        answer = run_rag_pipeline(id, user_id=user_id, query=query, db=db)
        return {"answer": answer}
    else:
        raise HTTPException(status_code=400, detail="Invalid video ID")

@app.patch("/save/{video_id}", status_code=status.HTTP_200_OK)
def save_transcript(video_id:str, user_id: int = Depends(get_current_user), db:Session = Depends(get_db)):
    
   
    # move the embeddings from vector databsase
    old_namespace = f"{video_id}_temp"
    new_namespace = f"{user_id}:{video_id}"
    move_embeddings(old_namespace, new_namespace)
    transcript = db.query(Transcript).filter(Transcript.video_id == video_id,
                                             Transcript.is_saved == False).first() 
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript not found or already exists")
    transcript.is_saved = True
    transcript.user_id = str(user_id)
    db.commit()
    db.refresh(transcript)
    return {"message": "Transcript saved successfully", "transcript_id": transcript.id}

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_credentials: UserCredentials, db: Session = Depends(get_db)):
    hash_password = hash(user_credentials.password)
    user_credentials.password = hash_password
    user = User(
        email=user_credentials.email,
        password=user_credentials.password
    )
    #check if user already exists
    existing_user = db.query(User).filter(User.email == user_credentials.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "user_id": user.id}

@app.get("/transcripts", response_model=List[TranscriptOut], status_code=status.HTTP_200_OK)
def get_transcripts(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    transcripts = db.query(Transcript).filter(Transcript.user_id == str(user_id)).all()
    return transcripts  

@app.get("/transcripts/{video_id}", response_model=TranscriptOut, status_code=status.HTTP_200_OK)
def get_single_saved_transcript(video_id: str, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    transcript = db.query(Transcript).filter(
        Transcript.video_id == video_id,
        Transcript.user_id == str(user_id)
    ).first()
    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    return transcript  

#add auth route using router
from auth import router 
app.include_router(router,tags=["auth"])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
    