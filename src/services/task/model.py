from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import src.db as db

class Task(db.Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    story_id: Mapped[int] = mapped_column(ForeignKey("story.id"))
    estimate: Mapped[int]

    owner: Mapped["User"] = relationship(lazy="noload")
