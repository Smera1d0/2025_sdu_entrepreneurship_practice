#!/usr/bin/env python3
"""
SM4算法完整性测试和演示
包含标准测试向量验证、性能测试和功能演示
"""

import time
import os
from sm4_v0 import SM4
from sm4_opt import SM4Optimized
from gmssl import sm4 as gmssl_sm4

def compare_with_standard_library():
    """与标准SM4库对比验证"""
    
    print("=== 与标准SM4库对比验证 ===")
    
    # 测试数据
    key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    plaintext = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    
    # 我们的实现
    sm4_basic = SM4()
    sm4_opt = SM4Optimized()
    
    our_basic_result = sm4_basic.encrypt_block(plaintext, key)
    our_opt_result = sm4_opt.encrypt_block_optimized(plaintext, key)
    
    # 标准库实现 (gmssl)
    try:
        crypt_sm4 = gmssl_sm4.CryptSM4()
        crypt_sm4.set_key(key, gmssl_sm4.SM4_ENCRYPT)
        
        # gmssl会自动进行PKCS#7填充，输出32字节
        gmssl_full_result = crypt_sm4.crypt_ecb(plaintext)
        
        # 取前16字节作为实际的密文进行对比
        gmssl_result = gmssl_full_result[:16]
        
        print(f"测试密钥:   {key.hex().upper()}")
        print(f"测试明文:   {plaintext.hex().upper()}")
        print(f"我们(基础): {our_basic_result.hex().upper()}")
        print(f"我们(优化): {our_opt_result.hex().upper()}")
        print(f"gmssl标准: {gmssl_result.hex().upper()}")
        
        # 验证一致性
        basic_matches = our_basic_result == gmssl_result
        opt_matches = our_opt_result == gmssl_result
        
        print(f"\n对比结果:")
        print(f"✓ 基础版本与标准库一致: {'通过' if basic_matches else '失败'}")
        print(f"✓ 优化版本与标准库一致: {'通过' if opt_matches else '失败'}")
        
        # 测试解密
        if basic_matches and opt_matches:
            # 测试解密功能 - 使用gmssl的完整加密结果进行解密
            try:
                crypt_sm4.set_key(key, gmssl_sm4.SM4_DECRYPT)
                
                # 使用gmssl的完整加密结果（32字节）进行解密
                gmssl_decrypt_result = crypt_sm4.crypt_ecb(gmssl_full_result)
                
                # gmssl解密后去除填充，应该得到原始16字节
                if len(gmssl_decrypt_result) >= 16:
                    gmssl_decrypt = gmssl_decrypt_result[:16]
                    
                    our_basic_decrypt = sm4_basic.decrypt_block(our_basic_result, key)
                    our_opt_decrypt = sm4_opt.decrypt_block_optimized(our_opt_result, key)
                    
                    # 验证所有解密结果都等于原文
                    all_decrypt_correct = (
                        our_basic_decrypt == plaintext and 
                        our_opt_decrypt == plaintext and
                        gmssl_decrypt == plaintext
                    )
                    
                    print(f"✓ 解密功能与标准库一致: {'通过' if all_decrypt_correct else '失败'}")
                    
                    if not all_decrypt_correct:
                        print(f"  调试信息:")
                        print(f"  原文:       {plaintext.hex().upper()}")
                        print(f"  我们基础:   {our_basic_decrypt.hex().upper()}")
                        print(f"  我们优化:   {our_opt_decrypt.hex().upper()}")
                        print(f"  gmssl解密:  {gmssl_decrypt.hex().upper()}")
                    
                    return basic_matches and opt_matches and all_decrypt_correct
                else:
                    print(f"✓ 解密功能测试: 跳过 (gmssl解密结果长度异常)")
                    # 至少验证我们自己的解密是否正确
                    our_basic_decrypt = sm4_basic.decrypt_block(our_basic_result, key)
                    our_opt_decrypt = sm4_opt.decrypt_block_optimized(our_opt_result, key)
                    our_decrypt_ok = (our_basic_decrypt == plaintext and our_opt_decrypt == plaintext)
                    print(f"✓ 我们的解密功能: {'通过' if our_decrypt_ok else '失败'}")
                    return basic_matches and opt_matches and our_decrypt_ok
                    
            except Exception as e:
                print(f"✓ 解密功能测试: 跳过 (gmssl解密错误: {e})")
                # 至少验证我们自己的解密是否正确
                our_basic_decrypt = sm4_basic.decrypt_block(our_basic_result, key)
                our_opt_decrypt = sm4_opt.decrypt_block_optimized(our_opt_result, key)
                our_decrypt_ok = (our_basic_decrypt == plaintext and our_opt_decrypt == plaintext)
                print(f"✓ 我们的解密功能: {'通过' if our_decrypt_ok else '失败'}")
                return basic_matches and opt_matches and our_decrypt_ok
        
        return basic_matches and opt_matches
        
    except Exception as e:
        print(f"✗ 标准库测试出错: {e}")
        return False

