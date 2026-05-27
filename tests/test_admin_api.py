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
        hashed_password=hash_password("password"),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def token_for(email: str) -> str:
    response = client.post(
        "/login",
        data={"username": email, "password": "password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_for(email)}"}


def create_character(user_id: int, hp: int = 0) -> Character:
    db = TestingSessionLocal()
    character = Character(
        name="Mira",
        class_name="Wizard",
        level=1,
        route="elf",
        hp=hp,
        user_id=user_id,
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    db.close()
    return character


def test_me_exposes_admin_flag():
    create_user("admin@example.com", is_admin=True)

    response = client.get("/me", headers=auth_headers("admin@example.com"))

    assert response.status_code == 200
    assert response.json()["is_admin"] is True


def test_non_admin_cannot_use_admin_endpoint():
    owner = create_user("owner@example.com")
    character = create_character(owner.id)

    response = client.post(
        f"/admin/characters/{character.id}/xp",
        json={"amount": 10},
        headers=auth_headers("owner@example.com"),
    )

    assert response.status_code == 403


def test_admin_can_update_xp_gold_karma_item_and_revive_character():
    owner = create_user("owner@example.com")
    admin = create_user("admin@example.com", is_admin=True)
    character = create_character(owner.id, hp=0)

    xp_response = client.post(
        f"/admin/characters/{character.id}/xp",
        json={"amount": 5},
        headers=auth_headers(admin.email),
    )
    assert xp_response.status_code == 200
    assert xp_response.json()["level"] > 1

    gold_response = client.post(
        f"/admin/characters/{character.id}/gold",
        json={"gold": 7, "silver": 2, "copper": 1},
        headers=auth_headers(admin.email),
    )
    assert gold_response.status_code == 200
    assert gold_response.json()["gold"] == 7
    assert gold_response.json()["silver"] == 2
    assert gold_response.json()["copper"] == 1

    item_response = client.post(
        f"/admin/characters/{character.id}/item",
        json={"name": "Potion", "rarity": "common", "consumable": True},
        headers=auth_headers(admin.email),
    )
    assert item_response.status_code == 200
    assert item_response.json()["items"][0]["rarity"] == "common"

    karma_response = client.post(
        f"/admin/users/{owner.id}/karma",
        json={"amount": -3},
        headers=auth_headers(admin.email),
    )
    assert karma_response.status_code == 200
    assert karma_response.json()["karma"] == -3

    revive_response = client.post(
        f"/admin/characters/{character.id}/revive",
        headers=auth_headers(admin.email),
    )
    assert revive_response.status_code == 200
    assert revive_response.json()["is_dead"] is False
    assert revive_response.json()["hp"] > 0


def test_admin_can_list_all_characters():
    owner = create_user("owner@example.com")
    admin = create_user("admin@example.com", is_admin=True)
    create_character(owner.id)

    response = client.get(
        "/admin/characters",
        headers=auth_headers(admin.email),
    )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Mira"
