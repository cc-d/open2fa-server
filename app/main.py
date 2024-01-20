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
from .deps import get_user_totps, get_totp_from_reqhash

import logging as lg
from logfunc import logf


app = FastAPI()


@app.get("/")
async def index_status():
    return {"status": "ok"}


@app.post('/totp', response_model=schemas.TOTP)
@logf(level='INFO', use_print=True)
async def create_totp(
    new_totp: schemas.TOTP, db: Session = Depends(get_db)
) -> schemas.TOTP:
    print(f"new_totp: {new_totp}", '@' * 80)
    lg.info(f"new_totp: {new_totp}")

    lg.info(f"creating new_totp: {new_totp}")
    db_totp = models.TOTP(**new_totp.model_dump())
    db.add(db_totp)
    db.commit()
    db.refresh(db_totp)

    return db_totp


@app.get('/totp', response_model=list[schemas.TOTP])
async def read_totps(
    user_totps: list[schemas.TOTP] = Depends(get_totp_from_reqhash),
) -> list[schemas.TOTP]:
    return user_totps


@app.get('/totp/{enc_secret}', response_model=schemas.TOTP)
async def read_totp(enc_sec: str, user_totps=Depends(get_totp_from_reqhash)):
    totp = next(
        (totp for totp in user_totps if totp.enc_secret == enc_sec), None
    )
    if totp is None:
        raise HTTPException(status_code=404, detail="TOTP not found")
    return totp


@app.delete('/totp/{enc_secret}', response_model=schemas.TOTP)
async def delete_totp(
    enc_sec: str,
    user_totps=Depends(get_totp_from_reqhash),
    db: Session = Depends(get_db),
):
    del_totp = None
    for totp in user_totps:
        if totp.enc_secret == enc_sec:
            del_totp = totp
            break
    if del_totp is None:
        raise HTTPException(status_code=404, detail="TOTP not found")

    db.delete(del_totp)
    db.commit()
    return {"status": "ok"}


@app.get('/openapi.json')
async def get_openapi():
    return app.openapi(
        title="API documentation", version="1.0.0", routes=app.routes
    )
