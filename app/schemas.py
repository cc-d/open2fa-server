from pydantic import BaseModel


class TOTP(BaseModel):
    enc_secret: str
    user_hash: str
    org_name: str

    class Config:
        orm_mode = True


class TOTPCreate(TOTP):
    user_hash: str
    enc_secret: str
    org_name: str
