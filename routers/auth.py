from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        phone=user.phone,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        batch_id=user.batch_id,
        mess_id=user.mess_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = auth.create_access_token(data={"sub": str(db_user.id)})
    return {"token": access_token, "user": db_user}

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if user.role != login_data.role:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role mismatch. Expected {login_data.role}",
        )
        
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"token": access_token, "user": user}
