from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.users import get_current_user, get_db
from app.models.character import Character
from app.models.inventory import Inventory, InventoryItem
from app.models.user import User
from app.schemas.inventory import (
    AddItemRequest,
    CurrencyUpdateRequest,
    InventoryResponse,
)
from app.schemas.user import KarmaUpdate

router = APIRouter(prefix="/admin")


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def get_character_or_404(character_id: int, db: Session) -> Character:
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


def get_or_create_inventory(character_id: int, db: Session) -> Inventory:
    inventory = db.query(Inventory).filter(
        Inventory.character_id == character_id
    ).first()
    if inventory:
        return inventory

    inventory = Inventory(character_id=character_id, gold=0, silver=0, copper=0)
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


@router.get("/characters")
def get_admin_characters(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(Character).all()


@router.post("/characters/{character_id}/xp")
def add_character_xp(
    character_id: int,
    xp_data: KarmaUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    character = get_character_or_404(character_id, db)
    character.xp += xp_data.amount
    while character.xp >= character.level + 1:
        character.level += 1
        character.xp = 0
    db.commit()
    db.refresh(character)
    return character


@router.post("/characters/{character_id}/gold", response_model=InventoryResponse)
def add_character_currency(
    character_id: int,
    currency_data: CurrencyUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    get_character_or_404(character_id, db)
    inventory = get_or_create_inventory(character_id, db)
    inventory.gold += currency_data.gold
    inventory.silver += currency_data.silver
    inventory.copper += currency_data.copper
    db.commit()
    db.refresh(inventory)
    return inventory


@router.post("/characters/{character_id}/revive")
def revive_character(
    character_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    character = get_character_or_404(character_id, db)
    character.is_dead = False
    if character.hp <= 0:
        character.hp = 1
    db.commit()
    db.refresh(character)
    return character


@router.post("/characters/{character_id}/item", response_model=InventoryResponse)
def grant_character_item(
    character_id: int,
    item_data: AddItemRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    get_character_or_404(character_id, db)
    inventory = get_or_create_inventory(character_id, db)
    db.add(InventoryItem(
        name=item_data.name,
        rarity=item_data.rarity,
        consumable=item_data.consumable,
        inventory_id=inventory.id,
    ))
    db.commit()
    db.refresh(inventory)
    return inventory


@router.post("/users/{user_id}/karma")
def update_user_karma(
    user_id: int,
    karma_data: KarmaUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.karma += karma_data.amount
    db.commit()
    db.refresh(user)
    return {"id": user.id, "karma": user.karma}
