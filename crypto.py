import os

from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
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
    key = kdf.derive(password.encode('utf-8'))


    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=backend,
    )

    encryptor = cipher.encryptor()

    ct = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    tag = encryptor.tag


    crypto_options = {}

    crypto_options['iv'] = b64encode(iv).decode('utf-8')

    crypto_options['salt'] = b64encode(salt).decode('utf-8')
    crypto_options['iter'] = str(10000)
    crypto_options['tag'] = b64encode(tag).decode('utf-8')
    crypto_options['ct'] = b64encode(ct).decode('utf-8')


    return crypto_options


def decrypt_dump(password, option):

    backend = default_backend()

    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=(128//8),
        salt=option['salt'],
        iterations=option['iter'],
        backend=backend
    )
    key = kdf.derive(password.encode('utf-8'))

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(option['iv'], option['tag']),
        backend=backend,
    )

    dec = cipher.decryptor()
    pt = (dec.update(option['ct']) + dec.finalize()).decode('utf-8')
    return pt
