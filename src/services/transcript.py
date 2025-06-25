
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk["text"] for chunk in transcript_list])
    except Exception as e:
        print("Error fetching transcript:", e)
        return ""