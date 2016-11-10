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


def encrypt():

    password = 'pass'

    iv = os.urandom(16)

    backend = default_backend()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=(128//8),
        salt=b'sdfsdfsdfsd',
        iterations=1000,
        backend=backend
    )
    key = kdf.derive(password.encode('utf-8'))

    data = 'eyJpdiI6IlZUQVZXTFFLRUxMbWF3MFltcTFMOWc9PSIsInYiOjEsIml0ZXIiOjEwMDAwLCJrcyI6MTI4LCJ0cyI6MTI4LCJtb2RlIjoiZ2NtIiwiYWRhdGEiOiIiLCJjaXBoZXIiOiJhZXMiLCJzYWx0IjoiSEQrQldxdHozbU09IiwiY3QiOiJET2hZamJ5VW0zQ3JaKy9nbnR1S09PenA0VjFTQ1Y5U1lIaTRSTjdJTG00UCJ9'


    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=backend,
    )

    encryptor = cipher.encryptor()

    ct = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    tag = encryptor.tag
    return ct,iv, tag


def decrypt():

    ct ,iv, tag = encrypt()

    password = 'pass'

    backend = default_backend()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=(128//8),
        salt=b'sdfsdfsdfsd',
        iterations=1000,
        backend=backend
    )
    key = kdf.derive(password.encode('utf-8'))

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=backend,
    )

    dec = cipher.decryptor()
    pt = (dec.update(ct) + dec.finalize()).decode('utf-8')
    print(pt)


if __name__ == '__main__':

    decrypt()
