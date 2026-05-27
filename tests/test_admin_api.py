import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.users import get_db
from app.core.security import hash_password
from app.db.database import Base
from app.main import app
from app.models.character import Character
from app.models.inventory import Inventory
from app.models.user import User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_user(email: str, is_admin: bool = False) -> User:
    db = TestingSessionLocal()
    user = User(
        username=email.split("@")[0],
        email=email,
        hashed_password=hash_password("secret"),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def login(email: str) -> dict[str, str]:
    response = client.post(
        "/login",
        data={"username": email, "password": "secret"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_character(user_id: int) -> Character:
    db = TestingSessionLocal()
    character = Character(
        name="Mira",
        class_name="Wizard",
        route="north",
        user_id=user_id,
        hp=0,
        armor_class=11,
        level=1,
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    db.close()
    return character


def test_admin_can_manage_character_and_user_state():
    admin = create_user("admin@example.com", is_admin=True)
    player = create_user("player@example.com")
    character = create_character(player.id)
    headers = login(admin.email)

    xp_response = client.post(
        f"/admin/characters/{character.id}/xp",
        json={"amount": 5},
        headers=headers,
    )
    assert xp_response.status_code == 200
    assert xp_response.json()["xp"] == 5

    gold_response = client.post(
        f"/admin/characters/{character.id}/gold",
        json={"amount": 3},
        headers=headers,
    )
    assert gold_response.status_code == 200
    assert gold_response.json()["gold"] == 3

    item_response = client.post(
        f"/admin/characters/{character.id}/item",
        json={"name": "Potion", "rarity": "Обычный", "is_consumable": True},
        headers=headers,
    )
    assert item_response.status_code == 200
    assert item_response.json()["items"][0]["name"] == "Potion"

    revive_response = client.post(
        f"/admin/characters/{character.id}/revive",
        headers=headers,
    )
    assert revive_response.status_code == 200
    assert revive_response.json()["hp"] == 1
    assert revive_response.json()["is_dead"] is False

    karma_response = client.post(
        f"/admin/users/{player.id}/karma",
        json={"amount": 2},
        headers=headers,
    )
    assert karma_response.status_code == 200
    assert karma_response.json()["karma"] == 2


def test_non_admin_cannot_use_admin_endpoints():
    player = create_user("player@example.com")
    character = create_character(player.id)
    headers = login(player.email)

    response = client.post(
        f"/admin/characters/{character.id}/xp",
        json={"amount": 5},
        headers=headers,
    )

    assert response.status_code == 403
