from fastapi import APIRouter, Response, status, HTTPException, Depends
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder
from typing import Annotated

router = APIRouter(prefix="/users", tags=["Users"])

# common dependency
DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[models.User, Depends(oauth2.get_current_user)]


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


@router.get("/spots", response_model=schemas.UserWithSpots)
def get_user_spots(db: DbDep, user_auth: CurrentUserDep):
    print(user_auth.id)
    user_with_spots = (
        db.query(models.User)
        .options(selectinload(models.User.spots))
        .filter(models.User.id == user_auth.id)
        .first()
    )
    print(user_with_spots)
    return user_with_spots


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
def get_all_active_users(db: DbDep):
    """
    Get all active users.
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


@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def update_user(id: int, new_user: schemas.UserUpdate, db: DbDep):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found in database",
        )
    stored_user_data = jsonable_encoder(user)
    stored_user_model = schemas.UserUpdate(**stored_user_data)
    update_data = new_user.model_dump(exclude_unset=True)
    updated_user = stored_user_model.model_copy(update=update_data)

    for key, value in updated_user.model_dump().items():
        setattr(user, key, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this data already exists",
        )
    return user


# spots
@router.post("/add_spot/{id}")
def add_spot_to_user(id: int, db: DbDep, user_auth: CurrentUserDep):
    """
    Adds a spot to the user's list of spots.

    This function looks up a spot by its ID and associates it with the authenticated user.
    If the spot or user does not exist, or if the user is already associated with the spot,
    an HTTPException is raised.

    Parameters:
    - id (int): The ID of the spot to be added.

    Returns:
    - Response: An HTTP 201 Created status code if the spot is successfully added to the user.

    Exceptions:
    - HTTPException: 404 if the spot with the given ID does not exist.
    - HTTPException: 409 if the user is already associated with the spot.
    """

    spot = db.query(models.Spot).filter(models.Spot.id == id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spot with id {id} do not exist",
        )
    user_spot_check = (
        db.query(models.User)
        .join(models.UserSpots)
        .join(models.Spot)
        .filter(models.User.id == user_auth.id, models.Spot.id == id)
        .first()
    )
    if user_spot_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with id {user_auth.id} is already added to spot with id {id}",
        )
    try:
        user_auth.spots.append(spot)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with id {user_auth.id} is already added to spot with id {id}",
        )
    return Response(status_code=status.HTTP_201_CREATED)
