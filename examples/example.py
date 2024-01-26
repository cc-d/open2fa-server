from cryptography.fernet import Fernet
from base58 import b58decode
from uuid import UUID
from base64 import b64encode, urlsafe_b64decode, urlsafe_b64encode

# Base58-decoded key
base58_uuid = 'DzCfDLQRcUQqD251Q7w79c'

secret = 'I65VU7K5ZQL7WB4E'

# Convert base58 UUID to bytes
key_bytes = b58decode(base58_uuid)

key_b64 = urlsafe_b64encode(key_bytes.hex().encode())
print(key_b64, 'key_b64', type(key_b64), 'hex', key_bytes.hex(), sep=' || ')


key_base64 = b64encode(UUID(bytes=key_bytes).hex.encode())

# Initialize a Fernet key from the base64 encoded key
fernet_key = Fernet(key_base64)

# Encrypt the secret
encrypted_secret = fernet_key.encrypt(secret.encode())

print('encrypted_secret', encrypted_secret)

# Decrypt the secret
decrypted_secret = fernet_key.decrypt(encrypted_secret)

print('decrypted_secret', decrypted_secret)
