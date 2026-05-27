from pydantic import BaseModel
from typing import Optional

class CharacterCreate(BaseModel):
    name: str
    class_name: str
    level: int
    route: str
    subclass: str = ""
    race: str = ""
    background: str = ""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    investigation: int = 0
    hp: int = 0
    armor_class: int = 10

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    class_name: Optional[str] = None
    xp: Optional[int] = None
    route: Optional[str] = None
    subclass: Optional[str] = None
    race: Optional[str] = None
    background: Optional[str] = None
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    constitution: Optional[int] = None
    intelligence: Optional[int] = None
    wisdom: Optional[int] = None
    charisma: Optional[int] = None
    investigation: Optional[int] = None
    hp: Optional[int] = None
    armor_class: Optional[int] = None


