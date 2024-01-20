from .models import TOTP

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status, Request
from .db import get_db


def get_user_totps(uhash: str, db: Session = Depends(get_db)) -> list[TOTP]:
    return list(db.query(TOTP).filter(TOTP.user_hash == uhash).all())


def get_totp_from_reqhash(
    req: Request, db: Session = Depends(get_db)
) -> list[TOTP]:
    print(req.headers, req.headers.get('X-User-Hash', None), '@' * 100)
    uhash = req.headers.get('X-User-Hash', None)
    if uhash is None:
        raise HTTPException(
            status_code=401, detail="Missing X-User-Hash header"
        )
    return get_user_totps(uhash, db)
