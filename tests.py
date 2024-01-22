import os
from functools import wraps
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from logfunc import logf
from pyshared import ranstr
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app import config as cfg
from app.main import app
from app import db as _db


def _testuuid():
    return str(uuid4()).replace('-', '')


@pytest.fixture(scope='session')
def create_db():
    _db.Base.metadata.create_all(bind=_db.engine)
    yield
    _db.Base.metadata.drop_all(bind=_db.engine)
    if os.path.exists(
        cfg.SQLITE_DB_PATH and cfg.SQLITE_DB_PATH.endswith('test.db')
    ):
        os.remove(cfg.SQLITE_DB_PATH)


@pytest.fixture(scope='session')
def client(create_db):
    with TestClient(app, base_url='http://test/api/v1') as client:
        yield client


def test_index_status(client):
    r = client.get('/')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_no_user_hash(client):
    r = client.get('/totps')
    assert r.status_code == 400


def test_no_user_found(client):
    r = client.get('/totps', headers={'X-User-Hash': _testuuid()})
    assert r.status_code == 404


def test_create_totp_no_org(client):
    _sec, _uid = ranstr(32), _testuuid()
    r = client.post(
        '/totps',
        headers={'X-User-Hash': _uid},
        json={'totps': [{'enc_secret': _sec}]},
    )
    assert r.status_code == 200
    for _totp in r.json()['totps']:
        assert _totp['enc_secret'] == _sec
        assert _totp['org_name'] is None


def test_user_exists(client):
    _uid = _testuuid()
    r = client.post(
        '/totps',
        headers={'X-User-Hash': _uid},
        json={'totps': [{'enc_secret': ranstr(32)}]},
    )
    assert r.status_code == 200
    assert r.json()['user_created'] == True

    r = client.post(
        '/totps',
        headers={'X-User-Hash': _uid},
        json={'totps': [{'enc_secret': ranstr(32)}]},
    )
    assert r.status_code == 200
    assert r.json()['user_created'] == False


def test_list_totps(client):
    _uid = _testuuid()
    _totps = [{'enc_secret': ranstr(32)} for _ in range(5)]
    r = client.post(
        '/totps', headers={'X-User-Hash': _uid}, json={'totps': _totps}
    )
    listed_totps = client.get('/totps', headers={'X-User-Hash': _uid}).json()
    assert len(listed_totps) == len(_totps)

    r = client.get(f'/totps', headers={'X-User-Hash': _uid})
    assert r.status_code == 200
    assert len(r.json()) == len(_totps)


def test_delete_totp(client):
    uuid = _testuuid()
    totp_sec = ranstr(32)

    r = client.post(
        '/totps',
        headers={'X-User-Hash': uuid},
        json={'totps': [{'enc_secret': totp_sec}]},
    )
    r = client.delete(f'/totp/{totp_sec}', headers={'X-User-Hash': uuid})
    assert r.status_code == 200


def test_no_totp_for_user_with_enc_secret(client):
    _uid, _totp = _testuuid(), ranstr(32)
    r = client.post(
        '/totps',
        headers={'X-User-Hash': _uid},
        json={'totps': [{'enc_secret': _totp}]},
    )
    r = client.get(f'/totps/{ranstr(32)}', headers={'X-User-Hash': _uid})
    assert r.status_code == 404
