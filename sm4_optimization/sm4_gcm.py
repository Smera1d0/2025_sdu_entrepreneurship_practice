import os
import struct
from typing import Callable
from sm4_v0 import SM4
from sm4_ttable import SM4TTable
from sm4_opt import SM4Optimized

# Galois域乘法
# 参考NIST SP800-38D

def gf_mul(x: int, y: int) -> int:
    R = 0xE1000000000000000000000000000000
    z = 0
    for i in range(128):
        if (y >> (127 - i)) & 1:
            z ^= x
        if x & 1:
            x = (x >> 1) ^ R
        else:
            x >>= 1
    return z & ((1 << 128) - 1)

def ghash(h: bytes, aad: bytes, ciphertext: bytes) -> bytes:
    # h: 16字节
    # aad: 附加数据
    # ciphertext: 密文
    assert len(h) == 16
    h_int = int.from_bytes(h, 'big')
    y = 0
    # 处理AAD
    aad_padded = aad + b'\x00' * ((16 - len(aad) % 16) % 16)
    for i in range(0, len(aad_padded), 16):
        block = int.from_bytes(aad_padded[i:i+16], 'big')
        y = gf_mul(y ^ block, h_int)
    # 处理密文
    ct_padded = ciphertext + b'\x00' * ((16 - len(ciphertext) % 16) % 16)
    for i in range(0, len(ct_padded), 16):
        block = int.from_bytes(ct_padded[i:i+16], 'big')
        y = gf_mul(y ^ block, h_int)
    # 长度块
    aad_len = len(aad) * 8
    ct_len = len(ciphertext) * 8
    length_block = (aad_len << 64) | ct_len
    y = gf_mul(y ^ length_block, h_int)
    return y.to_bytes(16, 'big')

class SM4GCM:
    def __init__(self, key: bytes, mode: str = 'base'):
        assert len(key) == 16
        self.key = key
        if mode == 'base':
            self.sm4 = SM4()
            self.encrypt_block = self.sm4.encrypt_block
            self.decrypt_block = self.sm4.decrypt_block
        elif mode == 'ttable':
            self.sm4 = SM4TTable()
            self.encrypt_block = self.sm4.encrypt_block
            self.decrypt_block = self.sm4.decrypt_block
        elif mode == 'opt':
            self.sm4 = SM4Optimized()
            self.encrypt_block = self.sm4.encrypt_block_optimized
            self.decrypt_block = self.sm4.decrypt_block_optimized
        else:
            raise ValueError('Unknown mode')

    def _inc32(self, ctr: bytes) -> bytes:
        c = int.from_bytes(ctr, 'big')
        c = (c + 1) & ((1 << 128) - 1)
        return c.to_bytes(16, 'big')

    def gctr(self, icb: bytes, data: bytes) -> bytes:
        assert len(icb) == 16
        n = (len(data) + 15) // 16
        out = b''
        cb = icb
        for i in range(n):
            block = data[i*16:(i+1)*16]
            enc = self.encrypt_block(cb, self.key)
            out += bytes([a ^ b for a, b in zip(block, enc[:len(block)])])
            cb = self._inc32(cb)
        return out

    def encrypt(self, plaintext: bytes, iv: bytes, aad: bytes = b''):
        assert len(iv) == 12  # 96位IV
        h = self.encrypt_block(b'\x00'*16, self.key)
        j0 = iv + b'\x00\x00\x00\x01'
        ciphertext = self.gctr(j0, plaintext)
        tag = ghash(h, aad, ciphertext)
        return ciphertext, tag

    def decrypt(self, ciphertext: bytes, iv: bytes, tag: bytes, aad: bytes = b''):
        assert len(iv) == 12
        h = self.encrypt_block(b'\x00'*16, self.key)
        j0 = iv + b'\x00\x00\x00\x01'
        plaintext = self.gctr(j0, ciphertext)
        check_tag = ghash(h, aad, ciphertext)
        if check_tag != tag:
            raise ValueError('Tag mismatch!')
        return plaintext 