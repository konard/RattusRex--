from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.character import Character
from app.models.inventory import Inventory, InventoryItem
from app.models.user import User
from app.api.users import get_current_user
from app.schemas.inventory import (
    InventoryResponse,
    AddItemRequest,
    GoldUpdateRequest
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_character_inventory(
    character_id: int,
    current_user: User,
    db: Session
) -> Inventory:
    character = db.query(Character).filter(
        Character.id == character_id,
        Character.user_id == current_user.id
    ).first()

    if not character:
        raise HTTPException(
            status_code=404,
            detail="Character not found"
        )

    inventory = db.query(Inventory).filter(
        Inventory.character_id == character_id
    ).first()

    if not inventory:
        inventory = Inventory(
            character_id=character_id,
            gold=0,
            silver=0,
            copper=0
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

    return inventory


@router.get("/characters/{character_id}/inventory", response_model=InventoryResponse)
def get_inventory(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inventory = get_character_inventory(character_id, current_user, db)
    return inventory


@router.post("/characters/{character_id}/inventory/items", response_model=InventoryResponse)
def add_item(
    character_id: int,
    item_data: AddItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inventory = get_character_inventory(character_id, current_user, db)

    item = InventoryItem(
        name=item_data.name,
        rarity=item_data.rarity,
        consumable=item_data.consumable,
        inventory_id=inventory.id
    )
    db.add(item)
    db.commit()
    db.refresh(inventory)

    return inventory


@router.delete("/characters/{character_id}/inventory/items/{item_id}", response_model=InventoryResponse)
def remove_item(
    character_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inventory = get_character_inventory(character_id, current_user, db)

    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.inventory_id == inventory.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db.delete(item)
    db.commit()
    db.refresh(inventory)

    return inventory


@router.post("/characters/{character_id}/inventory/gold/add", response_model=InventoryResponse)
def add_gold(
    character_id: int,
    gold_data: GoldUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if gold_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )

    inventory = get_character_inventory(character_id, current_user, db)

    inventory.gold += gold_data.amount
    db.commit()
    db.refresh(inventory)

    return inventory


@router.post("/characters/{character_id}/inventory/gold/subtract", response_model=InventoryResponse)
def subtract_gold(
    character_id: int,
    gold_data: GoldUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if gold_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )

    inventory = get_character_inventory(character_id, current_user, db)

    if inventory.gold < gold_data.amount:
        raise HTTPException(
            status_code=400,
            detail="Not enough gold"
        )

    inventory.gold -= gold_data.amount
    db.commit()
    db.refresh(inventory)

    return inventory