def test_standard_vectors():
    """使用标准测试向量验证SM4实现的正确性"""
    print("=== SM4 标准测试向量验证 ===")
    
    # SM4标准测试向量
    key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    plaintext = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    expected_ciphertext = bytes.fromhex("681EDF34D206965E86B3E94F536E4246")
    
    # 测试基础版本
    sm4_basic = SM4()
    basic_result = sm4_basic.encrypt_block(plaintext, key)
    basic_decrypt = sm4_basic.decrypt_block(basic_result, key)
    
    # 测试优化版本
    sm4_opt = SM4Optimized()
    opt_result = sm4_opt.encrypt_block_optimized(plaintext, key)
    opt_decrypt = sm4_opt.decrypt_block_optimized(opt_result, key)
    
    print(f"密钥:     {key.hex().upper()}")
    print(f"明文:     {plaintext.hex().upper()}")
    print(f"期望密文: {expected_ciphertext.hex().upper()}")
    print(f"基础版本: {basic_result.hex().upper()}")
    print(f"优化版本: {opt_result.hex().upper()}")
    
    # 验证结果
    basic_correct = basic_result == expected_ciphertext
    opt_correct = opt_result == expected_ciphertext
    versions_match = basic_result == opt_result
    decrypt_correct = basic_decrypt == plaintext and opt_decrypt == plaintext
    
    print(f"\n验证结果:")
    print(f"✓ 基础版本正确性: {'通过' if basic_correct else '失败'}")
    print(f"✓ 优化版本正确性: {'通过' if opt_correct else '失败'}")
    print(f"✓ 版本一致性:     {'通过' if versions_match else '失败'}")
    print(f"✓ 解密正确性:     {'通过' if decrypt_correct else '失败'}")
    
    return basic_correct and opt_correct and versions_match and decrypt_correct

def performance_benchmark():
    """性能基准测试"""
    print("\n=== 性能基准测试 ===")
    
    # 生成测试数据
    key = os.urandom(16)
    plaintext = os.urandom(16)
    
    # 测试不同的数据量
    test_counts = [1000, 5000, 10000, 50000]
    
    sm4_basic = SM4()
    sm4_opt = SM4Optimized()
    
    # 准备gmssl
    gmssl_cipher = None

    try:
        gmssl_cipher = gmssl_sm4.CryptSM4()
        gmssl_cipher.set_key(key, gmssl_sm4.SM4_ENCRYPT)
    except:
        gmssl_cipher = None
    
    if gmssl_cipher:
        print(f"{'测试次数':<10} {'基础版本(秒)':<15} {'优化版本(秒)':<15} {'gmssl(秒)':<12} {'性能提升':<10}")
        print("-" * 70)
    else:
        print(f"{'测试次数':<10} {'基础版本(秒)':<15} {'优化版本(秒)':<15} {'性能提升':<10}")
        print("-" * 55)
    
    for count in test_counts:
        # 基础版本测试
        start_time = time.time()
        for _ in range(count):
            sm4_basic.encrypt_block(plaintext, key)
        basic_time = time.time() - start_time
        
        # 优化版本测试
        start_time = time.time()
        for _ in range(count):
            sm4_opt.encrypt_block_optimized(plaintext, key)
        opt_time = time.time() - start_time
        
        # gmssl测试（如果可用）
        gmssl_time = None
        if gmssl_cipher:
            try:
                start_time = time.time()
                for _ in range(count):
                    gmssl_cipher.crypt_ecb(plaintext)
                gmssl_time = time.time() - start_time
            except:
                gmssl_time = None
        
        speedup = basic_time / opt_time if opt_time > 0 else float('inf')
        
        if gmssl_time is not None:
            print(f"{count:<10} {basic_time:<15.3f} {opt_time:<15.3f} {gmssl_time:<12.3f} {speedup:<7.2f}x")
        else:
            print(f"{count:<10} {basic_time:<15.3f} {opt_time:<15.3f} {speedup:<7.2f}x")

