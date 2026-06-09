from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This creates a local SQLite database file called cloud.db
DATABASE_URL = "sqlite:///./cloud.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each request to the server gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All your database models (tables) will inherit from this
Base = declarative_base()

# This function gives a database session to each API request, then closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()