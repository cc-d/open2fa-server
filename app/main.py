from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from .db import get_db
from app import db as _db
from app import models
from app import schemas
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.routing import APIRouter
from .deps import get_user_from_reqhash, get_user_from_hash
from . import ex
from .utils import addcomref, ensure_user

import logging as lg
from logfunc import logf

_db.Base.metadata.create_all(bind=_db.engine)

app = FastAPI()

router = APIRouter(prefix="/api/v1")


@router.get("/")
async def index_status():
    return {"status": "ok"}


@router.post('/totps', response_model=schemas.TOTPCreateOut)
@logf()
async def push_totps(
    new_totp: schemas.TOTPIn, request: Request, db: Session = Depends(get_db)
) -> schemas.TOTP:
    db_user = get_user_from_reqhash(request, must_exist=False, db=db)

    user_created = False
    if db_user is None:
        db_user = ensure_user(request.headers['X-User-Hash'], db)
        user_created = True

    u_totp_map = {t.enc_secret: t for t in db_user.totps}

    for new_totp in new_totp.totps:
        _enc_sec = new_totp.enc_secret
        if _enc_sec in u_totp_map:
            u_totp_map[_enc_sec].name = new_totp.name
            db.add(u_totp_map[_enc_sec])
            continue
        new_totp = models.TOTP(**new_totp.__dict__, uhash=db_user.uhash)
        u_totp_map[_enc_sec] = new_totp

    uniq_totps = []
    for k, v in u_totp_map.items():
        db.add(v)
        uniq_totps.append(schemas.TOTP.model_validate(v))

    db.commit()

    return {'user_created': user_created, 'totps': uniq_totps}


@router.get('/totps', response_model=schemas.TOTPPull)
@logf()
async def pull_totps(
    u: models.User = Depends(get_user_from_reqhash),
) -> list[schemas.TOTP]:
    return schemas.TOTPPull(
        totps=[schemas.TOTP.model_validate(t) for t in u.totps]
    )


@router.delete('/totp/{enc_secret}', response_model=schemas.TOTPDeleteOut)
@logf()
async def delete_totp(
    enc_secret: str,
    u: models.User = Depends(get_user_from_reqhash),
    db: Session = Depends(get_db),
):
    utotp = next((t for t in u.totps if t.enc_secret == enc_secret), None)
    if utotp is None:
        raise ex.NoTOTPFoundException()
    db.delete(utotp)
    db.commit()
    return schemas.TOTPDeleteOut()


app.include_router(router)
