from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool = True


class ProductCreate(ProductBase):
    # Input limits live here and not on ProductBase, so existing rows can always be returned.
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    description: Annotated[str, StringConstraints(max_length=2000)]
    price: float = Field(gt=0, le=1_000_000)

# --- User Schemas ---

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str  
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    owner_id: int
    #owner: UserOut
    model_config = ConfigDict(from_attributes=True)


class ProductOut(ProductResponse):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # bcrypt only handles 72 bytes. Count bytes, not characters, because
        # accented letters and emoji take more than one byte each.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return value
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Auth & Token Schemas 

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None




class Wishlist(BaseModel):
    product_id: int
    dir: int = Field(ge=0, le=1)