from pydantic import BaseModel, ConfigDict
from typing import Optional as Opt


class TOTP(BaseModel):
    enc_secret: str
    user_hash: str
    org_name: Opt[str] = None

    def __repr__(self):
        return (
            f"<PYD TOTP enc_secret={self.enc_secret[:3]}..."
            f" user_hash={self.user_hash[:3]}... org_name={self.org_name}>"
        )
