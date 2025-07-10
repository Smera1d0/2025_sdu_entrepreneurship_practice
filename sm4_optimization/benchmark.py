import time
import os
from sm4_v0 import SM4
from sm4_opt import SM4Optimized

def benchmark_sm4():
    """SM4性能测试"""
    # 生成测试数据
    key = os.urandom(16)
    plaintext = os.urandom(16)
    
    # 基础版本测试
    sm4_basic = SM4()
    start_time = time.time()
    for _ in range(10000):
        ciphertext = sm4_basic.encrypt_block(plaintext, key)
    basic_time = time.time() - start_time
    
    # 优化版本测试
    sm4_opt = SM4Optimized()
    start_time = time.time()
    for _ in range(10000):
        ciphertext = sm4_opt.encrypt_block_optimized(plaintext, key)
    opt_time = time.time() - start_time
    
    print(f"基础版本 10000次加密耗时: {basic_time:.3f}秒")
    print(f"优化版本 10000次加密耗时: {opt_time:.3f}秒")
    print(f"性能提升: {basic_time/opt_time:.2f}倍")
    
    # 验证正确性
    basic_result = sm4_basic.encrypt_block(plaintext, key)
    opt_result = sm4_opt.encrypt_block_optimized(plaintext, key)
    print(f"结果一致性: {basic_result == opt_result}")

if __name__ == "__main__":
    benchmark_sm4()