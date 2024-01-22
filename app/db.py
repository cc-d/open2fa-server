import os
from . import config

# this next line is required apparently for sqlite
from sqlalchemy.dialects import sqlite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base


conn_args = {'check_same_thread': False} if config.TESTING else {}
engine = create_engine(config.DB_URI, connect_args=conn_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
