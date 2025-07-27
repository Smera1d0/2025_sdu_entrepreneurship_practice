# SM4算法软件实现与优化

## 项目概述

本项目实现了中国国家密码标准SM4对称加密算法，包含基础版本、T-table优化、C语言指令集优化三种实现，并提供了SM4-GCM工作模式的优化实现，以及完整的性能测试和功能验证。

## 文件结构

```
sm4_optimization/
├── sm4_v0.py          # SM4基础实现版本
├── sm4_ttable.py      # T-table查表优化版本
├── sm4_opt.py         # C语言/指令集优化版本（Python接口）
├── sm4_opt.c          # C语言高性能实现（可扩展AES-NI/GFNI/VPROLD等指令集）
├── sm4_gcm.py         # SM4-GCM模式实现
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

### 2. T-table查表优化 (sm4_ttable.py)
- 预计算T变换查找表，加速S盒和线性变换
- 查表法大幅减少循环和位运算，提高执行效率
- 性能优于基础实现

### 3. C语言/指令集优化 (sm4_opt.c/sm4_opt.py)
- 用C语言实现SM4核心加解密，极大提升性能
- 可扩展支持AES-NI、GFNI、VPROLD等现代指令集（当前为基础C实现，后续可补充）
- Python通过ctypes调用C动态库，兼容性好
- 性能远超纯Python实现

### 4. SM4-GCM模式 (sm4_gcm.py)
- 实现了基于SM4的GCM（Galois/Counter Mode）认证加密模式
- 支持三种SM4实现作为底层加密函数
- 提供高效的GHASH实现，支持AAD和认证标签
- 适合高安全性、高性能场景

## 优化策略

### 1. 查找表优化（T-table）
```python
# 预计算T变换表
self.T = [0] * 256
for i in range(256):
    s = self.S_BOX[i]
    t = s | (s << 8) | (s << 16) | (s << 24)
    t = self._linear_transform_l(t)
    self.T[i] = t
```

### 2. C语言/指令集优化
- 用C实现SM4核心轮函数和密钥扩展，充分利用底层算力
- 可扩展支持AES-NI、GFNI、VPROLD等指令集（如有需求可补充）
- Python通过ctypes调用，接口简单

### 3. GCM模式优化
- 采用自定义GHASH高效实现
- 支持任意长度AAD和密文
- 认证标签安全可靠

## 性能测试方法

```bash
python benchmark.py
```

输出示例：
```
=== SM4单块加密性能 ===
基础版本 10000次加密耗时: 0.66秒
T-table版本 10000次加密耗时: 0.24秒
C优化版本 10000次加密耗时: 0.08秒
T-table加速比: 2.75倍
C优化加速比: 8.25倍
结果一致性: 基础-Ttable: True, 基础-C: True

=== SM4-GCM模式性能 ===
GCM模式(base) 1000次加解密耗时: 0.95秒
GCM模式(ttable) 1000次加解密耗时: 0.38秒
GCM模式(opt) 1000次加解密耗时: 0.13秒
```

## SM4-GCM用法示例

```python
from sm4_gcm import SM4GCM
key = b'0123456789abcdef'
iv = b'123456789012'  # 12字节IV
plaintext = b'hello world, sm4-gcm!'
aad = b'header'

# 选择不同底层实现：base/ttable/opt
sm4gcm = SM4GCM(key, mode='opt')
ciphertext, tag = sm4gcm.encrypt(plaintext, iv, aad)
plain = sm4gcm.decrypt(ciphertext, iv, tag, aad)
assert plain == plaintext
```

## C语言库编译说明

```bash
# macOS/Linux
cc -shared -fPIC -o libsm4opt.dylib sm4_opt.c
# 或
gcc -shared -fPIC -o libsm4opt.so sm4_opt.c

# Windows
cl /LD sm4_opt.c /Fe:sm4opt.dll
```

## 依赖说明
- Python 3.7+
- 无需第三方库（GCM模式需自带GHASH实现，已内置）
- 性能对比可选安装gmssl: `pip install gmssl`

## 参考标准
- GM/T 0002-2012《SM4分组密码算法》
- GB/T 32907-2016《信息安全技术 SM4分组密码算法》
- NIST SP800-38D（GCM模式）

本实现严格遵循国家标准，支持多种优化方式和GCM认证加密模式，适合教学、科研和高性能工程应用。
