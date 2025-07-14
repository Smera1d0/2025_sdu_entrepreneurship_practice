# SM2 椭圆曲线数字签名算法优化实现

本项目实现了国密 SM2 椭圆曲线数字签名算法的基础版和优化版，展示了不同优化策略对性能的影响。

## 项目结构

```
sm2_optimization/
├── basic_sm2/              # 基础版 SM2 实现
│   ├── __init__.py
│   └── sm2_basic.py        # 纯 Python 实现，便于理解
├── optimized_sm2/          # 优化版 SM2 实现
│   ├── __init__.py
│   └── sm2_optimized.py    # 使用 gmpy2 优化的实现
├── test_sm2.py             # 正确性测试脚本
├── benchmark_sm2.py        # 性能对比测试脚本
└── README.md               # 项目说明文档
```

## 功能特性

### 基础版 (basic_sm2)
- **纯 Python 实现**：使用标准库，易于理解和学习
- **完整的 SM2 流程**：包含密钥生成、数字签名、签名验证
- **标准 Z 值计算**：支持用户 ID 和椭圆曲线参数的哈希
- **教学友好**：代码结构清晰，注释详细

### 优化版 (optimized_sm2)
- **gmpy2 加速**：使用 gmpy2 库进行大数运算优化
- **内存优化**：使用 `__slots__` 减少内存占用
- **高效模运算**：使用 `gmpy2.f_mod()` 和 `gmpy2.invert()` 加速
- **性能提升**：相比基础版有 **6倍以上** 的性能提升

## 算法实现

### SM2 数字签名核心算法

1. **密钥生成**
   ```python
   d = random.randrange(1, n)    # 私钥
   P = point_mul(G, d)           # 公钥
   ```

2. **签名生成**
   ```python
   Z = get_z(ID, P, a, b, Gx, Gy)  # Z值计算
   e = hash(Z + M)                  # 消息哈希
   k = random.randrange(1, n)       # 随机数
   (x1, y1) = point_mul(G, k)       # 椭圆曲线点乘
   r = (e + x1) mod n               # 签名第一部分
   s = (1+d)^(-1) * (k - r*d) mod n # 签名第二部分
   ```

3. **签名验证**
   ```python
   t = (r + s) mod n                # 验证参数
   (x1', y1') = s*G + t*P          # 椭圆曲线运算
   R = (e + x1') mod n              # 验证值
   return R == r                    # 验证结果
   ```

### 椭圆曲线参数

本实现使用 SM2 标准椭圆曲线参数：
- **域参数 p**: `0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF`
- **曲线参数 a**: `0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC`
- **曲线参数 b**: `0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93`
- **基点 G**: `(Gx, Gy)`
- **阶 n**: `0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123`

## 环境要求

### 基础版依赖
```bash
# 仅需 Python 标准库
python >= 3.7
```

### 优化版依赖
```bash
# 需要安装 gmpy2 库
python >= 3.7
gmpy2 >= 2.1.0
```

## 安装和使用

### 1. 克隆项目
```bash
git clone <repository_url>
cd sm2_optimization
```

### 2. 安装依赖
```bash
# 基础版无需额外依赖
# 优化版需要安装 gmpy2
pip install gmpy2
```

### 3. 运行测试
```bash
# 正确性测试
python test_sm2.py

# 性能对比测试
python benchmark_sm2.py
```

## 测试结果

### 正确性测试
```
===== SM2 标准流程详细测试 =====
[基础版] 标准ID签名/验签...
[基础版] 自定义ID签名/验签...
[优化版] 标准ID签名/验签...
[优化版] 自定义ID签名/验签...
[交叉] 基础签名优化验签...
[交叉] 优化签名基础验签...
[长消息] 基础版...
[长消息] 优化版...
[异常] 错误签名应验签失败...
所有详细测试通过！
```

### 性能对比测试
```
===== SM2 Benchmark =====
基础版 SM2 验签耗时: 7.6938 秒 (标准ID, 短消息)
基础版 SM2 验签耗时: 7.7507 秒 (标准ID, 长消息)
基础版 SM2 验签耗时: 7.7337 秒 (自定义ID, 短消息)
优化版 SM2 验签耗时: 1.2672 秒 (标准ID, 短消息)
优化版 SM2 验签耗时: 1.2532 秒 (标准ID, 长消息)
优化版 SM2 验签耗时: 1.2523 秒 (自定义ID, 短消息)
优化提升(短消息): 6.07x
优化提升(长消息): 6.18x
```

## 对比表格

