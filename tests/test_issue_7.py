from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.api import characters, inventory, users
from app.api.users import get_current_user
from app.db.database import Base
from app.main import app
from app.models.user import User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            user = User(
                username="tester",
                email="test@example.com",
                hashed_password="hash"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


app.dependency_overrides[users.get_db] = override_get_db
app.dependency_overrides[characters.get_db] = override_get_db
app.dependency_overrides[inventory.get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_character():
    response = client.post(
        "/characters",
        json={
            "name": "Rogue",
            "class_name": "Плут",
            "level": 1,
            "route": "city",
            "subclass": "Следопыт",
            "race": "Человек",
            "background": "Бывший сыщик",
            "strength": 8,
            "dexterity": 16,
            "constitution": 12,
            "intelligence": 14,
            "wisdom": 10,
            "charisma": 11,
            "investigation": 7,
            "hp": 9,
            "armor_class": 14,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_character_contains_issue_7_fields():
    character = create_character()

    assert character["subclass"] == "Следопыт"
    assert character["race"] == "Человек"
    assert character["background"] == "Бывший сыщик"
    assert character["investigation"] == 7
    assert character["hp"] == 9
    assert character["armor_class"] == 14


def test_inventory_supports_split_currency_and_item_rarity():
    character = create_character()

    response = client.post(
        f"/characters/{character['id']}/inventory/currency/add",
        json={"gold": 1, "silver": 12, "copper": 15},
    )

    assert response.status_code == 200
    assert response.json()["gold"] == 2
    assert response.json()["silver"] == 3
    assert response.json()["copper"] == 5

    response = client.post(
        f"/characters/{character['id']}/inventory/items",
        json={
            "name": "Зелье лечения",
            "rarity": "Необычный",
            "is_consumable": True,
        },
    )

    item = response.json()["items"][0]
    assert item["rarity"] == "Необычный"
    assert item["is_consumable"] is True


def test_buy_uses_rarity_price_and_adds_item(monkeypatch):
    character = create_character()
    client.post(
        f"/characters/{character['id']}/inventory/currency/add",
        json={"gold": 10, "silver": 0, "copper": 0},
    )
    rolls = iter([10, 2, 30, 0])
    monkeypatch.setattr(inventory.random, "randint", lambda start, end: next(rolls))

    response = client.post(
        f"/characters/{character['id']}/shop/buy",
        json={
            "item_name": "Свиток",
            "rarity": "Обычный",
            "is_consumable": True,
            "searcher_type": "hireling",
            "hireling_level": "Плохой",
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["item_price"] == 50
    assert data["hireling_cost"] == 4
    assert data["total_cost"] == 54
    assert data["inventory"]["gold"] == 9
    assert data["inventory"]["silver"] == 4
    assert data["inventory"]["copper"] == 6
    assert data["inventory"]["items"][0]["name"] == "Свиток"


def test_failed_search_charges_only_hireling_and_does_not_add_item(monkeypatch):
    character = create_character()
    client.post(
        f"/characters/{character['id']}/inventory/currency/add",
        json={"gold": 2, "silver": 0, "copper": 0},
    )
    monkeypatch.setattr(inventory.random, "randint", lambda start, end: 1)

    response = client.post(
        f"/characters/{character['id']}/shop/buy",
        json={
            "item_name": "Редкий меч",
            "rarity": "Редкий",
            "searcher_type": "hireling",
            "hireling_level": "Хороший",
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data["success"] is False
    assert data["hireling_cost"] == 120
    assert data["item_price"] is None
    assert data["inventory"]["gold"] == 0
    assert data["inventory"]["silver"] == 8
    assert data["inventory"]["items"] == []


def test_sell_requires_owned_item_and_removes_it_after_success(monkeypatch):
    character = create_character()
    add_response = client.post(
        f"/characters/{character['id']}/inventory/items",
        json={"name": "Кинжал", "rarity": "Обычный"},
    )
    item_id = add_response.json()["items"][0]["id"]
    rolls = iter([10, 1, 50, 0])
    monkeypatch.setattr(inventory.random, "randint", lambda start, end: next(rolls))

    response = client.post(
        f"/characters/{character['id']}/shop/sell",
        json={
            "item_id": item_id,
            "searcher_type": "character",
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["item_price"] == 75
    assert data["inventory"]["items"] == []
    assert data["inventory"]["silver"] == 7
    assert data["inventory"]["copper"] == 5

    response = client.post(
        f"/characters/{character['id']}/shop/sell",
        json={
            "item_id": item_id,
            "searcher_type": "character",
        },
    )

    assert response.status_code == 400
