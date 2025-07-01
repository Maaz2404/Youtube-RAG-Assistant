import json
import os
from datetime import datetime, timedelta,timezone
from services.rag import delete_embeddings  # You need to implement this

TEMP_TRACK_FILE = "temp_embeddings.json"
EXPIRY_MINUTES = 60  # 1 hr

def cleanup_temp_embeddings():
    if not os.path.exists(TEMP_TRACK_FILE):
        return
    with open(TEMP_TRACK_FILE, "r") as f:
        data = json.load(f)
    now = datetime.now(timezone.utc)
    to_delete = []
    for video_id, ts in data.items():
        created = datetime.fromisoformat(ts)
        if now - created > timedelta(minutes=EXPIRY_MINUTES):
            delete_embeddings(f"{video_id}_temp")
            to_delete.append(video_id)
    # Remove deleted entries
    for vid in to_delete:
        del data[vid]
    with open(TEMP_TRACK_FILE, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    cleanup_temp_embeddings()