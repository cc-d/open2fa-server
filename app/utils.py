from .models import TOTP, User
import logging as lg
from sqlalchemy.orm import Session
from typing import Tuple as T


def addcomref(model: any, db: Session, **kwargs) -> any:
    lg.info(f'Adding {model} with {kwargs}')
    m = model(**kwargs)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def ensure_user(uhash: str, db: Session) -> User:
    """Ensure user exists, if not, create it
    Args:
        uhash (str): User hash
        db (Session): SQLAlchemy session
    Returns:
        User: User instance
    """
    u = db.query(User).filter(User.uhash == uhash).first()
    if u is None:
        lg.info(f'Creating new user for uhash: {uhash}')
        return addcomref(User, db, uhash=uhash)
    return u
