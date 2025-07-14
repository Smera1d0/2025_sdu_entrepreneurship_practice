# benchmark 脚本，比较基础版和优化版 SM2 的性能
import sys
import timeit
sys.path.append('./basic_sm2')
sys.path.append('./optimized_sm2')
from sm2_basic import gen_keypair as gen_keypair_basic, sm2_sign as sm2_sign_basic, sm2_verify as sm2_verify_basic
from sm2_optimized import gen_keypair as gen_keypair_opt, sm2_sign as sm2_sign_opt, sm2_verify as sm2_verify_opt

msg = "Benchmark SM2!"
msg_long = "A" * 1024
ID_std = b'1234567812345678'
ID_alt = b'ABCDEFGHABCDEFGH'
N = 100

print('===== SM2 Benchmark =====')

def bench_basic():
    d, P = gen_keypair_basic()
    sig = sm2_sign_basic(msg, d, P, ID_std)
    for _ in range(N):
        sm2_verify_basic(msg, P, sig, ID_std)

def bench_basic_long():
    d, P = gen_keypair_basic()
    sig = sm2_sign_basic(msg_long, d, P, ID_std)
    for _ in range(N):
        sm2_verify_basic(msg_long, P, sig, ID_std)

def bench_basic_altid():
    d, P = gen_keypair_basic()
    sig = sm2_sign_basic(msg, d, P, ID_alt)
    for _ in range(N):
        sm2_verify_basic(msg, P, sig, ID_alt)

def bench_opt():
    d, P = gen_keypair_opt()
    sig = sm2_sign_opt(msg, d, P, ID_std)
    for _ in range(N):
        sm2_verify_opt(msg, P, sig, ID_std)

def bench_opt_long():
    d, P = gen_keypair_opt()
    sig = sm2_sign_opt(msg_long, d, P, ID_std)
    for _ in range(N):
        sm2_verify_opt(msg_long, P, sig, ID_std)

def bench_opt_altid():
    d, P = gen_keypair_opt()
    sig = sm2_sign_opt(msg, d, P, ID_alt)
    for _ in range(N):
        sm2_verify_opt(msg, P, sig, ID_alt)

basic_time = timeit.timeit(bench_basic, number=10)
basic_long_time = timeit.timeit(bench_basic_long, number=10)
basic_altid_time = timeit.timeit(bench_basic_altid, number=10)
opt_time = timeit.timeit(bench_opt, number=10)
opt_long_time = timeit.timeit(bench_opt_long, number=10)
opt_altid_time = timeit.timeit(bench_opt_altid, number=10)

print(f"基础版 SM2 验签耗时: {basic_time:.4f} 秒 (标准ID, 短消息)")
print(f"基础版 SM2 验签耗时: {basic_long_time:.4f} 秒 (标准ID, 长消息)")
print(f"基础版 SM2 验签耗时: {basic_altid_time:.4f} 秒 (自定义ID, 短消息)")
print(f"优化版 SM2 验签耗时: {opt_time:.4f} 秒 (标准ID, 短消息)")
print(f"优化版 SM2 验签耗时: {opt_long_time:.4f} 秒 (标准ID, 长消息)")
print(f"优化版 SM2 验签耗时: {opt_altid_time:.4f} 秒 (自定义ID, 短消息)")
print(f"优化提升(短消息): {basic_time/opt_time:.2f}x")
print(f"优化提升(长消息): {basic_long_time/opt_long_time:.2f}x")
