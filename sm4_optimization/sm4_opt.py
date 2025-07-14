import ctypes
import os
import sys

class SM4Optimized:
    def __init__(self, lib_path=None):
        if lib_path is None:
            # 默认动态库名
            if sys.platform.startswith('darwin'):
                libname = 'libsm4opt.dylib'
            elif sys.platform.startswith('win'):
                libname = 'sm4opt.dll'
            else:
                libname = 'libsm4opt.so'
            lib_path = os.path.join(os.path.dirname(__file__), libname)
        self.lib = ctypes.CDLL(lib_path)
        self.lib.sm4_key_expansion.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
        self.lib.sm4_encrypt_block.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
        self.lib.sm4_decrypt_block.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]

    def encrypt_block_optimized(self, plaintext: bytes, key: bytes) -> bytes:
        assert len(plaintext) == 16 and len(key) == 16
        rk = (ctypes.c_uint32 * 32)()
        self.lib.sm4_key_expansion(ctypes.c_char_p(key), rk)
        outbuf = ctypes.create_string_buffer(16)
        self.lib.sm4_encrypt_block(ctypes.c_char_p(plaintext), outbuf, rk)
        return outbuf.raw

    def decrypt_block_optimized(self, ciphertext: bytes, key: bytes) -> bytes:
        assert len(ciphertext) == 16 and len(key) == 16
        rk = (ctypes.c_uint32 * 32)()
        self.lib.sm4_key_expansion(ctypes.c_char_p(key), rk)
        outbuf = ctypes.create_string_buffer(16)
        self.lib.sm4_decrypt_block(ctypes.c_char_p(ciphertext), outbuf, rk)
        return outbuf.raw