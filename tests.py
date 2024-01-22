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
    with TestClient(app) as client:
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
        '/totps', headers={'X-User-Hash': _uid}, json={'enc_secret': _sec}
    )
    assert r.status_code == 200
    assert r.json()['org_name'] is None


def test_user_exists(client):
    _uid = _testuuid()
    r = client.post(
        '/totps',
        headers={'X-User-Hash': _uid},
        json={'enc_secret': ranstr(32)},
    )
    assert r.status_code == 200
    assert r.json()['user_created'] == True

    r = client.post(
        '/totps',
        headers={'X-User-Hash': _uid},
        json={'enc_secret': ranstr(32)},
    )
    assert r.status_code == 200
    assert r.json()['user_created'] == False


def test_multiple_user_same_totp(client):
    _sec, _org = ranstr(32), ranstr(32)
    uids = [_testuuid() for _ in range(2)]
    for _uuid in uids:
        r = client.post(
            '/totps',
            headers={'X-User-Hash': _uuid},
            json={'enc_secret': _sec, 'org_name': _org},
        )
        assert r.status_code == 200
        assert r.json()['org_name'] == _org
        assert r.json()['enc_secret'] == _sec

        assert r.json()['user_created'] == True
        if _uuid == uids[0]:
            assert r.json()['newly_created'] == True
        else:
            assert r.json()['newly_created'] == False


def test_list_totps(client):
    _uid = _testuuid()
    _totps = [ranstr(32) for _ in range(2)]
    for _totp in _totps:
        r = client.post(
            '/totps', headers={'X-User-Hash': _uid}, json={'enc_secret': _totp}
        )
    listed_totps = client.get('/totps', headers={'X-User-Hash': _uid}).json()
    assert len(listed_totps) == len(_totps)

    r = client.get(f'/totps/{_totps[0]}', headers={'X-User-Hash': _uid})
    assert r.status_code == 200
    assert r.json()['enc_secret'] == _totps[0]


def test_delete_totp(client):
    uids = [_testuuid() for _ in range(2)]
    totp_sec = ranstr(32)
    for _uid in uids:
        r = client.post(
            '/totps',
            headers={'X-User-Hash': _uid},
            json={'enc_secret': totp_sec},
        )
    r = client.delete(f'/totp/{totp_sec}', headers={'X-User-Hash': uids[0]})
    assert r.status_code == 200
    assert r.json()['deleted_from_db'] == False
    r = client.delete(f'/totp/{totp_sec}', headers={'X-User-Hash': uids[1]})
    assert r.status_code == 200
    assert r.json()['deleted_from_db'] == True


def test_totp_create_exists(client):
    _uid, _totp = _testuuid(), ranstr(32)
    r = client.post(
        '/totps', headers={'X-User-Hash': _uid}, json={'enc_secret': _totp}
    )
    r = client.post(
        '/totps', headers={'X-User-Hash': _uid}, json={'enc_secret': _totp}
    )
    assert r.status_code == 409


def test_no_totp_for_user_with_enc_secret(client):
    _uid, _totp = _testuuid(), ranstr(32)
    r = client.post(
        '/totps', headers={'X-User-Hash': _uid}, json={'enc_secret': _totp}
    )
    r = client.get(f'/totps/{ranstr(32)}', headers={'X-User-Hash': _uid})
    assert r.status_code == 404
