from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app import models
from app.auth import hash_password, verify_password, create_access_token
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# --- What data we expect when someone registers ---
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

# --- Register a new user ---
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if username already taken
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check if email already taken
    existing_email = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the user with a hashed password (never store plain passwords)
    user = models.User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": f"User '{user.username}' created successfully"}

# --- Login and get a token ---
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find the user
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # Create and return a JWT token
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- Get your own profile (requires login) ---
@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }