"""
DDH-based Private Intersection-Sum Protocol 实现（严格参考论文Figure 2伪代码）
依赖:
    pip install phe pycryptodome
"""
import hashlib
import random
from Crypto.Util import number
from phe import paillier

def H(x, p):
    h = hashlib.sha256(str(x).encode()).digest()
    return int.from_bytes(h, 'big') % p

class DDH_PSI_Sum_Homomorphic:
    def __init__(self, p=None, g=None):
        # 群参数
        self.p = number.getPrime(2048) if p is None else p
        self.g = 2 if g is None else g

    # Round 1 (P1)
    def P1_round1(self, V):
        self.k1 = random.randrange(2, self.p-1)
        # H(vi)^k1
        self.V = V
        self.HV_k1 = [pow(H(v, self.p), self.k1, self.p) for v in V]
        random.shuffle(self.HV_k1)
        return self.HV_k1

    # Round 2 (P2)
    def P2_round2(self, HV_k1, W):
        self.k2 = random.randrange(2, self.p-1)
        # Z = {H(vi)^k1k2}
        self.Z = [pow(hv, self.k2, self.p) for hv in HV_k1]
        random.shuffle(self.Z)
        # Paillier密钥对
        self.pk, self.sk = paillier.generate_paillier_keypair()
        # 对W中的每个(wj, tj)
        self.W = W
        self.HWj_k2 = []
        self.AEnc_tj = []
        for wj, tj in W:
            hwj = pow(H(wj, self.p), self.k2, self.p)
            self.HWj_k2.append(hwj)
            self.AEnc_tj.append(self.pk.encrypt(tj))
        # 发送 (HWj_k2, AEnc_tj)
        return self.Z, self.pk, list(zip(self.HWj_k2, self.AEnc_tj))

    # Round 3 (P1)
    def P1_round3(self, Z, HWj_k2_AEnc_tj):
        # 对每个 (H(wj)^k2, AEnc(tj))，P1用k1再加密
        HWj_k1k2 = [pow(hwj, self.k1, self.p) for hwj, _ in HWj_k2_AEnc_tj]
        # 交集索引J: H(wj)^k1k2 ∈ Z
        J = [i for i, val in enumerate(HWj_k1k2) if val in Z]
        # 交集密文和
        AEnc_tj_list = [HWj_k2_AEnc_tj[i][1] for i in J]
        if AEnc_tj_list:
            S_J = AEnc_tj_list[0]
            for ct in AEnc_tj_list[1:]:
                S_J += ct
        else:
            S_J = None
        # 返回S_J密文
        return S_J

    # Output (P2)
    def P2_decrypt(self, S_J):
        if S_J is None:
            return 0
        return self.sk.decrypt(S_J) 