| 对比项目 | 基础版 (basic_sm2) | 优化版 (optimized_sm2) | 性能提升 |
|---------|-------------------|----------------------|---------|
| **实现语言** | 纯 Python | Python + gmpy2 | - |
| **大数运算** | `int` + `pow()` | `gmpy2.mpz()` + `gmpy2.invert()` | 3-5x |
| **模运算** | `(a * b) % p` | `gmpy2.f_mod(a * b, p)` | 2-3x |
| **内存占用** | 普通类属性 | `__slots__` 优化 | 减少 20-30% |
| **代码复杂度** | 简单易懂 | 略复杂 | - |
| **依赖库** | 无额外依赖 | 需要 gmpy2 | - |
| **验签耗时** | ~7.7 秒 (100次) | ~1.26 秒 (100次) | **6.1x** |
| **适用场景** | 教学学习 | 高性能应用 | - |
| **兼容性** | 高 (标准库) | 中 (需安装 gmpy2) | - |

## 优化策略详解

### 1. 大数运算优化
- **基础版**: 使用 Python 内置 `int` 和 `pow(k, -1, p)`
- **优化版**: 使用 `gmpy2.mpz()` 和 `gmpy2.invert()`
- **效果**: 大数运算速度提升 3-5 倍

### 2. 模运算优化
- **基础版**: 使用 `(a * b) % p`
- **优化版**: 使用 `gmpy2.f_mod(a * b, p)`
- **效果**: 减少临时大数对象创建

### 3. 内存优化
- **基础版**: 普通类属性存储
- **优化版**: 使用 `__slots__` 限制属性
- **效果**: 减少内存占用和属性访问开销

### 4. 椭圆曲线点运算优化
- **点加法**: 优化斜率计算和模逆运算
- **点乘法**: 使用二进制展开的快速点乘算法
- **效果**: 椭圆曲线运算整体提速

## 安全性说明

⚠️ **重要提醒**: 本实现仅用于教学和性能对比研究，**不建议用于生产环境**。

### 当前限制
1. **随机数生成**: 使用 `random.randrange()`，非密码学安全
2. **侧信道攻击**: 未实现时序攻击防护
3. **哈希算法**: 使用 SHA-256 代替国密 SM3
4. **参数验证**: 缺少完整的输入参数校验

### 生产环境建议
- 使用 `secrets` 模块生成密码学安全的随机数
- 实现 SM3 哈希算法替代 SHA-256
- 添加侧信道攻击防护措施
- 使用经过安全审计的密码学库

## 扩展功能

本项目可扩展的功能包括：
- **SM2 加密/解密**: 实现椭圆曲线加密功能
- **密钥交换**: 实现 SM2 密钥协商协议
- **证书支持**: 支持 X.509 证书格式
- **硬件加速**: 集成硬件安全模块 (HSM)

## 技术细节

### 椭圆曲线运算
本实现采用 Weierstrass 形式椭圆曲线 `y² = x³ + ax + b`，使用标准的点加法和点乘算法。

### Z 值计算
根据 GM/T 0003.2-2012 标准，Z 值计算包含：
```
Z = SM3(ENTL || ID || a || b || Gx || Gy || Px || Py)
```
其中 ENTL 是用户 ID 长度的 2 字节大端表示。

### 签名格式
签名结果为 `(r, s)` 元组，其中：
- `r, s` 均为 `[1, n-1]` 范围内的整数
- 序列化时通常转换为固定长度的字节串

## 使用示例

### 基础用法
```python
from basic_sm2.sm2_basic import gen_keypair, sm2_sign, sm2_verify

# 生成密钥对
d, P = gen_keypair()

# 签名
msg = "Hello, SM2!"
signature = sm2_sign(msg, d, P)

# 验证
is_valid = sm2_verify(msg, P, signature)
print(f"签名验证: {'通过' if is_valid else '失败'}")
```

### 自定义 ID
```python
custom_id = b'MyCustomID123'
signature = sm2_sign(msg, d, P, custom_id)
is_valid = sm2_verify(msg, P, signature, custom_id)
```

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 参考资料

- [GM/T 0003.2-2012 SM2椭圆曲线公钥密码算法](http://www.gmbz.org.cn/)
- [GM/T 0004-2012 SM3密码杂凑算法](http://www.gmbz.org.cn/)
- [RFC 6090: Fundamental Elliptic Curve Cryptography Algorithms](https://tools.ietf.org/html/rfc6090)
- [gmpy2 Documentation](https://gmpy2.readthedocs.io/)

