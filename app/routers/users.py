from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, oauth2, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = utils.hash(user.password)

    # Hardcode 'user' role for public registration
    new_user = models.User(
        email=user.email,
        password=hashed_password,
        role="user",
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Users may read their own record; admins may read any record.
    # The permission check comes first so a non-admin learns nothing about which ids exist.
    if current_user.id != id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )

    return user