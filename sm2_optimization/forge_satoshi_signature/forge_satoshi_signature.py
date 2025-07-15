

# 伪造中本聪签名的演示脚本
# 注意：这只是一个技术演示，我们无法真正获取中本聪的私钥。

import ecdsa
import hashlib
import base64

# 使用比特币的 secp256k1 曲线
curve = ecdsa.SECP256k1

# 1. 假设我们拥有了中本聪的私钥
# 这是一个虚构的私钥，仅用于演示目的。
# 真实的中本聪私钥是未知的。
satoshi_private_key_hex = "18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725"
satoshi_sk = ecdsa.SigningKey.from_string(bytes.fromhex(satoshi_private_key_hex), curve=curve)

# 2. 从私钥生成公钥
satoshi_vk = satoshi_sk.get_verifying_key()
print("===== “中本聪”的密钥对 (演示) =====")
print(f"“私钥”: {satoshi_sk.to_string().hex()}")
print(f"“公钥” (未压缩): {satoshi_vk.to_string().hex()}")

# 3. 定义要签名的消息
message = "I am Satoshi Nakamoto and I am back.".encode('utf-8')
print(f"\n要签名的消息: {message.decode('utf-8')}")

# 4. 对消息进行签名
# 比特币签名通常需要对消息哈希两次
hash1 = hashlib.sha256(message).digest()
hash2 = hashlib.sha256(hash1).digest()
signature = satoshi_sk.sign(hash2)

print(f"\n生成的签名 (Base64): {base64.b64encode(signature).decode('utf-8')}")

# 5. 验证签名
# 任何人都可以使用公钥、消息和签名来验证其有效性
print("\n===== 验证签名 =====")
try:
    # 同样，验证时也需要对消息进行两次哈希
    is_valid = satoshi_vk.verify(signature, hash2)
    if is_valid:
        print("[+] 验证成功！该签名确实是由对应的私钥生成的。")
        print("这意味着，如果这个私钥真的是中本聪的，那么这个签名就是有效的。")
    else:
        # 理论上，如果代码没错，这里不会执行
        print("[-] 验证失败。") 
except ecdsa.BadSignatureError:
    print("[-] 验证失败，签名无效。")

print("\n===== 结论 =====")
print("这个脚本演示了拥有私钥即可伪造任何签名的能力。")
print("由于我们无法获得真正的中本聪私钥，所以这仅仅是一个技术演示，而非真正的伪造。")
print("这也强调了保护私钥的极端重要性。")

