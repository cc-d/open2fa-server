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
    name: Opt[str] = None


class TOTP(TOTPCommon):
    uhash: str

    model_config = ConfigDict(from_attributes=True)

    def __repr__(self):
        return default_repr(
            self, repr_format='<{obj_name} {attributes}>', join_attrs_on=' '
        )


class TOTPIn(BaseModel):
    totps: List[TOTPCommon]


class TOTPOut(TOTPCommon):
    name: Union[str, None] = None
    enc_secret: str
    uhash: str


class TOTPCreateOut(BaseModel):
    user_created: bool
    totps: list[TOTPCommon]


class TOTPPull(BaseModel):
    totps: list[TOTPCommon]


class TOTPDeleteOut(BaseModel):
    success: bool = True
