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


# assosciation table
user_totp_assoc = Table(
    'user_totp_assoc',
    _db.Base.metadata,
    Column('uhash', String(255), FKey('users.uhash')),
    Column('id', Int, FKey('totps.id')),
)


class User(_db.Base):
    __tablename__ = 'users'
    uhash: Mapped[str] = mapcol(
        String(255), primary_key=True, index=True, nullable=False
    )
    totps: Mapped[list['TOTP']] = rel(
        "TOTP", back_populates="users", secondary="user_totp_assoc"
    )

    def __repr__(self):
        return f"<models.User uhash={self.uhash}>"


class TOTP(_db.Base):
    __tablename__ = 'totps'
    id: Mapped[int] = mapcol(Int, primary_key=True, index=True, nullable=False)
    enc_secret: Mapped[str] = mapcol(Text, index=True, nullable=False)
    org_name: Mapped[str] = mapcol(
        String(255), nullable=True, default=None, server_default=None
    )
    users: Mapped[list[User]] = rel(
        'User', secondary="user_totp_assoc", back_populates="totps"
    )

    def __repr__(self):
        return (
            f"<models.TOTP id={self.id} enc_secret={self.enc_secret} "
            f"org_name={self.org_name}>"
        )
