import os

DB_URI = os.getenv("DB_URI", "sqlite:///sqlite.db")
TEST_DB_URI = os.getenv("TEST_DB_URI", "sqlite:///pytest.db")

TEST_UID = '4a26e0f1d58048c188324c29ae463101'
TEST_ORG = 'Test Org'
TEST_TOTP = 'JBSWY3DPEHPK3PXP'
TEST_ENC_SEC = 'gAAAAABlq_ia8qJoDt5weWB_BKoOOrhh-FNQHwyVnV0reVIKGH74chN_PCkdWz3MR_TFOzsBqRGCvcpvHf8-f5lNZwkJxwf83_z8hBgQNoDJdiPXUj427jo='
TEST_SEC = 'JBSWY3DPEHPK3PXP'
