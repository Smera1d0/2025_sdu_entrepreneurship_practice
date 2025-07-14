"""
DDH-based Private Intersection-Sum Protocol 实现（严格参考论文Figure 2伪代码）
依赖:
    pip install phe pycryptodome
"""
import hashlib
import random
from Crypto.Util import number
from phe import paillier
from DDH_PSI_Sum_protocol import DDH_PSI_Sum_Homomorphic

# 哈希函数，将元素映射到有限域G

def H(x, p):
    h = hashlib.sha256(str(x).encode()).digest()
    return int.from_bytes(h, 'big') % p

# ===================== 测试用例 =====================
if __name__ == "__main__":
    print("===== 样例1：部分交集 =====")
    V1 = ['alice', 'bob', 'carol', 'dave']
    W1 = [('bob', 20), ('carol', 30), ('eve', 50), ('frank', 60)]
    psi1 = DDH_PSI_Sum_Homomorphic()
    HV_k1 = psi1.P1_round1(V1)
    Z, pk, HWj_k2_AEnc_tj = psi1.P2_round2(HV_k1, W1)
    S_J = psi1.P1_round3(Z, HWj_k2_AEnc_tj)
    intersection_sum = psi1.P2_decrypt(S_J)
    print(f"交集: {set(V1) & set(w for w, _ in W1)}")
    print(f"交集权重和: {intersection_sum}\n")

    print("===== 样例2：无交集 =====")
    V2 = ['alice', 'bob']
    W2 = [('carol', 10), ('dave', 20)]
    psi2 = DDH_PSI_Sum_Homomorphic()
    HV_k1 = psi2.P1_round1(V2)
    Z, pk, HWj_k2_AEnc_tj = psi2.P2_round2(HV_k1, W2)
    S_J = psi2.P1_round3(Z, HWj_k2_AEnc_tj)
    intersection_sum = psi2.P2_decrypt(S_J)
    print(f"交集: {set(V2) & set(w for w, _ in W2)}")
    print(f"交集权重和: {intersection_sum}\n")

    print("===== 样例3：全交集 =====")
    V3 = ['a', 'b']
    W3 = [('a', 5), ('b', 7)]
    psi3 = DDH_PSI_Sum_Homomorphic()
    HV_k1 = psi3.P1_round1(V3)
    Z, pk, HWj_k2_AEnc_tj = psi3.P2_round2(HV_k1, W3)
    S_J = psi3.P1_round3(Z, HWj_k2_AEnc_tj)
    intersection_sum = psi3.P2_decrypt(S_J)
    print(f"交集: {set(V3) & set(w for w, _ in W3)}")
    print(f"交集权重和: {intersection_sum}\n")

    print("===== 样例4：权重为0 =====")
    V4 = ['x', 'y']
    W4 = [('x', 0), ('z', 100)]
    psi4 = DDH_PSI_Sum_Homomorphic()
    HV_k1 = psi4.P1_round1(V4)
    Z, pk, HWj_k2_AEnc_tj = psi4.P2_round2(HV_k1, W4)
    S_J = psi4.P1_round3(Z, HWj_k2_AEnc_tj)
    intersection_sum = psi4.P2_decrypt(S_J)
    print(f"交集: {set(V4) & set(w for w, _ in W4)}")
    print(f"交集权重和: {intersection_sum}\n")

    print("===== 样例5：空集合 =====")
    V5 = []
    W5 = []
    psi5 = DDH_PSI_Sum_Homomorphic()
    HV_k1 = psi5.P1_round1(V5)
    Z, pk, HWj_k2_AEnc_tj = psi5.P2_round2(HV_k1, W5)
    S_J = psi5.P1_round3(Z, HWj_k2_AEnc_tj)
    intersection_sum = psi5.P2_decrypt(S_J)
    print(f"交集: {set(V5) & set(w for w, _ in W5)}")
    print(f"交集权重和: {intersection_sum}\n") 