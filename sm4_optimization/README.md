# SM4算法软件实现与优化

## 项目概述

本项目实现了中国国家密码标准SM4对称加密算法，包含基础版本和优化版本两种实现，并提供了完整的性能测试和功能验证。

## 文件结构

```
sm4_optimization/
├── sm4_v0.py          # SM4基础实现版本
├── sm4_opt.py         # SM4优化实现版本
├── benchmark.py       # 性能基准测试
├── test_sm4.py        # 完整功能测试和演示
└── README.md         # 本文档
```

## SM4算法简介

SM4是中华人民共和国国家密码管理局发布的对称加密算法标准（GM/T 0002-2012），具有以下特点：
- 分组长度：128位
- 密钥长度：128位
- 加密轮数：32轮
- 采用非平衡Feistel结构

## 实现特性

### 1. 基础版本 (sm4_v0.py)
- 严格按照标准规范实现
- 包含完整的S盒、线性变换L和L'
- 支持128位分组加密和解密
- 代码清晰易懂，便于学习和验证

### 2. 优化版本 (sm4_opt.py)
- 使用查找表优化S盒变换和线性变换
- 预计算T变换和T'变换表
- 使用struct模块优化字节操作
- 性能提升约2.7倍

## 优化策略

### 1. 查找表优化
```python
# 为每个字节位置预计算T变换表
self.T_TABLE = [[0] * 256 for _ in range(4)]
for pos in range(4):
    for i in range(256):
        s = self.S_BOX[i]
        temp = s << (8 * (3 - pos))
        self.T_TABLE[pos][i] = temp ^ self._rotl(temp, 2) ^ self._rotl(temp, 10) ^ self._rotl(temp, 18) ^ self._rotl(temp, 24)
```

### 2. 快速变换
```python
def _fast_t_transform(self, word):
    return (
        self.T_TABLE[0][(word >> 24) & 0xFF] ^
        self.T_TABLE[1][(word >> 16) & 0xFF] ^
        self.T_TABLE[2][(word >> 8) & 0xFF] ^
        self.T_TABLE[3][word & 0xFF]
    )
```

### 3. 高效数据转换
```python
# 使用struct模块进行快速字节转换
x = list(struct.unpack('>4I', plaintext))
return struct.pack('>4I', x[3], x[2], x[1], x[0])
```

## 性能测试结果

| 测试次数 | 基础版本(秒) | 优化版本(秒) | gmssl标准库(秒) | 优化版本提升 | 相比标准库提升 |
|----------|-------------|-------------|----------------|-------------|----------------|
| 1,000    | 0.065       | 0.024       | 0.071          | 2.70x       | 2.96x          |
| 5,000    | 0.328       | 0.118       | 0.366          | 2.78x       | 3.10x          |
| 10,000   | 0.661       | 0.239       | 0.726          | 2.77x       | 3.04x          |
| 50,000   | 3.292       | 1.194       | 3.680          | 2.76x       | 3.08x          |

**性能分析:**
- 优化版本比基础版本快约2.8倍
- 优化版本比gmssl标准库快约3倍
- 在大数据量测试中性能优势更加明显
- 相比标准库的性能提升非常稳定，在3倍左右

## 标准测试向量验证

使用GM/T 0002-2012标准测试向量验证：
- 密钥: `0123456789ABCDEFFEDCBA9876543210`
- 明文: `0123456789ABCDEFFEDCBA9876543210`
- 期望密文: `681EDF34D206965E86B3E94F536E4246`

✅ 所有实现版本都通过标准测试向量验证

## 与标准库对比验证

与gmssl标准库对比验证结果：
- ✅ 基础版本与gmssl标准库结果完全一致
- ✅ 优化版本与gmssl标准库结果完全一致
- ✅ 加密结果: `681EDF34D206965E86B3E94F536E4246`
- ✅ 解密功能正确性验证通过

**安装gmssl进行对比验证:**
```bash
pip install gmssl
```

## 安全特性验证

### 1. 雪崩效应
明文变化1位，密文平均变化约50%的位，符合良好密码算法的雪崩效应要求。

### 2. 密钥敏感性
不同密钥对相同明文产生完全不同的密文。

### 3. 可逆性
所有加密操作都可以正确解密回原文。
```bash
1. 基本加密解密:
   原始消息: Hello, SM4!
   密钥:     e21f3956ba3617bd22483d08f4a0e299
   密文:     7f267a66fa5dd81c638d4ff920393c7e
   解密结果: Hello, SM4!

2. 密钥敏感性:
   明文:     54657374206d65737361676521212121
   密钥1:    5bfdafcb5690c3fe64961eed16a40ff6
   密文1:    0e1f9773cc21e25a01be60e168d70860
   密钥2:    6deb0d3a1ca9bd4eb85b345f40aae29a
   密文2:    f99544d02631c1880dc44525a6b4db48
   密文不同: 是

3. 雪崩效应 (明文1位变化):
   明文1:    0123456789abcdeffedcba9876543210
   明文2:    0123456789abcdeffedcba9876543211
   密文1:    681edf34d206965e86b3e94f536e4246
   密文2:    be9a2469307a96f9d33ddbed4cf39994
   不同位数: 67/128 (52.3%)
```

## 使用方法

### 基本加密解密
```python
from sm4_opt import SM4Optimized

# 创建SM4实例
sm4 = SM4Optimized()

# 16字节密钥和明文
key = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
plaintext = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'

# 加密
ciphertext = sm4.encrypt_block_optimized(plaintext, key)

# 解密
decrypted = sm4.decrypt_block_optimized(ciphertext, key)

assert decrypted == plaintext
```

### 性能测试
```bash
python benchmark.py
```

### 完整功能测试
```bash
python test_sm4.py
```

## 技术栈

- Python 3.7+
- struct模块（字节操作优化）
- time模块（性能测试）
- os模块（随机数生成）

## 参考标准

- GM/T 0002-2012《SM4分组密码算法》
- GB/T 32907-2016《信息安全技术 SM4分组密码算法》

---

本实现严格遵循国家标准。优化版本在保持算法正确性的前提下显著提升了性能，为实际部署提供了良好的基础。
