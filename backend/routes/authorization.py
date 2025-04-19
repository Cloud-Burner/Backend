from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.core.db import get_db
from backend.utils import auth as auth_utils

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        hashed_password=auth_utils.hash_password(user.password),
        role=user.role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter_by(email=form_data.username).first()
    if not user or not auth_utils.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth_utils.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
async def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth_utils.decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
