from sqlalchemy import Column, String, Text
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from app import db as _db


class TOTP(_db.Base):
    __tablename__ = 'totps'
    enc_secret: Mapped[str] = mapped_column(
        Text, primary_key=True, index=True, nullable=False
    )
    user_hash: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    org_name: Mapped[str] = mapped_column(
        String(255), nullable=True, default=None, server_default=None
    )

    def __repr__(self):
        return (
            f"<TOTP enc_secret={self.enc_secret[:3]}..."
            f" user_hash={self.user_hash[:3]}... org_name={self.org_name}>"
        )


_db.Base.metadata.create_all(bind=_db.engine)
