import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app import db as _db
from app import config as cfg
from uuid import uuid4
from pyshared import ranstr
from functools import wraps
from unittest.mock import patch
from logfunc import logf


def _testuuid():
    return str(uuid4()).replace('-', '')


TEST_UID = _testuuid()
TEST_ORG = 'Test Org'
TEST_TOTP = 'JBSWY3DPEHPK3PXP'
# TEST_ENC_SEC = 'gAAAAABlq_ia8qJoDt5weWB_BKoOOrhh-FNQHwyVnV0reVIKGH74chN_PCkdWz3MR_TFOzsBqRGCvcpvHf8-f5lNZwkJxwf83_z8hBgQNoDJdiPXUj427jo='
TEST_ENC_SEC = ranstr(32)
TEST_SEC = 'JBSWY3DPEHPK3PXP'


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(cfg.TEST_DB_URI)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db():
    # Create the in-memory SQLite database for each test
    engine = create_engine(cfg.TEST_DB_URI)
    _db.Base.metadata.create_all(bind=engine)

    yield engine

    _db.Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(
        app, base_url="http://testserver", headers={'X-User-Hash': TEST_UID}
    ) as client:
        yield client


def test_index_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_totp(client):
    response = client.post(
        "/totp",
        json={
            "enc_secret": TEST_ENC_SEC,
            "user_hash": TEST_UID,
            "org_name": TEST_ORG,
        },
    )
    print(response.json(), response.status_code, response.text)
    assert response.status_code == 200
    data = response.json()
    assert data["enc_secret"] == TEST_ENC_SEC
    assert data["user_hash"] == TEST_UID
    assert data["org_name"] == TEST_ORG


def test_read_totps(client):
    response = client.get("/totp")
    assert response.status_code == 200
    totps = response.json()
    assert isinstance(totps, list)


def test_read_totp(client):
    client.get = logf(level='INFO', use_print=True)(client.get)

    response = client.get(f"/totp/{TEST_ENC_SEC}")
    assert response.status_code == 200
    totp = response.json()
    assert totp["enc_secret"] == TEST_ENC_SEC


def test_delete_totp(client):
    response = client.delete(f"/totp/{TEST_ENC_SEC}")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}

    # Verify that the TOTP is deleted
    response = client.get(f"/totp/{TEST_ENC_SEC}")
    assert response.status_code == 404
