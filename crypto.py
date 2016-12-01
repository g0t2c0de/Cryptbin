import os

from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes)

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from base64 import b64decode, b64encode


def encrypt_dump(password, data):

    salt = os.urandom(16)
    iv = os.urandom(16)

    backend = default_backend()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=(128//8),
        salt=salt,
        iterations=10000,
        backend=backend
    )

    try:
        key = kdf.derive(password.encode('utf-8'))
    except TypeError:
        print('Password must be string character')

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=backend
    )

    encryptor = cipher.encryptor()

    try:
        ct = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    except Exception as e:
        print(str(e))

    tag = encryptor.tag
    crypto_opt = {}

    opt = {'iv': iv, 'salt': salt, 'tag': tag, 'ct': ct}

    for key in opt:
        crypto_opt[key] = b64encode(opt[key]).decode('utf-8')

    crypto_opt['iter'] = str(10000)

    return crypto_opt


def check(password, option):

    backend = default_backend()

    opt = ('iv', 'salt', 'tag', 'ct')

    opts = {}
    for key in opt:
        opts[key] = b64decode(option[key])

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=(128//8),
        salt=opts['salt'],
        iterations=int(option['iter']),
        backend=backend
    )

    key = kdf.derive(password.encode('utf-8'))
    iv = opts['iv']
    tag = opts['tag']
    ct = opts['ct']
    return key, iv, tag, ct


def decrypt_dump(password, data):

    key, iv, tag, ct = check(password, data)
    backend = default_backend()

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=backend,
    )

    decryptor = cipher.decryptor()

    try:
        return (decryptor.update(ct) + decryptor.finalize()).decode('utf-8')
    except Exception as e:
        print(str(e))
        return None
