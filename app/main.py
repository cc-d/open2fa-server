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

import logging as lg
from logfunc import logf

_db.Base.metadata.create_all(bind=_db.engine)

app = FastAPI()

router = APIRouter(prefix="/api/v1")


@router.get("/")
async def index_status():
    return {"status": "ok"}


@router.post('/totps', response_model=schemas.TOTPCreateOut)
@logf(log_level=lg.INFO)
async def create_totp(
    new_totp: schemas.TOTPIn, request: Request, db: Session = Depends(get_db)
) -> schemas.TOTP:
    u = get_user_from_reqhash(request, must_exist=False, db=db)

    user_created = False
    if u is None:
        lg.info('No user found for given uhash header, creating...')
        u = models.User(uhash=request.headers.get('X-User-Hash'))
        db.add(u)
        db.commit()
        db.refresh(u)
        user_created = True

    if set([t.enc_secret for t in new_totp.totps]) == set(
        [t.enc_secret for t in u.totps]
    ):
        raise ex.TOTPExistsException()

    new_totps = []
    for _totp in new_totp.totps:
        _org = None if _totp.name is None else _totp.name
        _totp = models.TOTP(enc_secret=_totp.enc_secret, name=_org, user=u)
        db.add(_totp)

        new_totps.append(
            schemas.TOTPOut(
                enc_secret=_totp.enc_secret, name=_totp.name, uhash=u.uhash
            )
        )

    db.commit()

    return schemas.TOTPCreateOut(user_created=user_created, totps=new_totps)


@router.get('/totps', response_model=list[schemas.TOTPOut])
async def get_user_totps(
    u: models.User = Depends(get_user_from_reqhash),
) -> list[schemas.TOTP]:
    return u.totps


@router.get('/totps/{enc_secret}', response_model=schemas.TOTPOut)
async def read_totp(
    enc_secret: str, u: models.User = Depends(get_user_from_reqhash)
):
    for totp in u.totps:
        if totp.enc_secret == enc_secret:
            return totp
    raise ex.NoTOTPFoundException()


@router.delete('/totp/{enc_secret}', response_model=schemas.TOTPDeleteOut)
async def delete_totp(
    enc_secret: str,
    u: models.User = Depends(get_user_from_reqhash),
    db: Session = Depends(get_db),
):
    utotp = next((t for t in u.totps if t.enc_secret == enc_secret), None)
    if utotp is None:
        raise ex.NoTOTPFoundException()
    u.totps.remove(utotp)
    db.commit()
    return schemas.TOTPDeleteOut()


app.include_router(router)
