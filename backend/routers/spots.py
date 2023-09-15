from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/spots", tags=["Spots"])

# common dependency
DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[models.User, Depends(oauth2.get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.SpotOut])
def get_spots(db: DbDep, current_user: CurrentUserDep):
    return db.query(models.Spot).all()


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.SpotOut)
def get_one_spot(id: int, db: DbDep, current_user: CurrentUserDep):
    if spot := db.query(models.Spot).filter(models.Spot.id == id).first():
        return spot
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Spot with ID {id} not found"
        )


@router.post("/", response_model=schemas.SpotOut)
def create_spot(spot_in: schemas.SpotIn, db: DbDep):
    if db.query(models.Spot).filter(models.Spot.name == spot_in.name).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Spot with {spot_in.name} already exists",
        )
    new_spot = models.Spot(**spot_in.model_dump())
    try:
        db.add(new_spot)
        db.commit()
        db.refresh(new_spot)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Spot named {spot_in.name} already exists",
        ) from e

    return new_spot


@router.delete("/{id}")
def delete_spot(id: int, db: DbDep, current_user: CurrentUserDep):
    """
    Delete a spot by ID.
    """
    spot_query = db.query(models.Spot).filter(models.Spot.id == id)
    spot = spot_query.first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spot with ID {id} not found in database",
        )
    spot_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.SpotOut)
def update_spot(id: int, new_spot: schemas.SpotUpdate, db: DbDep):
    """Update spot by ID."""
    spot_query = db.query(models.Spot).filter(models.Spot.id == id)
    spot = spot_query.first()

    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Spot with ID {id} not found"
        )

    # updating provided data and validating it against schemas
    stored_spot_data = jsonable_encoder(spot)
    stored_spot_model = schemas.SpotUpdate(**stored_spot_data)
    update_data = new_spot.model_dump(exclude_unset=True)
    updated_spot = stored_spot_model.model_copy(update=update_data)

    for key, value in updated_spot.model_dump().items():
        setattr(spot, key, value)

    try:
        db.commit()
        db.refresh(spot)
    except IntegrityError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Spot with this data already exists",
        ) from e
    return spot
