# open2fa-server

api/webui for open2fa

https://github.com/cc-d/open2fa/blob/main/README.md

# Testing

As of 2024-01-21, just finished the tests today.

```bash
tests.py::test_index_status PASSED
tests.py::test_no_user_hash PASSED
tests.py::test_no_user_found PASSED
tests.py::test_create_totp_no_org PASSED
tests.py::test_user_exists PASSED
tests.py::test_multiple_user_same_totp PASSED
tests.py::test_list_totps PASSED
tests.py::test_delete_totp PASSED
tests.py::test_totp_create_exists PASSED
tests.py::test_no_totp_for_user_with_enc_secret PASSED

---------- coverage: platform darwin, python 3.11.7-final-0 ----------
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py       0      0   100%
app/config.py         6      0   100%
app/db.py            14      0   100%
app/deps.py          19      0   100%
app/ex.py            13      0   100%
app/main.py          69      2    97%   105, 121
app/models.py        18      1    94%   47
app/schemas.py       27      2    93%   13, 28
-----------------------------------------------
TOTAL               166      5    97%

```
