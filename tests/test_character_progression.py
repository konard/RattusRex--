from app.api.characters import update_character
from app.models.character import Character
from app.schemas.character import CharacterUpdate


class QueryStub:
    def __init__(self, character):
        self.character = character

    def filter(self, *args):
        return self

    def first(self):
        return self.character


class DbStub:
    def __init__(self, character):
        self.character = character
        self.committed = False
        self.refreshed = None

    def query(self, model):
        return QueryStub(self.character)

    def commit(self):
        self.committed = True

    def refresh(self, character):
        self.refreshed = character


class UserStub:
    id = 1


def make_character(level=1, xp=0):
    character = Character()
    character.id = 1
    character.user_id = 1
    character.name = "Hero"
    character.class_name = "Warrior"
    character.route = "North"
    character.level = level
    character.xp = xp
    return character


def test_character_level_is_derived_from_xp_threshold():
    character = make_character(level=1, xp=0)
    db = DbStub(character)

    updated = update_character(
        character_id=1,
        character_data=CharacterUpdate(xp=2),
        current_user=UserStub(),
        db=db,
    )

    assert updated.level == 2
    assert updated.xp == 0
    assert db.committed
    assert db.refreshed is character


def test_character_level_cannot_be_updated_manually():
    assert "level" not in CharacterUpdate.__fields__
