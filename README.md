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

Here's an explanation of how the hash/secret mechanisms work in the provided code:

1. **Encryption and Decryption Functions (`aes_encrypt` and `aes_decrypt`):**

   - These functions are used for encrypting and decrypting TOTP secrets.
   - `aes_encrypt`: It takes a TOTP secret (`data`) and an encryption key (`enc_key`) as input.
     - It first pads the input data using PKCS7 padding.
     - Then, it creates an AES cipher using the encryption key and ECB mode.
     - The padded data is encrypted using this cipher.
     - Finally, the encrypted data is base58-encoded and returned as a string.
   - `aes_decrypt`: It takes an encrypted TOTP secret (`enc_data`) and the encryption key (`enc_key`) as input.
     - It decodes the base58-encoded encrypted data.
     - Then, it creates an AES cipher using the encryption key and ECB mode.
     - The encrypted data is decrypted using this cipher.
     - PKCS7 padding is removed from the decrypted data.
     - The decrypted data is returned as a string.

2. **User Hash Generation (`gen_user_hash`):**

   - This function generates a 32-character SHA256 hash from a base58-encoded user ID (`b58_uid`).
   - The hash is used to identify users in the system.

3. **UUID Generation (`gen_uuid`):**

   - This function generates a random UUID and returns it as a base58-encoded string.
   - It can be used for generating unique identifiers.

4. **Overall Usage:**
   - `aes_encrypt` is used to encrypt TOTP secrets before storing them.
   - `aes_decrypt` is used to decrypt TOTP secrets when they need to be retrieved.
   - `gen_user_hash` is used to create user hashes based on user IDs.
   - `gen_uuid` is used to generate unique identifiers (UUIDs).

These mechanisms ensure that TOTP secrets are stored securely and can be decrypted when needed, using an encryption key associated with a specific user or organization.

# flow

Understood, if encryption also happens on the client, and the server never sees the UUID, here's a revised high-level overview of how the system works:

1. **UUID and UUID Hash Creation on the Client (User's Device):**

   - When a user sets up the system for the first time, they provide their UUID (Universally Unique Identifier).
   - The user's device generates a hash of the UUID (UUID Hash). This hash is unique for each user.

2. **Client-Side Encryption of User-Saved TOTP Secrets:**

   - The user generates and saves their TOTP secrets locally on their device.
   - The user's device also performs encryption on the TOTP secrets using the UUID Hash as the encryption key.

3. **Secure Remote Synchronization Request from Client:**

   - The client initiates a secure remote synchronization request with the server.
   - This request typically includes the user's UUID Hash but not the actual UUID for added security.

4. **Server Retrieves Encrypted TOTP Secrets Using UUID Hash:**

   - The server receives the UUID Hash as part of the synchronization request.
   - The server uses the received UUID Hash to retrieve the encrypted user-saved TOTP secrets associated with that hash.

5. **Secure Transfer of Encrypted TOTP Secrets:**

   - The server sends the encrypted TOTP secrets back to the client securely. The server never sees the actual UUID.

6. **Client's Secure TOTP Secret Decryption:**

   - The client's device uses the UUID Hash as the decryption key to decrypt the received TOTP secrets.

7. **TOTP Code Generation on the Client:**

   - When the client needs to use a TOTP code for authentication or other purposes, it generates the TOTP code locally using the stored and decrypted TOTP secrets.

In this updated workflow, the encryption of TOTP secrets also happens on the client, and the server never has access to the actual UUID. The server operates based on the UUID Hash for security, ensuring that it cannot identify users by their UUID, enhancing privacy and security.
