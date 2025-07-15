
# PoC: SM2 签名中因重用随机数 k 导致私钥泄露的攻击验证
import sys
from basic_sm2.sm2_basic import n, Gx, Gy, Point, point_mul, get_z, sm3_hash, inverse_mod, gen_keypair, a, b

# 为了能复现攻击，我们需要一个修改版的签名函数，它允许我们手动指定 k
def sm2_sign_fixed_k(msg, d, k, P=None, ID=b'1234567812345678'):
    if P is None:
        P = point_mul(Point(Gx, Gy), d)
    Z = get_z(ID, P, a, b, Gx, Gy)
    e = int.from_bytes(sm3_hash(Z + msg.encode()), 'big')
    P1 = point_mul(Point(Gx, Gy), k)
    r = (e + P1.x) % n
    s = (inverse_mod(1 + d, n) * (k - r * d)) % n
    return (r, s)

def k_reuse_attack(sig1, sig2):
    r1, s1 = sig1
    r2, s2 = sig2
    
    # 根据推导公式计算 d
    # d = (s2 - s1) * inv(r1 - r2 + s1 - s2) mod n
    s2_minus_s1 = (s2 - s1) % n
    r1_minus_r2 = (r1 - r2) % n
    s1_minus_s2 = (s1 - s2) % n
    
    denominator = (r1_minus_r2 + s1_minus_s2) % n
    if denominator == 0:
        print("分母为零，无法计算。")
        return None
        
    inv_denominator = inverse_mod(denominator, n)
    
    cracked_d = (s2_minus_s1 * inv_denominator) % n
    return cracked_d

if __name__ == '__main__':
    print("===== SM2 k-reuse Attack PoC ====")

    # 1. 生成一个合法的密钥对
    d, P = gen_keypair()
    print(f"原始私钥 (d): {hex(d)}")
    print(f"对应公钥 (P.x): {hex(P.x)}")
    print(f"对应公钥 (P.y): {hex(P.y)}")

    # 2. 定义两条不同的消息
    msg1 = "This is the first message."
    msg2 = "This is a different message."

    # 3. 模拟错误操作：使用同一个 k 对两条消息签名
    k = 1234567890  # 固定的随机数 k
    print(f"\n使用的固定随机数 (k): {k}")

    sig1 = sm2_sign_fixed_k(msg1, d, k, P)
    sig2 = sm2_sign_fixed_k(msg2, d, k, P)
    print(f"消息1的签名 (r1, s1): ({hex(sig1[0])}, {hex(sig1[1])})")
    print(f"消息2的签名 (r2, s2): ({hex(sig2[0])}, {hex(sig2[1])})")

    # 4. 实施攻击
    print("\n开始攻击... 仅使用两个签名和公开参数进行计算...")
    cracked_d = k_reuse_attack(sig1, sig2)

    if cracked_d:
        print(f"\n破解出的私钥 (cracked_d): {hex(cracked_d)}")

        # 5. 验证结果
        if cracked_d == d:
            print("\n[+] 攻击成功！破解出的私钥与原始私钥完全一致。")
        else:
            print("\n[-] 攻击失败！破解出的私钥不正确。")
