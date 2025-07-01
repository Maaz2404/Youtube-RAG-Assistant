from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Maazahmad612/@localhost:5432/yt-rag")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    db = None
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # basic test query
        print("✅ Database connection successful!")
    except Exception as e:
        print("❌ Database connection failed!")
        print("Error:", e)
    finally:
        if db is not None:
            db.close()
            
if __name__ == "__main__":
    test_db_connection()
