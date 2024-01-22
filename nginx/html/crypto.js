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

// Pad the data to ensure it's a multiple of the block size (PKCS7 padding)
function pad(data, blockSize) {
    const padding = blockSize - (data.length % blockSize);
    const paddingArray = new Array(padding).fill(padding);
    const paddedData = new Uint8Array(data.length + padding);
    paddedData.set(data);
    paddedData.set(paddingArray, data.length);
    return paddedData;
}

// Encrypt using the same Base58-encoded key
function encrypt(data, base58Key) {
    const keyBytes = decodeBase58(base58Key);
    console.log("Encryption Key (Base58):", base58Key);

    // Pad the data to ensure it's a multiple of the block size
    const blockSize = 16; // AES block size is 16 bytes
    const dataBytes = new TextEncoder().encode(data);
    const paddedData = pad(dataBytes, blockSize);
    console.log("Padded Data (Hex):", CryptoJS.enc.Hex.stringify(CryptoJS.enc.Utf8.parse(paddedData)));

    const keyWordArray = CryptoJS.lib.WordArray.create(keyBytes);

    const encrypted = CryptoJS.AES.encrypt(CryptoJS.lib.WordArray.create(paddedData), keyWordArray, {
        mode: CryptoJS.mode.ECB,
    });

    const encryptedHex = CryptoJS.enc.Hex.stringify(encrypted.ciphertext);
    const encryptedBase58 = encodeBase58(encryptedHex);
    console.log("Encrypted Data (Base58):", encryptedBase58);
    return encryptedBase58;
}

// Decrypt using the same Base58-encoded key
function decrypt(encryptedBase58, base58Key) {
    const keyBytes = decodeBase58(base58Key);
    console.log("Decryption Key (Base58):", base58Key);

    const encryptedHex = decodeBase58(encryptedBase58);
    console.log("Encrypted Data (Hex):", encryptedHex);

    const keyWordArray = CryptoJS.lib.WordArray.create(keyBytes);

    const decrypted = CryptoJS.AES.decrypt({ ciphertext: CryptoJS.enc.Hex.parse(encryptedHex) }, keyWordArray, {
        mode: CryptoJS.mode.ECB,
    });

    const decryptedText = CryptoJS.enc.Utf8.stringify(decrypted);
    console.log("Decrypted Text:", decryptedText);
    return decryptedText;
}
var u = 'JBSWY3DPEHPK3PXP';

const encryptedText = encrypt(u, u);
const decryptedText = decrypt(encryptedText, u);

console.log("Encrypted Text:", encryptedText);
console.log("Decrypted Text:", decryptedText);