from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def wishlist_action(
    wishlist: schemas.Wishlist,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    product = db.query(models.Product).filter(models.Product.id == wishlist.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id:{wishlist.product_id} does not exist"
        )

    wishlist_query = db.query(models.Wishlist).filter(
        models.Wishlist.product_id == wishlist.product_id,
        models.Wishlist.user_id == current_user.id
    )
    found_wishlist = wishlist_query.first()

    if wishlist.dir == 1:
        if found_wishlist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already added product {wishlist.product_id} to wishlist"
            )
        new_wishlist = models.Wishlist(
            product_id=wishlist.product_id,
            user_id=current_user.id
        )
        db.add(new_wishlist)
        db.commit()
        return {"message": "Successfully added to wishlist"}

    else:
        if not found_wishlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wishlist entry does not exist"
            )

        wishlist_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "Successfully removed from wishlist"}

@router.get("/", status_code=200)
def get_wishlist(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    wishlist_items = (
        db.query(models.Wishlist, models.Product)
        .join(models.Product, models.Product.id == models.Wishlist.product_id)
        .filter(models.Wishlist.user_id == current_user.id)
        .all()
    )

    results = []
    for wishlist, product in wishlist_items:
        results.append({
            "product_id": wishlist.product_id,
            "product": product
        })

    return results
