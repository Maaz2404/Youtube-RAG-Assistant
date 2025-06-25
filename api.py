from fastapi import  FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel,Field
from typing import List, Optional
from services.rag import run_rag_pipeline

from dotenv import load_dotenv


load_dotenv()

class TranscriptRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    query: str = Field(..., description="User query related to the video transcript")
    
    

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to the YouTube Transcript API"}

@app.post("/ask" )
def ask_transcript(request: TranscriptRequest):
    
    id = request.video_id
    query = request.query
    if (id != ""):
        answer = run_rag_pipeline(id, query)
        return {"answer": answer}
    else:
        raise HTTPException(status_code=400, detail="Invalid video ID")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    
    
    