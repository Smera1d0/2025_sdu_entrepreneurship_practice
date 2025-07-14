# 基础版 SM2 实现
# 仅用于教学和测试，未做安全加固
import random
from hashlib import sha256
import struct

# 椭圆曲线参数（示例，非国密标准参数）
p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Point({hex(self.x)}, {hex(self.y)})"

O = Point(0, 0)  # 无穷远点

def inverse_mod(k, p):
    return pow(k, -1, p)

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
    while k:
        if k & 1:
            R = point_add(R, P)
        P = point_add(P, P)
        k >>= 1
    return R

def gen_keypair():
    d = random.randrange(1, n)
    P = point_mul(Point(Gx, Gy), d)
    return d, P

def sm3_hash(data: bytes) -> bytes:
    # 这里用sha256代替sm3，实际国密应使用sm3
    return sha256(data).digest()

def get_z(ID: bytes, P, a, b, Gx, Gy):
    ENTL = struct.pack('>H', len(ID)*8)
    joint = ENTL + ID \
        + int(a).to_bytes(32, 'big') + int(b).to_bytes(32, 'big') \
        + int(Gx).to_bytes(32, 'big') + int(Gy).to_bytes(32, 'big') \
        + int(P.x).to_bytes(32, 'big') + int(P.y).to_bytes(32, 'big')
    return sm3_hash(joint)

def sm2_sign(msg, d, P=None, ID=b'1234567812345678'):
    if P is None:
        P = point_mul(Point(Gx, Gy), d)
    Z = get_z(ID, P, a, b, Gx, Gy)
    e = int.from_bytes(sm3_hash(Z + msg.encode()), 'big')
    while True:
        k = random.randrange(1, n)
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
