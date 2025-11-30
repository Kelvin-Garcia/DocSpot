from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get the database URL from environment variables
# For local development, you might set it directly or use a .env file
# For Neon, it will be provided as DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_gLe4nSBvJG9H@ep-lucky-band-a4whki7l-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
