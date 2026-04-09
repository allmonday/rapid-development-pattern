from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
import src.db as db

class Sprint(db.Base):
    __tablename__ = "sprint"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(String(100))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))

    stories: Mapped[list["Story"]] = relationship(lazy="noload")
