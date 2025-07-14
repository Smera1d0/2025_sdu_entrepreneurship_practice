# 优化版 SM2 实现
# 主要优化点：使用内置 pow() 逆元、减少重复计算、简化点乘
import random
from hashlib import sha256
import struct
import gmpy2

p = gmpy2.mpz(0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF)
a = gmpy2.mpz(0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC)
b = gmpy2.mpz(0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93)
Gx = gmpy2.mpz(0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7)
Gy = gmpy2.mpz(0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0)
n = gmpy2.mpz(0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123)

class Point:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = gmpy2.mpz(x)
        self.y = gmpy2.mpz(y)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Point({hex(int(self.x))}, {hex(int(self.y))})"

O = Point(0, 0)

def inverse_mod(k, p):
    return gmpy2.invert(k, p)


def point_add(P, Q):
    if P == O:
        return Q
    if Q == O:
        return P
    if P.x == Q.x and P.y != Q.y:
        return O
    if P == Q:
        l = (3 * P.x * P.x + a) * inverse_mod(2 * P.y, p) % p
    else:
        l = (Q.y - P.y) * inverse_mod(Q.x - P.x, p) % p
    x3 = (l * l - P.x - Q.x) % p
    y3 = (l * (P.x - x3) - P.y) % p
    return Point(x3, y3)


def point_mul(P, k):
    R = O
    addend = P
    k = gmpy2.mpz(k)
    while k:
        if k & 1:
            R = point_add(R, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return R

def gen_keypair():
    d = gmpy2.mpz(random.randrange(1, int(n)))
    P = point_mul(Point(Gx, Gy), d)
    return d, P

def sm3_hash(data: bytes) -> bytes:
    # 这里用sha256代替sm3，实际国密应使用sm3
    return sha256(data).digest()

def get_z(ID: bytes, P, a, b, Gx, Gy):
    ENTL = struct.pack('>H', len(ID)*8)
    joint = ENTL + ID + int.to_bytes(int(a), 32, 'big') + int.to_bytes(int(b), 32, 'big') \
        + int.to_bytes(int(Gx), 32, 'big') + int.to_bytes(int(Gy), 32, 'big') \
        + int.to_bytes(int(P.x), 32, 'big') + int.to_bytes(int(P.y), 32, 'big')
    return sm3_hash(joint)

def sm2_sign(msg, d, P=None, ID=b'1234567812345678'):
    if P is None:
        P = point_mul(Point(Gx, Gy), d)
    Z = get_z(ID, P, a, b, Gx, Gy)
    e = int.from_bytes(sm3_hash(Z + msg.encode()), 'big')
    while True:
        k = gmpy2.mpz(random.randrange(1, int(n)))
        P1 = point_mul(Point(Gx, Gy), k)
        r = (e + P1.x) % n
        if r == 0 or r + k == n:
            continue
        s = (inverse_mod(1 + d, n) * (k - r * d)) % n
        if s != 0:
            break
    return (r, s)

def sm2_verify(msg, P, sig, ID=b'1234567812345678'):
    r, s = sig
    Z = get_z(ID, P, a, b, Gx, Gy)
    e = int.from_bytes(sm3_hash(Z + msg.encode()), 'big')
    t = (r + s) % n
    if t == 0:
        return False
    P1 = point_add(point_mul(Point(Gx, Gy), s), point_mul(P, t))
    R = (e + P1.x) % n
    return R == r
