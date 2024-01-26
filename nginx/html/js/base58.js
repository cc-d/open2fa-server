const ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
function b58encode(input) {
  const base = ALPHABET.length;
  let num = BigInt(0);
  let encoded = "";

  for (let i = 0; i < input.length; i++) {
    num = num * BigInt(256) + BigInt(input.charCodeAt(i));
  }

  while (num > BigInt(0)) {
    const remainder = num % BigInt(base);
    encoded = ALPHABET[Number(remainder)] + encoded;
    num = num / BigInt(base);
  }

  return encoded;
}

function b58decode(input) {
  const base = ALPHABET.length;
  let num = BigInt(0);

  for (let i = 0; i < input.length; i++) {
    const charIndex = ALPHABET.indexOf(input[i]);
    if (charIndex === -1) {
      throw new Error("Invalid character in base58 string");
    }
    num = num * BigInt(base) + BigInt(charIndex);
  }

  let decoded = "";
  while (num > BigInt(0)) {
    const byte = num % BigInt(256);
    decoded = String.fromCharCode(Number(byte)) + decoded;
    num = num / BigInt(256);
  }

  return decoded;
}

