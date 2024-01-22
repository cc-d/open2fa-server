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

# how it works

The generate_base58_uuid() function generates a random UUID, converts it to bytes, and then encodes it as a Base58 string. This UUID is used as the encryption key.
Encryption:

The encrypt function takes the data (e.g., a secret message) and the encryption key.
It first pads the data to ensure it's a multiple of the block size (128 bits or 16 bytes for AES).
Then, it encodes the encryption key from Base58 to bytes.
It creates an AES cipher object with the encryption key and the ECB mode (Electronic Codebook mode).
The data is encrypted using the cipher object.
The resulting ciphertext is Base64-encoded to ensure it can be stored as a string.
Decryption:

The decrypt function takes the encrypted string and the encryption key.
It decodes the encryption key from Base58 to bytes.
The Base64-encoded ciphertext is decoded back to bytes.
An AES cipher object is created using the encryption key and ECB mode.
The ciphertext is decrypted using the cipher object.
The decrypted data is unpadded to remove any padding added during encryption.
Finally, the decrypted data is decoded back to a string.
