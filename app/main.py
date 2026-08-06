from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine
from app import models

from . import models
from .limiter import limiter
from .database import engine, get_db
from .routers import products, users, auth, wishlist

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.state.limiter = limiter

app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(wishlist.router)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Try again later."}
    )


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception:
        return {
            "status": "ok",
            "database": "error"
        }


@app.get("/")
def root():
    return {"message": "Hello World"}