def demonstrate_features():
    """演示SM4的各种功能"""
    print("\n=== SM4功能演示 ===")
    
    sm4 = SM4Optimized()
    
    # 演示1: 基本加密解密
    print("1. 基本加密解密:")
    message = "Hello, SM4!"
    key = os.urandom(16)
    
    # 将消息填充到16字节
    padded_msg = message.encode('utf-8').ljust(16, b'\x00')
    ciphertext = sm4.encrypt_block_optimized(padded_msg, key)
    decrypted = sm4.decrypt_block_optimized(ciphertext, key)
    
    print(f"   原始消息: {message}")
    print(f"   密钥:     {key.hex()}")
    print(f"   密文:     {ciphertext.hex()}")
    
    # 修复f-string中的反斜杠问题
    decrypted_msg = decrypted.decode('utf-8').rstrip('\x00')
    print(f"   解密结果: {decrypted_msg}")
    
    # 演示2: 不同密钥产生不同密文
    print("\n2. 密钥敏感性:")
    plaintext = b"Test message!!!!"
    key1 = os.urandom(16)
    key2 = os.urandom(16)
    
    cipher1 = sm4.encrypt_block_optimized(plaintext, key1)
    cipher2 = sm4.encrypt_block_optimized(plaintext, key2)
    
    print(f"   明文:     {plaintext.hex()}")
    print(f"   密钥1:    {key1.hex()}")
    print(f"   密文1:    {cipher1.hex()}")
    print(f"   密钥2:    {key2.hex()}")
    print(f"   密文2:    {cipher2.hex()}")
    print(f"   密文不同: {'是' if cipher1 != cipher2 else '否'}")
    
    # 演示3: 雪崩效应
    print("\n3. 雪崩效应 (明文1位变化):")
    plaintext1 = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    plaintext2 = bytes.fromhex("0123456789ABCDEFFEDCBA9876543211")  # 最后一位改变
    key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    
    cipher1 = sm4.encrypt_block_optimized(plaintext1, key)
    cipher2 = sm4.encrypt_block_optimized(plaintext2, key)
    
    # 计算不同的位数
    diff_bits = bin(int.from_bytes(cipher1, 'big') ^ int.from_bytes(cipher2, 'big')).count('1')
    
    print(f"   明文1:    {plaintext1.hex()}")
    print(f"   明文2:    {plaintext2.hex()}")
    print(f"   密文1:    {cipher1.hex()}")
    print(f"   密文2:    {cipher2.hex()}")
    print(f"   不同位数: {diff_bits}/128 ({diff_bits/128*100:.1f}%)")

def main():
    """主函数"""
    print("SM4密码算法测试与演示程序")
    print("=" * 50)
    
    # 标准测试向量验证
    if test_standard_vectors():
        print("✓ 所有标准测试通过")
    else:
        print("✗ 标准测试失败")
        return
    
    # 与标准库对比验证
    if compare_with_standard_library():
        print("✓ 标准库对比通过")
    else:
        print("✗ 标准库对比失败")
        return
    
    # 性能测试
    performance_benchmark()
    
    # 功能演示
    demonstrate_features()
    
    # 与标准库对比
    compare_with_standard_library()

if __name__ == "__main__":
    main()
