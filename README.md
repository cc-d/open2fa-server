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

`aes_encrypt` is used for encrypting TOTP secrets before storage.

`aes_decrypt` is used for decrypting TOTP secrets when they need to be retrieved.

`gen_user_hash` is used to create truncated sha256 hashes truncated to 32 characters which are used to identify users

`gen_uuid` is used to generate unique identifiers (UUIDs).

## How it works

**THE UUID IS NEVER SENT TO THE SERVER, IT IS ONLY STORED LOCALLY**

LOCAL FLOW

```
open2fa installed -> add/remove/etc keys locally -> generate codes locally
```

SERVER FLOW

```
open2fa cli init -> generate uuid -> store uuid locally ->

keys are encrypted using uuid -> keys are synced to server ->

keys are retrieved from server by another client ->

keys are decrypted using uuid -> codes are generated locally
```

1. **Client Initialization (`open2fa init`):**

   - When a client initializes with the `open2fa` server, it follows these steps:

     a. The client generates a random UUID using the `gen_uuid` function.

     b. This UUID serves as the encryption key for the client's TOTP secrets.

     c. If the key doesn't already exist, it is created and stored locally (e.g., in `~/.open2fa/open2fa.id`).

2. **Storing TOTP Secrets on the Server:**

   - To add a TOTP secret, the client performs the following steps:

     a. The user enters a TOTP secret into the client application.

     b. The client encrypts this TOTP secret using the UUID-based encryption key (created during initialization).

     c. The client sends the encrypted TOTP secret to the `open2fa` server for storage, associating it with the user's UUID.

     d. The server stores the encrypted TOTP secret, linked to the user's UUID.

3. **Retrieving TOTP Secrets from the Server:**

   - When the user wants to retrieve their TOTP secrets for generating one-time passwords, the following happens:

   - The client sends a request to the server, specifying the user's UUID (generated during initialization) or a base58-encoded user ID.

   - The server identifies the user based on the provided UUID or user ID.

   - The server retrieves the encrypted TOTP secrets associated with the user.

   - The server returns the list of encrypted TOTP secrets to the client.

   - The client uses its locally stored UUID-based encryption key to decrypt the TOTP secrets.

4. **Generating One-Time Passwords (TOTPs):**

   - With the decrypted TOTP secrets, the client can now generate one-time passwords (TOTPs) as needed.

   - The client uses the decrypted TOTP secrets to calculate TOTP values based on the current time.

   - These TOTP values are used for two-factor authentication when needed, typically by entering them along with the username and password for a service.
