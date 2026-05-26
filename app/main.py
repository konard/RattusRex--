from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from app.api.users import router as users_router
from app.db.database import Base, engine
from app.models.user import User
from app.models.character import Character
from app.models.inventory import Inventory, InventoryItem
from app.api.characters import router as character_router
from app.api.shop import router as shop_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(character_router)
app.include_router(shop_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "Мики маус"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
