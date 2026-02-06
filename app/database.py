import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Παίρνουμε το DATABASE_URL από environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./parking.db")  # default για local

# Αν είναι SQLite, χρειάζεται check_same_thread
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
