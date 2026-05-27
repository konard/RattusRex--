from pydantic import BaseModel
from typing import List
from pydantic import ConfigDict


class InventoryItemResponse(BaseModel):
    id: int
    name: str
    rarity: str
    consumable: bool

    class Config:
        from_attributes = True


class InventoryResponse(BaseModel):
    id: int
    character_id: int
    gold: int
    silver: int
    copper: int
    items: List[InventoryItemResponse] = []

    class Config:
        from_attributes = True


class AddItemRequest(BaseModel):
    name: str
    rarity: str = "common"
    consumable: bool = False


class GoldUpdateRequest(BaseModel):
    amount: int


class CurrencyUpdateRequest(BaseModel):
    gold: int = 0
    silver: int = 0
    copper: int = 0

class ShopTransactionRequest(BaseModel):
    item_name: str
    item_price: int
    mercenary_cost: int = 0
    rarity: str = "common"
    consumable: bool = False
