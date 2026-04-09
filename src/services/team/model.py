from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
import src.db as db

class TeamUser(db.Base):
    __tablename__ = "team_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"))

class Team(db.Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    sprints: Mapped[list["Sprint"]] = relationship(lazy="noload")
    users: Mapped[list["User"]] = relationship(
        secondary=TeamUser.__table__, lazy="noload")
