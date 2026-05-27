from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from app.db.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str]

    class_name: Mapped[str]

    level: Mapped[int] = mapped_column(
        default=1
    )

    xp: Mapped[int] = mapped_column(
        default=0
    )

    route: Mapped[str]


    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    owner = relationship(
        "User",
        back_populates="characters"
    )

    inventory = relationship(
        "Inventory",
        back_populates="character",
        uselist=False,
        cascade="all, delete-orphan"
    )


