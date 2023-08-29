from fastapi import APIRouter, status, HTTPException, Depends
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    find_user = db.query(models.User).filter(models.User.email == user.email).first()

    if find_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with {user.email} already exists",
        )

    user.password = utils.get_password_hash(user.password)
    new_user = models.User(**user.model_dump())
    # try block with catching exception if someone added user with same credentials at the same time
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with {user.email} already exists",
        )

    return new_user
