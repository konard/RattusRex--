from pydantic import BaseModel
from pydantic import ConfigDict
from typing import List


class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    character_id: int
    gold: int
    items: List[InventoryItemResponse] = []


class GoldUpdateRequest(BaseModel):
    amount: int


class ShopTransactionRequest(BaseModel):
    item_name: str
    item_price: int
    mercenary_cost: int = 0
