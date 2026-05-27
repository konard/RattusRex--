from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.database import SessionLocal
from app.models.character import Character
from app.models.user import User
from app.api.users import get_current_user
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate
)
from app.api.users import get_db


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

@router.post("/characters")
def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    character = Character(
        **character_data.dict(),
        user_id=current_user.id
    )

    db.add(character)

    db.commit()

    db.refresh(character)

    return {
        "id": character.id,
        "name": character.name,
        "class_name": character.class_name,
        "level": character.level,
        "xp": character.xp,
        "route": character.route,
        "is_dead": character.is_dead
    }

@router.get("/characters")
def get_characters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    characters = db.query(Character).filter(
        Character.user_id == current_user.id
    ).all()

    return characters


@router.patch("/characters/{character_id}")
def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    character = db.query(Character).filter(
        Character.id == character_id,
        Character.user_id == current_user.id
    ).first()

    if not character:
        raise HTTPException(
            status_code=404,
            detail="Character not found"
        )
    if character_data.xp is not None:

        character.xp += character_data.xp

        while character.xp >= character.level + 1:
            character.level += 1
            character.xp = 0

    update_data = character_data.dict(exclude_unset=True, exclude="xp")

    for key, value in update_data.items():
        setattr(character, key, value)

    db.commit()
    db.refresh(character)

    return character
