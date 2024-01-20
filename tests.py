import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app import db as _db
from app import config as cfg


# start app
@pytest.fixture(scope="session")
def client():
    _db.TestBase.metadata.create_all(bind=_db.test_engine)
    with TestClient(app) as c:
        yield c
    _db.TestBase.metadata.drop_all(bind=_db.test_engine)


def test_index_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_totp(client):
    response = client.post(
        "/totp",
        json={
            "enc_secret": cfg.TEST_ENC_SEC,
            "user_hash": cfg.TEST_UID,
            "org_name": cfg.TEST_ORG,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["enc_secret"] == cfg.TEST_ENC_SEC
    assert data["user_hash"] == cfg.TEST_UID
    assert data["org_name"] == cfg.TEST_ORG


def test_read_totps(client):
    response = client.get("/totp")
    assert response.status_code == 200
    totps = response.json()
    assert isinstance(totps, list)


def test_read_totp(client):
    response = client.get(f"/totp/{cfg.TEST_ENC_SEC}")
    assert response.status_code == 200
    totp = response.json()
    assert totp["enc_secret"] == cfg.TEST_ENC_SEC


def test_delete_totp(client):
    response = client.delete(f"/totp/{cfg.TEST_ENC_SEC}")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}

    # Verify that the TOTP is deleted
    response = client.get(f"/totp/{cfg.TEST_ENC_SEC}")
    assert response.status_code == 404
