from pydantic import BaseModel
from typing import List
from pydantic import ConfigDict


class InventoryItemResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    id: int
    character_id: int
    gold: int
    items: List[InventoryItemResponse] = []

    class Config:
        from_attributes = True


class AddItemRequest(BaseModel):
    name: str


class GoldUpdateRequest(BaseModel):
    amount: int

class ShopTransactionRequest(BaseModel):
    item_name: str
    item_price: int
    mercenary_cost: int = 0