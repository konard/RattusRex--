from pydantic import BaseModel, ConfigDict
from typing import List


class InventoryItemResponse(BaseModel):
    id: int
    name: str
    rarity: str
    is_consumable: bool

    model_config = ConfigDict(from_attributes=True)


class InventoryResponse(BaseModel):
    id: int
    character_id: int
    gold: int
    silver: int
    copper: int
    items: List[InventoryItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AddItemRequest(BaseModel):
    name: str
    rarity: str = "Обычный"
    is_consumable: bool = False


class GoldUpdateRequest(BaseModel):
    amount: int


class CurrencyUpdateRequest(BaseModel):
    gold: int = 0
    silver: int = 0
    copper: int = 0


class ShopSearchRequest(BaseModel):
    item_name: str
    rarity: str
    is_consumable: bool = False
    searcher_type: str = "character"
    hireling_level: str = "Плохой"


class ShopBuyRequest(ShopSearchRequest):
    pass


class ShopSellRequest(BaseModel):
    item_id: int
    searcher_type: str = "character"
    hireling_level: str = "Плохой"


class ShopResult(BaseModel):
    success: bool
    search_roll: int
    modifier: int
    total_roll: int
    dc: int
    days: int
    hireling_cost: int
    price_roll: int | None
    multiplier: float | None
    item_price: int | None
    total_cost: int | None
    inventory: InventoryResponse
