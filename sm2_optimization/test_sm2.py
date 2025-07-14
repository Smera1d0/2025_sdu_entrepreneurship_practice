# 测试脚本，验证基础版和优化版 SM2 的正确性
import sys
sys.path.append('./basic_sm2')
sys.path.append('./optimized_sm2')
from sm2_basic import gen_keypair as gen_keypair_basic, sm2_sign as sm2_sign_basic, sm2_verify as sm2_verify_basic
from sm2_optimized import gen_keypair as gen_keypair_opt, sm2_sign as sm2_sign_opt, sm2_verify as sm2_verify_opt

print('===== SM2 标准流程详细测试 =====')

msg = "Hello, SM2!"
msg_long = "A" * 1024
ID_std = b'1234567812345678'
ID_alt = b'ABCDEFGHABCDEFGH'

# 基础版标准ID
print("[基础版] 标准ID签名/验签...")
d_b, P_b = gen_keypair_basic()
sig_b = sm2_sign_basic(msg, d_b, P_b, ID_std)
assert sm2_verify_basic(msg, P_b, sig_b, ID_std), "基础版标准ID验签失败"

# 基础版自定义ID
print("[基础版] 自定义ID签名/验签...")
sig_b2 = sm2_sign_basic(msg, d_b, P_b, ID_alt)
assert sm2_verify_basic(msg, P_b, sig_b2, ID_alt), "基础版自定义ID验签失败"
assert not sm2_verify_basic(msg, P_b, sig_b2, ID_std), "基础版ID不一致应验签失败"

# 优化版标准ID
print("[优化版] 标准ID签名/验签...")
d_o, P_o = gen_keypair_opt()
sig_o = sm2_sign_opt(msg, d_o, P_o, ID_std)
assert sm2_verify_opt(msg, P_o, sig_o, ID_std), "优化版标准ID验签失败"

# 优化版自定义ID
print("[优化版] 自定义ID签名/验签...")
sig_o2 = sm2_sign_opt(msg, d_o, P_o, ID_alt)
assert sm2_verify_opt(msg, P_o, sig_o2, ID_alt), "优化版自定义ID验签失败"
assert not sm2_verify_opt(msg, P_o, sig_o2, ID_std), "优化版ID不一致应验签失败"

# 交叉实现互验
print("[交叉] 基础签名优化验签...")
assert sm2_verify_opt(msg, P_b, sig_b, ID_std), "基础签名优化验签失败"
print("[交叉] 优化签名基础验签...")
assert sm2_verify_basic(msg, P_o, sig_o, ID_std), "优化签名基础验签失败"

# 长消息测试
print("[长消息] 基础版...")
sig_b_long = sm2_sign_basic(msg_long, d_b, P_b, ID_std)
assert sm2_verify_basic(msg_long, P_b, sig_b_long, ID_std), "基础版长消息验签失败"
print("[长消息] 优化版...")
sig_o_long = sm2_sign_opt(msg_long, d_o, P_o, ID_std)
assert sm2_verify_opt(msg_long, P_o, sig_o_long, ID_std), "优化版长消息验签失败"

# 异常情况
print("[异常] 错误签名应验签失败...")
wrong_sig = (sig_b[0], (sig_b[1]+1)%0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123)
assert not sm2_verify_basic(msg, P_b, wrong_sig, ID_std), "基础版异常签名未检测"
assert not sm2_verify_opt(msg, P_b, wrong_sig, ID_std), "优化版异常签名未检测"

print("所有详细测试通过！")
