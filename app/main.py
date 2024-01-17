from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from . import models
from . import schemas
from .db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_totp(
    user_hash: str, totp: schemas.TOTPCreate, db: Session = Depends(get_db)
):
    """Create a new TOTP record for a specific user.

    Args:
        user_hash (str): The user's unique hash.
        totp (schemas.TOTPCreate): The TOTP data to create.

    Returns:
        schemas.TOTPCreate: The created TOTP record.
    """
    db_totp = models.TOTP(user_hash=user_hash, **totp.dict())
    db.add(db_totp)
    db.commit()
    db.refresh(db_totp)
    return db_totp


async def read_totps(user_hash: str, db: Session = Depends(get_db)):
    """Get all TOTP records for a specific user.

    Args:
        user_hash (str): The user's unique hash.

    Returns:
        List[schemas.TOTPCreate]: List of TOTP records for the user.
    """
    totps = (
        db.query(models.TOTP).filter(models.TOTP.user_hash == user_hash).all()
    )
    return totps


async def read_totp(
    user_hash: str, enc_secret: str, db: Session = Depends(get_db)
):
    """Get a single TOTP record by enc_secret for a specific user.

    Args:
        user_hash (str): The user's unique hash.
        enc_secret (str): The encrypted secret of the TOTP.

    Returns:
        schemas.TOTPCreate: The requested TOTP record.
    """
    totp = (
        db.query(models.TOTP)
        .filter(
            models.TOTP.user_hash == user_hash,
            models.TOTP.enc_secret == enc_secret,
        )
        .first()
    )
    if totp is None:
        raise HTTPException(status_code=404, detail="TOTP not found")
    return totp


async def delete_totp(
    user_hash: str, enc_secret: str, db: Session = Depends(get_db)
):
    """Delete a TOTP record by enc_secret for a specific user.

    Args:
        user_hash (str): The user's unique hash.
        enc_secret (str): The encrypted secret of the TOTP.

    Returns:
        schemas.TOTPCreate: The deleted TOTP record.
    """
    totp = (
        db.query(models.TOTP)
        .filter(
            models.TOTP.user_hash == user_hash,
            models.TOTP.enc_secret == enc_secret,
        )
        .first()
    )
    if totp is None:
        raise HTTPException(status_code=404, detail="TOTP not found")
    db.delete(totp)
    db.commit()
    return totp
