from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean
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

    subclass: Mapped[str] = mapped_column(default="")
    race: Mapped[str] = mapped_column(default="")
    background: Mapped[str] = mapped_column(default="")
    hp: Mapped[int] = mapped_column(default=10)
    armor_class: Mapped[int] = mapped_column(default=10)
    strength: Mapped[int] = mapped_column(default=10)
    dexterity: Mapped[int] = mapped_column(default=10)
    constitution: Mapped[int] = mapped_column(default=10)
    intelligence: Mapped[int] = mapped_column(default=10)
    wisdom: Mapped[int] = mapped_column(default=10)
    charisma: Mapped[int] = mapped_column(default=10)
    investigation: Mapped[int] = mapped_column(default=0)
    is_dead: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )


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


