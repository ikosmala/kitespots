from fastapi import APIRouter, Response, status, HTTPException, Depends
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder
from typing import Annotated

router = APIRouter(prefix="/users", tags=["Users"])

# common dependency
DbDep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: DbDep):
    """
    Create a new user in the database.
    """
    find_user = db.query(models.User).filter(models.User.email == user.email).first()

    if find_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with {user.email} already exists",
        )

    user.password = utils.get_password_hash(user.password)
    new_user = models.User(**user.model_dump())
    # try block with catching exception if someone added user with same credentials after initial check
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


@router.get("/{id}", response_model=schemas.UserOut)
def get_one_user(id: int, db: DbDep):
    """Get information about user by ID."""
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found in database.",
        )
    return user


@router.get("/", response_model=list[schemas.UserOut])
def get_all_active_users(
    db: DbDep, current_user: Annotated[models.User, Depends(oauth2.get_current_user)]
):
    """
    Get all active users. Must be authentificated.
    """
    users = db.query(models.User).filter(models.User.active == True).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found in database"
        )
    return users


@router.delete("/{id}")
def delete_user(id: int, db: DbDep):
    """
    Delete a user by ID.
    """
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found in database",
        )
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut
)
def update_user_info(id: int, new_user: schemas.UserUpdate, db: DbDep):
    query_user = db.query(models.User).filter(models.User.id == id)
    old_user = query_user.first()

    if not old_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found in database",
        )
    stored_user_data = jsonable_encoder(old_user)
    stored_user_model = schemas.UserUpdate(**stored_user_data)
    update_data = new_user.model_dump(exclude_unset=True)
    updated_user = stored_user_model.model_copy(update=update_data)
    try:
        query_user.update(updated_user.model_dump(), synchronize_session=False)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this data already exists",
        )
    return query_user.first()
