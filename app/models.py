# app/models.py
from sqlalchemy import Column, String, Text
from .db import Base


class TOTP(Base):
    __tablename__ = "totps"
    enc_secret = Column(Text, primary_key=True, index=True, nullable=False)
    user_hash = Column(String(255), index=True, nullable=False)
    org_name = Column(String(255), index=True, nullable=True)

    def __repr__(self):
        return (
            f"<TOTP enc_secret={self.enc_secret[:3]}..."
            f" user_hash={self.user_hash[:3]}... org_name={self.org_name}>"
        )
