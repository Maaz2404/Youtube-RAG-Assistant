from sqlalchemy.orm import Session
from models import Transcript
import datetime

def create_temp_transcript(db: Session, session_id: str, video_id: str, video_title: str, channel_name: str) -> Transcript:
    transcript = Transcript(
        session_id=session_id,
        video_id=video_id,
        is_saved=False,
        video_title=video_title,
        channel_name=channel_name,
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript