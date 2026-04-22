from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import src.db as db

class Story(db.Base):
    __tablename__ = "story"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    sprint_id: Mapped[int] = mapped_column(ForeignKey("sprint.id"))

    tasks: Mapped[list["Task"]] = relationship(lazy="noload", order_by="Task.id")
    owner: Mapped["User"] = relationship(lazy="noload")
