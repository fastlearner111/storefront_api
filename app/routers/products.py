from fastapi import FastAPI, HTTPException, status, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from .. import oauth2
from ..dependencies import require_admin  

router = APIRouter(
    prefix="/products",
    tags=['Products']
)


@router.get("/", response_model=List[schemas.ProductOut])
def get_products(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str = ""
):
    products = (
        db.query(models.Product)
        .filter(models.Product.name.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return products


@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.ProductResponse,
             dependencies=[Depends(require_admin)])   
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_product = models.Product(owner_id=current_user.id, **product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/{id}", response_model=schemas.ProductOut)
def get_product(
    id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
        )

    return product



@router.delete("/{id}", 
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_admin)])   
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Not Found")

    

    product_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}", 
            response_model=schemas.ProductResponse,
            dependencies=[Depends(require_admin)])   
def update_product(
    id: int,
    updated_product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_query.update(updated_product.model_dump(), synchronize_session=False)
    db.commit()

    return product_query.first()
