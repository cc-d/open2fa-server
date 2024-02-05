const ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const BASE = BigInt(ALPHABET.length);

function b58decode(input) {
  let num = BigInt(0);
  for (let i = 0; i < input.length; i++) {
    const charIndex = ALPHABET.indexOf(input[i]);
    if (charIndex === -1) {
      throw new Error('Invalid character in Base58 string');
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

async function decryptWithBase58(
  ciphertextB58,
  keyB58,
  iv = b58decode('6xA5cTR1239iti1EFMiXoT')
) {
  const crypto = window.crypto.subtle;

  // Decode the Base58-encoded key and IV
  const decodedKey = b58decode(keyB58);

  const keyObj = await crypto.importKey(
    'raw',
    decodedKey,
    { name: 'AES-CBC' },
    false,
    ['decrypt']
  );

  const decodedCiphertext = b58decode(ciphertextB58);
  const decrypted = await crypto.decrypt(
    {
      name: 'AES-CBC',
      iv: iv,
    },
    keyObj,
    decodedCiphertext
  );

  return new TextDecoder().decode(decrypted);
}

// Base32 Decode function from the previous step
function base32Decode(input) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let bits = 0;
  let value = 0;
  const output = [];

  for (let i = 0; i < input.length; i++) {
    const idx = alphabet.indexOf(input[i].toUpperCase());
    if (idx === -1) {
      continue;
    }

    value = (value << 5) | idx;
    bits += 5;

    if (bits >= 8) {
      output.push((value >>> (bits - 8)) & 0xff);
      bits -= 8;
    }
  }

  return new Uint8Array(output);
}

// SHA-1 hashing function using crypto.subtle
async function sha1(data) {
  const encoder = new TextEncoder();
  const encodedData = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-1', encodedData);
  return new Uint8Array(hashBuffer); // Return byte array for further processing
}

async function generateTOTPCode(secretBase32) {
    // Decode Base32 secret to a format suitable for cryptographic operations
    const decodedSecret = base32Decode(secretBase32);

    // Calculate the time step
    const timeStep = Math.floor(Date.now() / 1000 / 30);
    const timeStepBytes = new ArrayBuffer(8);
    const view = new DataView(timeStepBytes);
    // TOTP uses the Unix time divided by 30 seconds to define the current time step.
    // We need to fill the ArrayBuffer with this time step value.
    // Set the last 4 bytes, since JavaScript uses big endian and TOTP time step is a 64-bit integer
    view.setUint32(4, timeStep, false);

    // Import the HMAC key
    const hmacKey = await crypto.subtle.importKey(
      'raw',
      decodedSecret.buffer, // Use the ArrayBuffer of the decoded secret
      { name: 'HMAC', hash: { name: 'SHA-1' } },
      false,
      ['sign']
    );

    // Sign the time step bytes with the HMAC key
    const hmac = await crypto.subtle.sign('HMAC', hmacKey, timeStepBytes);
    const offset = new Uint8Array(hmac)[19] & 0xf;
    const binary = (
      ((new Uint8Array(hmac)[offset] & 0x7f) << 24) |
      ((new Uint8Array(hmac)[offset + 1] & 0xff) << 16) |
      ((new Uint8Array(hmac)[offset + 2] & 0xff) << 8) |
      (new Uint8Array(hmac)[offset + 3] & 0xff)
    ) % 1000000;

    return binary.toString().padStart(6, '0');
  }

document.addEventListener('DOMContentLoaded', function () {
  const fetchSecretsBtn = document.getElementById('fetchSecretBtn');
  const decryptSecretsBtn = document.getElementById('decryptSecretsBtn');
  const open2faIdInput = document.getElementById('open2faIdInput');
  const open2faSecretInput = document.getElementById('open2faSecretInput');
  const rememberSecretCheck = document.getElementById('rememberSecretCheck');
  const rememberSecretsCheck = document.getElementById('rememberSecretsCheck');

  // Load saved values and checkbox states
  if (localStorage.getItem('open2faId')) {
    open2faIdInput.value = localStorage.getItem('open2faId');
    rememberSecretCheck.checked = localStorage.getItem('rememberSecret') === 'true';
  }

  if (localStorage.getItem('open2faSecret')) {
    open2faSecretInput.value = localStorage.getItem('open2faSecret');
    rememberSecretsCheck.checked = localStorage.getItem('rememberSecrets') === 'true';
  }


  fetchSecretsBtn.addEventListener('click', async () => {
    if (rememberSecretCheck.checked) {
      localStorage.setItem('open2faId', open2faIdInput.value);
      localStorage.setItem('rememberSecret', rememberSecretCheck.checked);
    } else {
      localStorage.removeItem('open2faId');
      localStorage.setItem('rememberSecret', false);
    }
    const open2faId = open2faIdInput.value.trim();
    await fetchEncryptedSecrets(open2faId);
  });

  decryptSecretsBtn.addEventListener('click', async () => {
    if (rememberSecretsCheck.checked) {
      localStorage.setItem('open2faSecret', open2faSecretInput.value);
      localStorage.setItem('rememberSecrets', rememberSecretsCheck.checked);
    } else {
      localStorage.removeItem('open2faSecret');
      localStorage.setItem('rememberSecrets', false);
    }
    const open2faSecret = open2faSecretInput.value.trim();
    await decryptAndGenerateCodes(open2faSecret);
  });

  async function fetchEncryptedSecrets(open2faId) {
    try {
      const response = await fetch('/api/v1/totps', {
        method: 'GET',
        headers: {
          'X-User-Hash': open2faId,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      displayEncryptedSecrets(data.totps);
    } catch (error) {
      console.error('Error fetching encrypted secrets:', error);
    }
  }

  function startCountdownAndRegenerateCodes(element, open2faSecret) {
    // Calculate the time left until the next 30-second window
    let timeLeft = 30 - (Math.floor(Date.now() / 1000) % 30);
    const countdownElement = element.querySelector('.countdown');
    countdownElement.textContent = `${timeLeft}s`;

    const countdownInterval = setInterval(() => {
      timeLeft--;
      countdownElement.textContent = `${timeLeft}s`;

      if (timeLeft <= 0) {
        clearInterval(countdownInterval); // Clear the existing interval
        regenerateCodeForElement(element, open2faSecret); // Regenerate the code for this specific element
        startCountdownAndRegenerateCodes(element, open2faSecret); // Restart the countdown
      }
    }, 1000);
  }

  async function regenerateCodeForElement(element, open2faSecret) {
    const encryptedSecret = element.dataset.encSecret;
    try {
      const decryptedSecret = await decryptWithBase58(
        encryptedSecret,
        open2faSecret
      );
      const totpCode = await generateTOTPCode(decryptedSecret);
      element.querySelector('.totp-code').textContent = `${totpCode}`;
      element.querySelector('.totp-code').classList.add('mui-light-green');
      element.querySelector('.totp-code').classList.remove('mui-red');
    } catch (error) {
      console.error('Error regenerating TOTP code:', error);
    }
  }

  // Adjust the decryptAndGenerateCodes function to call startCountdownAndRegenerateCodes
  async function decryptAndGenerateCodes(open2faSecret) {
    const encryptedSecretElements =
      secretsContainer.querySelectorAll('.encrypted-secret');
    encryptedSecretElements.forEach((element) => {
      regenerateCodeForElement(element, open2faSecret); // Initial code generation
      startCountdownAndRegenerateCodes(element, open2faSecret); // Start countdown and setup for regeneration
    });
  }

  function displayEncryptedSecrets(encryptedSecrets) {
    secretsContainer.innerHTML = '';
    encryptedSecrets.forEach((secret) => {
      const secretElement = document.createElement('div');
      secretElement.classList.add(
        'encrypted-secret',
        'd-flex',

      );
      secretElement.dataset.encSecret = secret.enc_secret;

      const nameLabel = document.createElement('span');
      nameLabel.classList.add('secret-name');
      nameLabel.textContent = secret.name + ':' || 'Unnamed Secret:';
      secretElement.appendChild(nameLabel);

      const codeLabel = document.createElement('span');
      codeLabel.textContent = ' (encrypted)';
      codeLabel.classList.add('totp-code');
      codeLabel.classList.add('mui-red');
      codeLabel.classList.remove('mui-light-green');
      secretElement.appendChild(codeLabel);

      const countdownLabel = document.createElement('span');
      countdownLabel.classList.add('countdown');
      secretElement.appendChild(countdownLabel);

      secretsContainer.appendChild(secretElement);
    });
  }
});
