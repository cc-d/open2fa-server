from fastapi import Depends, FastAPI, HTTPException, Request, status
from logfunc import logf
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from .db import get_db
from .models import TOTP, User
from . import ex
from typing import Optional as Opt, Union as U


@logf()
def get_user_from_reqhash(
    req: Request, must_exist: bool = True, db: Session = Depends(get_db)
) -> U[User, None]:
    uhash = req.headers.get('X-User-Hash', None)
    if uhash is None:
        raise ex.NoUserHashException()
    return get_user_from_hash(uhash, must_exist=must_exist, db=db)


@logf()
def get_user_from_hash(
    uhash: str, must_exist: bool = True, db: Session = Depends(get_db)
) -> U[User, None]:
    u = (
        db.query(User)
        .filter(User.uhash == uhash)
        .options(selectinload(User.totps))
        .first()
    )
    if u is None and must_exist:
        raise ex.NoUserFoundException()
    return u
