import redis
import os
import hashlib
import hashlib, binascii
if __name__ == "__main__":
    red = redis.Redis()

    salt1 = os.urandom(16)
    hash = hashlib.pbkdf2_hmac('sha256', b'test', salt1, 100000)
    pass1 = binascii.hexlify(hash)
    red.hset('wasikm:webapp:test', 'salt', salt1)
    red.hset('wasikm:webapp:test', 'test', pass1)

    salt2 = os.urandom(16)
    hash = hashlib.pbkdf2_hmac('sha256', b'admin', salt2, 100000)
    pass2 = binascii.hexlify(hash)
    red.hset('wasikm:webapp:admin', 'salt', salt2)
    red.hset('wasikm:webapp:admin', 'admin', pass2)

    salt3 = os.urandom(16)
    hash = hashlib.pbkdf2_hmac('sha256', b'password', salt3, 100000)
    pass3 = binascii.hexlify(hash)
    red.hset('wasikm:webapp:user', 'salt', salt3)
    red.hset('wasikm:webapp:user', 'user', pass3)

    print(red.hgetall('wasikm:webapp:test'))
    print(red.hgetall('wasikm:webapp:admin'))
    print(red.hgetall('wasikm:webapp:user'))
