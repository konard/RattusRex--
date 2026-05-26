from fastapi import FastAPI
import uvicorn
from app.api.users import router as users_router
from app.db.database import Base, engine
from app.models.user import User
from app.models.character import Character
from app.models.inventory import Inventory, InventoryItem
from app.api.characters import router as character_router
from app.api.inventory import router as inventory_router
app = FastAPI()
app.include_router(character_router)
app.include_router(inventory_router)
Base.metadata.create_all(bind=engine)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "Мики маус"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)