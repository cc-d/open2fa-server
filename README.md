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
Name    Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py  0 0   100%
app/config.py    6 0   100%
app/db.py  14 0   100%
app/deps.py19 0   100%
app/ex.py  13 0   100%
app/main.py69 2    97%   105, 121
app/models.py   18 1    94%   47
app/schemas.py  27 2    93%   13, 28
-----------------------------------------------
TOTAL166 5    97%

```

# Security

In the provided code, the security mechanisms are described as follows:

1. **Encryption and Decryption Functions (`aes_encrypt` and `aes_decrypt`):**

   - `aes_encrypt` function is used to encrypt TOTP secrets. It takes a TOTP secret (`data`) and an encryption key (`enc_key`) as input.
   - It performs PKCS7 padding on the input data.
   - An AES cipher is created using the encryption key and ECB mode.
   - The padded data is encrypted using this cipher.
   - Finally, the encrypted data is base58-encoded and returned as a string.

   - `aes_decrypt` function is used to decrypt TOTP secrets. It takes an encrypted TOTP secret (`enc_data`) and the encryption key (`enc_key`) as input.
   - It decodes the base58-encoded encrypted data.
   - An AES cipher is created using the encryption key and ECB mode.
   - The encrypted data is decrypted using this cipher.
   - PKCS7 padding is removed from the decrypted data.
   - The decrypted data is returned as a string.

2. **User Hash Generation (`gen_user_hash`):**

   - This function generates a 32-character SHA256 hash from a base58-encoded user ID (`b58_uid`).
   - The hash is used to uniquely identify users in the system.

3. **UUID Generation (`gen_uuid`):**

   - This function generates a random UUID and returns it as a base58-encoded string.
   - It can be used for creating unique identifiers.

4. **Overall Usage:**
   - `aes_encrypt` is used for encrypting TOTP secrets before storage.
   - `aes_decrypt` is used for decrypting TOTP secrets when they need to be retrieved.
   - `gen_user_hash` is used to create user hashes based on user IDs.
   - `gen_uuid` is used to generate unique identifiers (UUIDs).

**Security Workflow:**

```
[CLIENT DEVICE]

1. cli init -> generate uuid -> create UUID Hash
2. encrypt TOTP Secrets
3. send secure request to server

[AFTER CLIENT SENDS ENCRYPTED TOTP SECRETS TO SERVER]

4. client identifies using UUID Hash
5. retrieve encrypted TOTP Secrets from server
6. decrypt TOTP Secrets -> generate TOTP Code
```
