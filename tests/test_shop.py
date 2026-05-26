from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.shop import get_db as shop_get_db
from app.api.users import get_db as users_get_db
from app.db.database import Base
from app.main import app


@asynccontextmanager
async def no_database_lifespan(app):
    yield


app.router.lifespan_context = no_database_lifespan


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[users_get_db] = override_get_db
    app.dependency_overrides[shop_get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/users",
        json={
            "username": "hero-owner",
            "email": "hero@example.com",
            "password": "secret123"
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "hero@example.com",
            "password": "secret123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def character_id(client, auth_headers):
    response = client.post(
        "/characters",
        json={
            "name": "Ratmir",
            "class_name": "merchant",
            "route": "north"
        },
        headers=auth_headers
    )
    return response.json()["id"]


def test_buy_item_subtracts_price_and_mercenary_cost(
    client,
    auth_headers,
    character_id
):
    client.post(
        f"/characters/{character_id}/inventory/gold/add",
        json={"amount": 100},
        headers=auth_headers
    )

    response = client.post(
        f"/characters/{character_id}/shop/buy",
        json={
            "item_name": "Меч",
            "item_price": 30,
            "mercenary_cost": 15
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["gold"] == 55
    assert [item["name"] for item in body["items"]] == ["Меч"]


def test_sell_item_requires_inventory_item_and_updates_gold(
    client,
    auth_headers,
    character_id
):
    client.post(
        f"/characters/{character_id}/inventory/gold/add",
        json={"amount": 100},
        headers=auth_headers
    )
    client.post(
        f"/characters/{character_id}/shop/buy",
        json={
            "item_name": "Щит",
            "item_price": 20,
            "mercenary_cost": 10
        },
        headers=auth_headers
    )

    response = client.post(
        f"/characters/{character_id}/shop/sell",
        json={
            "item_name": "Щит",
            "item_price": 50,
            "mercenary_cost": 5
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["gold"] == 115
    assert body["items"] == []

    response = client.post(
        f"/characters/{character_id}/shop/sell",
        json={
            "item_name": "Щит",
            "item_price": 50,
            "mercenary_cost": 5
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Item is not in inventory"


def test_user_karma_can_be_added_and_subtracted(client, auth_headers):
    response = client.post(
        "/me/karma/add",
        json={"amount": 7},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["karma"] == 7

    response = client.post(
        "/me/karma/subtract",
        json={"amount": 3},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["karma"] == 4
