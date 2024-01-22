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
from .deps import get_user_from_reqhash, get_user_from_hash
from . import ex

import logging as lg
from logfunc import logf

_db.Base.metadata.create_all(bind=_db.engine)

app = FastAPI()


@app.get("/")
async def index_status():
    return {"status": "ok"}


@app.post('/totps', response_model=schemas.TOTPCreateOut)
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

    for totp in u.totps:
        if totp.enc_secret == new_totp.enc_secret:
            raise ex.TOTPExistsException()

    _totp = (
        db.query(models.TOTP)
        .filter(
            models.TOTP.enc_secret == new_totp.enc_secret,
            models.TOTP.org_name == new_totp.org_name,
        )
        .first()
    )

    if _totp is not None:
        lg.info('TOTP with enc_secret already exists for another user')
        _totp.users.append(u)
        created = False
    else:
        lg.info('No other users with TOTP found, creating new TOTP')
        _totp = models.TOTP(
            enc_secret=new_totp.enc_secret,
            org_name=new_totp.org_name,
            users=[u],
        )
        created = True

    db.add(_totp)
    db.commit()

    return schemas.TOTPCreateOut(
        enc_secret=_totp.enc_secret,
        org_name=_totp.org_name,
        newly_created=created,
        user_created=user_created,
    )


@app.get('/totps', response_model=list[schemas.TOTPOut])
async def get_user_totps(
    u: models.User = Depends(get_user_from_reqhash),
) -> list[schemas.TOTP]:
    return u.totps


@app.get('/totps/{enc_secret}', response_model=schemas.TOTPOut)
async def read_totp(
    enc_secret: str, u: models.User = Depends(get_user_from_reqhash)
):
    for totp in u.totps:
        if totp.enc_secret == enc_secret:
            return totp
    raise ex.NoTOTPFoundException()


@app.delete('/totp/{enc_secret}', response_model=schemas.TOTPDeleteOut)
async def delete_totp(
    enc_secret: str,
    u: models.User = Depends(get_user_from_reqhash),
    db: Session = Depends(get_db),
):
    utotp = next((t for t in u.totps if t.enc_secret == enc_secret), None)
    if utotp is None:
        raise ex.NoTOTPFoundException()
    utotp.users.remove(u)

    if len(utotp.users) == 0:
        lg.info('No other users with TOTP found, deleting TOTP')
        db.delete(utotp)
        deleted = True
    else:
        deleted = False

    db.commit()
    return schemas.TOTPDeleteOut(deleted_from_db=deleted)


@app.get('/openapi.json')
async def get_openapi():
    return app.openapi(
        title="API documentation", version="1.0.0", routes=app.routes
    )
