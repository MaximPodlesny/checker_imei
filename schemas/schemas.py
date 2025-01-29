from pydantic import BaseModel


class ProductRequest(BaseModel):
    artikul: str


class ProductResponse(BaseModel):
    name: str
    artikul: str
    price: float
    rating: float
    total_quantity: int

class MessageResponse(BaseModel):
   message: str