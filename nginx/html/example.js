// Base58 character set (excluding characters that can be visually confused)
const base58Chars =
  '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

// Use '_' as the padding character
const paddingChar = '~';

// Encode a byte array as a Base58 string
function encodeBase58(bytesOrString) {
  if (typeof bytesOrString === 'string') {
    bytes = new TextEncoder().encode(bytesOrString);
  } else {
    bytes = bytesOrString;
  }

  let result = '';
  let leadingZeros = 0;

  // Count leading zeros
  for (let i = 0; i < bytes.length; i++) {
    if (bytes[i] === 0) {
      leadingZeros++;
    } else {
      break;
    }
  }

  // Convert to base58
  let value = BigInt(
    '0x' + Array.from(bytes, (byte) => byte.toString(16)).join('')
  );
  while (value > 0n) {
    const remainder = Number(value % 58n);
    result = base58Chars[remainder] + result;
    value = value / 58n;
  }

  // Add leading '_' characters
  for (let i = 0; i < leadingZeros; i++) {
    result = paddingChar + result;
  }

  return result;
}

// Decode a Base58 string into a byte array
function decodeBase58(str) {
  let leadingZeros = 0;

  // Count leading '_' characters
  for (let i = 0; i < str.length; i++) {
    if (str[i] === paddingChar) {
      leadingZeros++;
    } else {
      break;
    }
  }

  // Remove leading '_' characters
  const cleanStr = str.substring(leadingZeros);

  // Convert to base10
  let value = BigInt('0');
  for (let i = cleanStr.length - 1; i >= 0; i--) {
    const charIndex = base58Chars.indexOf(cleanStr[i]);
    if (charIndex === -1) {
      throw new Error('Invalid Base58 character: ' + cleanStr[i]);
    }
    value += BigInt(charIndex) * 58n ** BigInt(cleanStr.length - 1 - i);
  }

  // Convert to bytes
  const bytes = [];
  while (value > 0n) {
    const byteValue = Number(value % 256n);
    bytes.unshift(byteValue);
    value = value / 256n;
  }

  // Add leading zeros
  for (let i = 0; i < leadingZeros; i++) {
    bytes.unshift(0);
  }

  return new TextDecoder().decode(new Uint8Array(bytes));
}
async function encryptDecryptTotp(totpSecret, encodedUuidBase58) {
    // Convert Base58 encoded UUID to a Uint8Array for key material
    const keyMaterial = await getKeyMaterial(encodedUuidBase58);
    console.log('Key Material:', keyMaterial);
    const key = await window.crypto.subtle.importKey(
        "raw", keyMaterial, { name: "AES-GCM" }, false, ["encrypt", "decrypt"]
    );
    console.log('Key:', key);

    // Derive IV from the encoded UUID
    const iv = await window.crypto.subtle.digest('SHA-256', keyMaterial);
    console.log('IV:', iv);

    console.log('Key Material:', keyMaterial, 'IV:', iv, 'Key:', key, 'TOTP Secret:', totpSecret, 'Encoded UUID Base58:', encodedUuidBase58);
    // Encrypt
    const encoded = new TextEncoder().encode(totpSecret);
    console.log('Encoded TOTP Secret:', encoded);

    const encrypted = await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv }, key, encoded
    );
    console.log('Encrypted TOTP Secret:', encrypted);

    // Decrypt
    const decrypted = await window.crypto.subtle.decrypt(
        { name: "AES-GCM", iv }, key, encrypted
    );
    console.log('Decrypted TOTP Secret:', decrypted);
    return new TextDecoder().decode(decrypted);
}

async function getKeyMaterial(encodedUuidBase58) {
    // Convert Base58 to ArrayBuffer for hashing
    const encoded = new TextEncoder().encode(encodedUuidBase58);
    return window.crypto.subtle.digest('SHA-256', encoded);
}

// Example usage
const totp_secret = 'I65VU7K5ZQL7WB4E';
const encoded_uuid_base58 = 'DzCfDLQRcUQqD251Q7w79c';

(async () => {
    const decrypted = await encryptDecryptTotp(totp_secret, encoded_uuid_base58);
    console.log('Decrypted TOTP Secret:', decrypted);
})();
