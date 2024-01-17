from .models import TOTP

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status, Request

from .schemas import TOTP as TOTPSchema


async def get_user_totps(uhash: str, db: Session) -> list[TOTP]:
    return db.query(TOTP).filter(TOTP.user_hash == uhash).all()


async def get_totp_from_reqhash(req: Request, db: Session) -> list[TOTP]:
    uhash = req.headers.get('X-User-Hash', None)
    if uhash is None:
        raise HTTPException(
            status_code=401, detail="Missing X-User-Hash header"
        )
    return get_user_totps(uhash, db)
