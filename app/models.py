from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey as FKey,
    Integer as Int,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column as mapcol, relationship as rel
from app import db as _db


class User(_db.Base):
    __tablename__ = 'users'
    uhash: Mapped[str] = mapcol(
        String(255), primary_key=True, index=True, nullable=False
    )
    totps: Mapped[list['TOTP']] = rel(
        "TOTP", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<models.User uhash={self.uhash}>"


class TOTP(_db.Base):
    __tablename__ = 'totps'
    enc_secret: Mapped[str] = mapcol(
        Text, index=True, nullable=False, primary_key=True
    )
    org_name: Mapped[str] = mapcol(
        String(255), nullable=True, default=None, server_default=None
    )
    uhash: Mapped[str] = mapcol(
        String(255),
        FKey('users.uhash', ondelete='CASCADE'),
        index=True,
        nullable=False,
    )
    user: Mapped[User] = rel("User", back_populates="totps")

    def __repr__(self):
        return (
            f"<models.TOTP id={self.id} enc_secret={self.enc_secret} "
            f"org_name={self.org_name}>"
        )
