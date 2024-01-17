from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from . import models
from .schemas import TOTP
from .db import get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request
from .deps import get_user_totps, get_totp_from_reqhash

import logging as lg

app = FastAPI()


@app.post('/totp', response_model=TOTP)
async def create_totp(
    new_totp: TOTP,
    user_totps=Depends(get_totp_from_reqhash),
    db: Session = Depends(get_db),
) -> TOTP:
    lg.info(f"new_totp: {new_totp}")
    if any(totp.enc_secret == new_totp.enc_secret for totp in user_totps):
        lg.info(f"dupicate totp: {new_totp}")
        raise HTTPException(
            status_code=400, detail="TOTP with this enc_secret already exists"
        )
    lg.info(f"creating new_totp: {new_totp}")
    db_totp = models.TOTP(**new_totp.model_dump())

    return db_totp


@app.get('/totp', response_model=List[TOTP])
async def read_totps(
    user_totps=Depends(get_totp_from_reqhash), db: Session = Depends(get_db)
) -> List[TOTP]:
    return user_totps


@app.get('/totp/{enc_secret}', response_model=TOTP)
async def read_totp(
    enc_sec: str,
    user_totps=Depends(get_totp_from_reqhash),
    db: Session = Depends(get_db),
):
    totp = next(
        (totp for totp in user_totps if totp.enc_secret == enc_sec), None
    )
    if totp is None:
        raise HTTPException(status_code=404, detail="TOTP not found")
    return totp


@app.delete('/totp/{enc_secret}', response_model=TOTP)
async def delete_totp(
    enc_sec: str,
    user_totps=Depends(get_totp_from_reqhash),
    db: Session = Depends(get_db),
):
    totp = next(
        (totp for totp in user_totps if totp.enc_secret == enc_sec), None
    )
    if totp is None:
        raise HTTPException(status_code=404, detail="TOTP not found")
    db.delete(totp)
    db.commit()
    return totp
