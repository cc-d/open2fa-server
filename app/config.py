import os

DB_URI = os.getenv("DB_URI", "sqlite:///sqlite.db")
TEST_DB_URI = os.getenv("TEST_DB_URI", "sqlite:///:memory:")
SQLALCHEMY_DATABASE_URL = DB_URI
