from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import oauth2, schemas, models, database, utils
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentification"])


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(database.get_db)],
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    HTTP_INVALID_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )

    if not user:
        raise HTTP_INVALID_CREDENTIALS

    verified_password = utils.verify_password(form_data.password, user.password)
    if not verified_password:
        raise HTTP_INVALID_CREDENTIALS

    # Create token - password verified
    access_token = oauth2.create_access_token(
        data={
            "user_id": user.id,
            "user_email": user.email,
        }
    )
    token = schemas.Token(access_token=access_token, token_type="bearer")
    return token
