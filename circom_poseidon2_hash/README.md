# Poseidon2哈希零知识证明电路

本项目使用circom实现了Poseidon2哈希算法的零知识证明电路，支持Groth16证明系统。用户可以证明自己知道某个哈希值的原象，而无需泄露原象本身。

## 🎯 项目概述

- **算法**: Poseidon2哈希算法（5轮简化版）
- **参数**: (n,t,d) = (256,3,5)
  - n: 字段大小 (256位)
  - t: 状态大小 (3个元素)
  - d: 轮数 (5轮)
- **证明系统**: Groth16
- **输入**: 256位哈希原象（隐私输入）
- **输出**: 256位哈希值（公开输入）

## 📁 项目结构

```
circom_poseidon2_hash/
├── poseidon2.circom             # Poseidon2哈希算法核心实现
├── poseidon2_hash.circom        # 主电路文件
├── calculate_hash.js            # 哈希值计算脚本
├── generate_proof.js            # 证明生成脚本
├── package.json                 # 项目依赖配置
├── README.md                    # 项目说明文档
├── .gitignore                   # Git忽略文件
└── 编译生成文件/
    ├── poseidon2_hash.r1cs      # R1CS约束系统
    ├── poseidon2_hash.wasm      # WebAssembly文件
    ├── poseidon2_hash.sym       # 符号表文件
    ├── poseidon2_hash_js/       # JavaScript生成文件
    └── poseidon2_hash_cpp/      # C++生成文件
```

## 🚀 快速开始

### 1. 环境要求

- Node.js (版本 >= 16)
- npm 或 yarn
- circom (版本 >= 2.1.4)
- snarkjs

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/Smera1d0/2025_sdu_entrepreneurship_practice.git
cd circom_poseidon2_hash

# 安装依赖
npm install
```

### 3. 编译电路

```bash
npm run compile
```

这将生成以下文件：
- `poseidon2_hash.r1cs`: R1CS约束系统
- `poseidon2_hash.wasm`: WebAssembly文件
- `poseidon2_hash.sym`: 符号表文件

### 4. 设置可信设置

```bash
# 下载可信设置文件（如果还没有）
wget https://zkrepl.dev/powersOfTau28_hez_final_12.ptau

# 生成初始zkey
npm run setup

# 贡献随机性
npm run contribute

# 导出验证密钥
npm run export-verifier
```

### 5. 计算哈希值

```bash
npm run calculate-hash
```

这会运行多个测试用例，计算Poseidon2哈希值并保存到文件。

### 6. 生成证明

```bash
npm run generate-proof
```

### 7. 验证证明

```bash
npm run verify-proof
```

## 📖 详细使用方法

### 手动计算哈希值

```bash
npm run calculate-hash
```

脚本会计算以下测试用例的哈希值：
- 简单测试: ["123", "456"]
- 零值测试: ["0", "0"]  
- 大数测试: ["999999999", "888888888"]

计算结果会保存到对应的JSON文件中。

### 自定义输入

你可以修改 `generate_proof.js` 中的输入数据：

```javascript
const input = {
    preimage: ["你的输入1", "你的输入2"]
};
```

### 查看生成的文件

- `input.json`: 输入数据（原象和哈希值）
- `proof.json`: Groth16证明
- `public.json`: 公开信号
- `verification_key.json`: 验证密钥

## 🔧 技术实现

### 电路设计

#### 主电路 (poseidon2_hash.circom)

```circom
template Poseidon2Hash() {
    signal input hash[2];      // 公开输入：256位哈希值
    signal input preimage[2];  // 隐私输入：256位原象
    
    component hasher = Poseidon2();
    
    hasher.in[0] <== preimage[0];
    hasher.in[1] <== preimage[1];
    
    hasher.out[0] === hash[0];
    hasher.out[1] === hash[1];
}
```

#### Poseidon2实现 (poseidon2.circom)

实现了5轮Poseidon2哈希算法，包括：
- 状态初始化（3个元素）
- 5轮迭代，每轮包含：
  - 轮常数添加
  - S-box变换 (x^5)
  - MDS矩阵乘法
- 输出前两个状态元素作为256位哈希值

### 哈希计算脚本

`calculate_hash.js` 提供了与circom电路完全一致的JavaScript实现：

- 使用相同的有限字段算术
- 实现相同的5轮Poseidon2算法
- 支持BigInt大数运算
- 提供详细的中间步骤输出

### 证明生成流程

1. **输入准备**: 使用哈希计算脚本生成正确的哈希值
2. **电路编译**: 生成R1CS约束和WASM文件
3. **可信设置**: 生成和贡献zkey
4. **证明生成**: 使用Groth16算法生成证明
5. **证明验证**: 验证证明的有效性

## 📊 性能参数

- **约束数量**: 约150个约束
- **证明大小**: ~2KB
- **验证时间**: <1ms
- **生成时间**: 取决于输入复杂度

## 🔒 安全考虑

1. **轮数**: 当前使用5轮，适用于演示和学习
2. **参数**: 使用简化的轮常数和MDS矩阵
3. **字段**: 使用circom默认的BN254曲线
4. **可信设置**: 使用公开的可信设置文件

**注意**: 生产环境使用前需要：
- 增加轮数到标准值（如72轮）
- 使用完整的轮常数表
- 使用完整的MDS矩阵
- 进行独立的安全审计

## 🛠️ 开发指南

### 修改轮数

要修改轮数，需要：
1. 在 `poseidon2.circom` 中展开更多轮
2. 在 `calculate_hash.js` 中修改循环次数
3. 重新编译电路

### 修改状态大小

要支持不同的状态大小：
1. 修改状态数组大小
2. 调整MDS矩阵维度
3. 更新哈希计算脚本

### 添加新功能

1. 在电路中添加新的约束
2. 更新哈希计算脚本
3. 修改证明生成脚本
4. 更新测试用例

## 🐛 故障排除

### 常见问题

1. **编译错误**: 确保circom版本 >= 2.1.4
2. **证明生成失败**: 检查输入数据格式
3. **验证失败**: 确保使用正确的验证密钥
4. **内存不足**: 增加Node.js内存限制

### 调试技巧

1. 使用 `calculate-hash` 脚本验证哈希计算
2. 检查生成的JSON文件格式
3. 查看详细的错误信息
4. 验证文件路径和权限

## 📚 参考资料

- [Poseidon2论文](https://eprint.iacr.org/2023/323.pdf)
- [Circom官方文档](https://docs.circom.io/)
- [SnarkJS文档](https://github.com/iden3/snarkjs)
- [零知识证明基础](https://zkproof.org/)

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- Circom团队提供的优秀工具链
- SnarkJS的Groth16实现
- Poseidon2论文作者

---

**注意**: 本项目主要用于学习和研究目的。生产环境使用前请进行充分的安全评估。 