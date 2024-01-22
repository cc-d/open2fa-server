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

//const tstr = 'This is a test string! 123';
//const b58Encoded = encodeBase58(tstr);
//console.log(tstr + ' -> ' + b58Encoded);
//const b58Decoded = decodeBase58(b58Encoded);
//console.log(b58Decoded);
