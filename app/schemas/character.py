from pydantic import BaseModel
from typing import Optional

class CharacterCreate(BaseModel):
    name: str
    class_name: str
    route: str

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    class_name: Optional[str] = None
    level: Optional[int] = None
    xp: Optional[int] = None
    route: Optional[str] = None


