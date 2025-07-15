
# PoC: SM2 签名中因不同用户重用相同随机数 k 导致私钥互相泄露的攻击验证

import sys
# 确保 basic_sm2 模块在路径中
sys.path.append('.') 
from basic_sm2.sm2_basic import n, Gx, Gy, a, b, Point, point_mul, get_z, sm3_hash, inverse_mod, gen_keypair

# 再次使用我们修改过的、允许手动指定 k 的签名函数
def sm2_sign_fixed_k(msg, d, k, P=None, ID=b'1234567812345678'):
    if P is None:
        P = point_mul(Point(Gx, Gy), d)
    Z = get_z(ID, P, a, b, Gx, Gy)
    e = int.from_bytes(sm3_hash(Z + msg.encode()), 'big')
    P1 = point_mul(Point(Gx, Gy), k)
    r = (e + P1.x) % n
    if r == 0 or r + k == n:
        # 在真实场景中，这会要求重新生成 k，但为了演示，我们忽略
        pass
    s = (inverse_mod(1 + d, n) * (k - r * d)) % n
    if s == 0:
        # 同样，在真实场景中会重新生成 k
        pass
    return (r, s)


def crack_other_user_key(my_d, my_sig, other_sig):
    """从攻击者自己的视角，破解另一个用户的私钥"""
    my_r, my_s = my_sig
    other_r, other_s = other_sig

    # 1. 攻击者首先从自己的签名和私钥中恢复出随机数 k
    # s = (inv(1 + d) * (k - r*d)) mod n  => k = s*(1+d) + r*d mod n
    k = (my_s * (1 + my_d) + my_r * my_d) % n

    # 2. 然后，利用恢复出的 k 和对方的签名来破解对方的私钥
    # s_other = (inv(1 + d_other) * (k - r_other*d_other)) mod n
    # s_other * (1 + d_other) = k - r_other*d_other mod n
    # s_other + s_other*d_other = k - r_other*d_other mod n
    # d_other * (s_other + r_other) = k - s_other mod n
    # d_other = (k - s_other) * inv(s_other + r_other) mod n
    
    k_minus_s_other = (k - other_s) % n
    s_other_plus_r_other = (other_s + other_r) % n
    
    if s_other_plus_r_other == 0:
        return None # 无法计算

    inv_denominator = inverse_mod(s_other_plus_r_other, n)
    cracked_d = (k_minus_s_other * inv_denominator) % n
    
    return cracked_d, k

if __name__ == '__main__':
    print("===== SM2 k-reuse Across Users Attack PoC =====")

    # 1. 生成 Alice 和 Bob 各自的密钥对
    d_a, P_a = gen_keypair()
    d_b, P_b = gen_keypair()
    print(f"Alice 的原始私钥 (da): {hex(d_a)}")
    print(f"Bob 的原始私钥 (db):   {hex(d_b)}")

    # 2. 定义一个被意外重用的随机数 k
    k_shared = 98765432109876543210
    print(f"\n被意外重用的随机数 (k): {k_shared}")

    # 3. Alice 和 Bob 使用同一个 k 对各自的消息进行签名
    msg_a = "Alice sends 1 BTC to Carol"
    msg_b = "Bob sends 5 BTC to David"
    
    sig_a = sm2_sign_fixed_k(msg_a, d_a, k_shared, P_a, ID=b'ALICE123')
    sig_b = sm2_sign_fixed_k(msg_b, d_b, k_shared, P_b, ID=b'BOB45678')
    print(f"Alice 的签名 (ra, sa): ({hex(sig_a[0])}, {hex(sig_a[1])})")
    print(f"Bob 的签名 (rb, sb):   ({hex(sig_b[0])}, {hex(sig_b[1])})")

    # 4. 开始互相攻击
    print("\n--- Alice 破解 Bob 的私钥 ---")
    cracked_d_b, recovered_k_a = crack_other_user_key(d_a, sig_a, sig_b)
    if cracked_d_b:
        print(f"Alice 从自己的签名中恢复出的 k: {recovered_k_a}")
        print(f"Alice 破解出的 Bob 的私钥: {hex(cracked_d_b)}")
        assert recovered_k_a == k_shared
        assert cracked_d_b == d_b
        print("[+] Alice 攻击成功！")
    else:
        print("[-] Alice 攻击失败。")

    print("\n--- Bob 破解 Alice 的私钥 ---")
    cracked_d_a, recovered_k_b = crack_other_user_key(d_b, sig_b, sig_a)
    if cracked_d_a:
        print(f"Bob 从自己的签名中恢复出的 k: {recovered_k_b}")
        print(f"Bob 破解出的 Alice 的私钥: {hex(cracked_d_a)}")
        assert recovered_k_b == k_shared
        assert cracked_d_a == d_a
        print("[+] Bob 攻击成功！")
    else:
        print("[-] Bob 攻击失败。")
