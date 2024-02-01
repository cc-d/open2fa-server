const ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
const BASE = BigInt(ALPHABET.length);

function b58decode(input) {
    let num = BigInt(0);
    for (let i = 0; i < input.length; i++) {
        const charIndex = ALPHABET.indexOf(input[i]);
        if (charIndex === -1) {
            throw new Error("Invalid character in Base58 string");
        }
        num = num * BASE + BigInt(charIndex);
    }

    let bytes = [];
    while (num > 0) {
        bytes.push(Number(num % BigInt(256)));
        num = num / BigInt(256);
    }
    return new Uint8Array(bytes.reverse()).buffer;
}

// Helper function to convert string to ArrayBuffer
function str2ab(str) {
    const buffer = new Uint8Array(str.length);
    for (let i = 0; i < str.length; i++) {
        buffer[i] = str.charCodeAt(i);
    }
    return buffer;
}

// While in most cases you would want to use a random IV, we use a constant
// IV here as the UUID entropy ensures that the same plaintext is never
// encrypted twice.
// This is equivalent to b'0123456789abcdef'
const defaultIv = b58decode('6xA5cTR1239iti1EFMiXoT');

async function decryptWithBase58(ciphertextB58, keyB58, iv=b58decode('6xA5cTR1239iti1EFMiXoT')) {
  const crypto = window.crypto.subtle;

  // Decode the Base58-encoded key and IV
  const decodedKey = b58decode(keyB58);

  const keyObj = await crypto.importKey(
      "raw",
      decodedKey,
      { name: "AES-CBC" },
      false,
      ["decrypt"]
  );

  const decodedCiphertext = b58decode(ciphertextB58);
  const decrypted = await crypto.decrypt(
      {
          name: "AES-CBC",
          iv: iv
      },
      keyObj,
      decodedCiphertext
  );

  return new TextDecoder().decode(decrypted);
}


