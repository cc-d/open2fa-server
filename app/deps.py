from fastapi import Depends, FastAPI, HTTPException, Request, status
from logfunc import logf
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import TOTP, User
from . import ex


@logf()
def get_user_from_reqhash(
    req: Request, must_exist: bool = True, db: Session = Depends(get_db)
) -> list[TOTP]:
    uhash = req.headers.get('X-User-Hash', None)
    if uhash is None:
        raise ex.NoUserHashException()
    return get_user_from_hash(uhash, must_exist=must_exist, db=db)


@logf()
def get_user_from_hash(
    uhash: str, must_exist: bool = True, db: Session = Depends(get_db)
) -> list[TOTP]:
    u = (
        db.query(User)
        .select_from(TOTP)
        .join(User.totps)
        .filter(User.uhash == uhash)
        .first()
    )
    if u is None and must_exist:
        raise ex.NoUserFoundException()
    return u
