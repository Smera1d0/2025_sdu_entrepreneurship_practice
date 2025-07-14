import time
import os
from sm4_v0 import SM4
from sm4_ttable import SM4TTable
from sm4_opt import SM4Optimized
from sm4_gcm import SM4GCM

def benchmark_sm4():
    """SM4三种实现性能测试"""
    key = os.urandom(16)
    plaintext = os.urandom(16)
    count = 10000

    # 基础版本
    sm4_basic = SM4()
    start_time = time.time()
    for _ in range(count):
        ciphertext = sm4_basic.encrypt_block(plaintext, key)
    basic_time = time.time() - start_time

    # T-table版本
    sm4_ttable = SM4TTable()
    start_time = time.time()
    for _ in range(count):
        ciphertext = sm4_ttable.encrypt_block(plaintext, key)
    ttable_time = time.time() - start_time

    # C优化版本
    sm4_opt = SM4Optimized()
    start_time = time.time()
    for _ in range(count):
        ciphertext = sm4_opt.encrypt_block_optimized(plaintext, key)
    opt_time = time.time() - start_time

    print(f"基础版本 {count}次加密耗时: {basic_time:.3f}秒")
    print(f"T-table版本 {count}次加密耗时: {ttable_time:.3f}秒")
    print(f"C优化版本 {count}次加密耗时: {opt_time:.3f}秒")
    print(f"T-table加速比: {basic_time/ttable_time:.2f}倍")
    print(f"C优化加速比: {basic_time/opt_time:.2f}倍")

    # 结果一致性
    basic_result = sm4_basic.encrypt_block(plaintext, key)
    ttable_result = sm4_ttable.encrypt_block(plaintext, key)
    opt_result = sm4_opt.encrypt_block_optimized(plaintext, key)
    print(f"结果一致性: 基础-Ttable: {basic_result == ttable_result}, 基础-C: {basic_result == opt_result}")

def benchmark_gcm():
    """SM4-GCM三种实现性能测试"""
    key = os.urandom(16)
    iv = os.urandom(12)
    aad = b"header"
    plaintext = os.urandom(1024)
    count = 1000
    for mode in ['base', 'ttable', 'opt']:
        gcm = SM4GCM(key, mode=mode)
        start_time = time.time()
        for _ in range(count):
            ciphertext, tag = gcm.encrypt(plaintext, iv, aad)
            _ = gcm.decrypt(ciphertext, iv, tag, aad)
        elapsed = time.time() - start_time
        print(f"GCM模式({mode}) {count}次加解密耗时: {elapsed:.3f}秒")

if __name__ == "__main__":
    print("=== SM4单块加密性能 ===")
    benchmark_sm4()
    print("\n=== SM4-GCM模式性能 ===")
    benchmark_gcm()