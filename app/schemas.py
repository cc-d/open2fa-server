from pydantic import BaseModel, ConfigDict
from typing import Optional as Opt, List, Union
from pyshared import truncstr, default_repr


class User(BaseModel):
    uhash: str
    totps: list['TOTP'] = []

    model_config = ConfigDict(from_attributes=True)

    def __repr__(self):
        return f'<schemas.User uhash={truncstr(self.uhash)}>'


class TOTPCommon(BaseModel):
    enc_secret: str
    org_name: Opt[str] = None


class TOTP(TOTPCommon):
    id: int
    users: User

    model_config = ConfigDict(from_attributes=True)

    def __repr__(self):
        return (
            '<schemas.TOTP '
            f'id={self.id} enc_secret={truncstr(self.enc_secret)} '
            f'org_name={self.org_name}>'
        )


class TOTPIn(BaseModel):
    totps: List[TOTPCommon]


class TOTPOut(TOTPCommon):
    org_name: Union[str, None] = None
    enc_secret: str
    uhash: str


class TOTPCreateOut(BaseModel):
    user_created: bool
    totps: list[TOTPCommon]


class TOTPDeleteOut(BaseModel):
    success: bool = True
