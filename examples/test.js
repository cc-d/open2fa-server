//(venv) py3 examples/example.py
//b'NjkyYTNlNmI0YmQ0NDAwYmFhMmI4MjYxNjk1YjVmZmI=' || key_b64 || <class 'bytes'> || hex || 692a3e6b4bd4400baa2b8261695b5ffb
//encrypted_secret b'gAAAAABlsw4CI_djjut4RS0rEeJoEZbtT_1sbb_uMMNdbCO-_CXpEgPLbMaPg9bZOLb98ir9L5B5W-apC_PdqXfwEnkHKA_VrSeoq7pAapnlk_VG0pjRq50='
//decrypted_secret b'I65VU7K5ZQL7WB4E'
//
//
// NjkyYTNlNmI0YmQ0NDAwYmFhMmI4MjYxNjk1YjVmZmI= is passed to fernet.Secret
//
// encrypted_secret b'gAAAAABlswvP3Fe-NhwpNJUJ-LIa9XLhsZ83OuuKE81zSiQ7acwg2W1Tu02Z0HNM-ZXeUrRU1GoOm7RxB9bxr3xDloa_92RROWDRX7kYZ3O1GzVmQxnpoh0='

var secret = new fernet.Secret("NjkyYTNlNmI0YmQ0NDAwYmFhMmI4MjYxNjk1YjVmZmI=");

var token = new fernet.Token({
  secret: secret,
  token: 'gAAAAABlswl5zPpanMkPpRv4cbs364kzGqhwrChW_wO5cLQqAZyUYmUvQ9hTtfrAalIQA0Zb2xgREbJtQTNnnYp10aT1hR7J3k0nZZpfg7jRwAURZJaEUi0=',
  ttl: 0 // Setting Time To Live to 0 for no expiration check
});

console.log(token.decode());


