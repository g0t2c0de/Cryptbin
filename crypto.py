import os

from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from base64 import b64decode
from urllib.request import urlopen
import json
import re
import os


def encrypt(password, data):

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
    crypto_options['iv'] = iv
    crypto_options['salt'] = salt
    crypto_options['iter'] = 10000
    crypto_options['tag'] = tag
    crypto_options['ct'] = ct


    return crypto_options


def decrypt(password, option):

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
