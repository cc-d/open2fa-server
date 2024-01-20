import os
from . import models
from . import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

engine = create_engine(config.DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

test_engine = create_engine(config.TEST_DB_URI)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)
TestBase = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
