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
async def push_totps(
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

    u_totp_map = {t.enc_secret: t for t in u.totps}

    new_totps, up_totps = [], []
    for new_totp in new_totp.totps:
        if new_totp.enc_secret in u_totp_map:
            existing_totp = u_totp_map[new_totp.enc_secret]
            if existing_totp.name != new_totp.name:
                lg.info(
                    f'Updating existing TOTP name from {existing_totp.name} to {new_totp.name}'
                )
                existing_totp.name = new_totp.name
                db.add(existing_totp)
                up_totps.append(
                    schemas.TOTPCommon.model_validate(existing_totp.__dict__)
                )
                continue
            lg.info(f'TOTP already exists, skipping: {new_totp}')
            continue
        lg.info(f'Creating new TOTP: {new_totp}')
        new_totp = models.TOTP(
            enc_secret=new_totp.enc_secret,
            name=new_totp.name,
            user=u,
            uhash=u.uhash,
        )
        db.add(new_totp)
        new_totps.append(schemas.TOTPCommon.model_validate(new_totp.__dict__))
        u_totp_map[new_totp.enc_secret] = new_totp

    db.commit()

    return {'user_created': user_created, 'totps': new_totps + up_totps}


@router.get('/totps', response_model=schemas.TOTPPull)
async def pull_totps(
    u: models.User = Depends(get_user_from_reqhash),
) -> list[schemas.TOTP]:
    return schemas.TOTPPull(
        totps=[schemas.TOTP.model_validate(t) for t in u.totps]
    )


@router.delete('/totp/{enc_secret}', response_model=schemas.TOTPDeleteOut)
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
