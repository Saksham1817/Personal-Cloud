from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# This is your "users" table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One user can have many files
    files = relationship("File", back_populates="owner")

# This is your "files" table — tracks every uploaded file
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_type = Column(String)
    file_size = Column(BigInteger)
    file_hash = Column(String, index=True)
    file_category = Column(String, default="others")
    storage_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="files")

    # Which user owns this file
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="files")