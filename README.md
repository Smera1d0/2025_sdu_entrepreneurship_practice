# 2025 SDU 创新创业实践项目

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/Smera1d0/2025_sdu_entrepreneurship_practice)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](README.md)
[![Architecture](https://img.shields.io/badge/arch-x86__64%20%7C%20ARM64-orange.svg)](README.md)

本仓库是为2025年山东大学创新创业实践课程开发的项目集合。

## 项目作者
- 姓名：密语
- 学号：202200460104
- 班级：网安 1 班




## 项目总览

| # | 项目名称 | 目录 | 描述 |
|---|---|---|---|
| 1 | SM4 算法的实现与优化 | [`sm4_optimization/`](./sm4_optimization/) | SM4 分组密码算法及其 GCM 工作模式的软件实现与性能优化。 |
| 2 | 基于数字水印的图片泄露检测 | [`digital_watermark/`](./digital_watermark/) | 一个健壮的图像水印系统，用于嵌入和提取隐藏数据以进行泄露检测。 |
| 3 | Circom 实现 Poseidon2 哈希电路 | [`circom_poseidon2_hash/`](./circom_poseidon2_hash/) | 使用 Circom 和 Groth16 实现 Poseidon2 哈希算法的零知识证明电路。 |
| 4 | SM3 算法的实现与优化 | [`sm3_optimization/`](./sm3_optimization/) | SM3 哈希函数的软件实现、优化及安全性分析。 |
| 5 | SM2 算法的实现与优化 | [`sm2_optimization/`](./sm2_optimization/) | 基于 Python 的 SM2 公钥密码系统的实现、优化和安全性分析。 |
| 6 | Google Password Checkup 协议实现 | [`DDH-based_Private_Intersection-Sum_Protocol/`](./DDH-based_Private_Intersection-Sum_Protocol/) | 对 Google Password Checkup 论文中基于 DDH 的私有交集求和协议的实现。 |

---

### 1. SM4 算法的实现与优化

**目录: [`sm4_optimization/`](./sm4_optimization/)**

本项目专注于国密 SM4 分组密码算法的软件实现和性能优化。

**主要内容:**
- **高性能核心:** 使用多种技术优化 SM4 算法，包括 T-table、AES-NI 以及最新的 CPU 指令集（如 GFNI、VPROLD 等）。
- **SM4-GCM 模式:** 基于高性能的 SM4 核心，实现并优化了 SM4-GCM 认证加密模式。

---

### 2. 基于数字水印的图片泄露检测

**目录: [`digital_watermark/`](./digital_watermark/)**

本项目实现了一个用于图像的数字水印系统，旨在追踪和检测未经授权的泄露。该实现基于开源项目进行了二次开发，并增强了其鲁棒性。

**主要内容:**
- **水印嵌入与提取:** 提供了在图像中嵌入和提取不可见水印（如二维码或文本）的工具。
- **鲁棒性测试:** 系统经过了多种图像处理攻击的严格测试，包括：
  - **几何攻击:** 翻转、旋转、缩放、裁剪、平移。
  - **信号处理攻击:** 对比度/亮度调整、高斯噪声、JPEG 压缩。
- **详细报告:** 包含了基准测试结果和鲁棒性测试报告。

---

### 3. Circom 实现 Poseidon2 哈希电路

**目录: [`circom_poseidon2_hash/`](./circom_poseidon2_hash/)**

本项目提供了一个基于 Circom 语言实现的 Poseidon2 哈希函数的零知识证明电路。它允许生成一个哈希原象的知识证明，而无需泄露该原象。

**主要内容:**
- **Poseidon2 实现:** 电路实现了 Poseidon2 哈希函数，参数为 `(n,t,d) = (256,3,5)` 或 `(256,2,5)`。
- **零知识证明电路:**
    - **隐私输入:** 哈希函数的原象。
    - **公开输入:** 计算得到的 Poseidon2 哈希值。
- **Groth16 证明系统:** 使用 Groth16 算法生成和验证紧凑的零知识证明。
- **参考文献:**
    - [Poseidon2 论文](https://eprint.iacr.org/2023/323.pdf)
    - [Circom 官方文档](https://docs.circom.io/)

---

### 4. SM3 算法的实现与优化

**目录: [`sm3_optimization/`](./sm3_optimization/)**

本项目专注于国密 SM3 密码哈希函数的软件实现和优化。

**主要内容:**
- **优化实现:** 从基础实现出发，应用高级优化技术，提升了 SM3 哈希函数的执行性能。
- **长度扩展攻击:** 包含了一个 PoC（概念验证），用于演示对使用 SM3 的朴素 MAC 结构的长度扩展攻击。
- **Merkle 树 (RFC 6962):**
    - 使用 SM3 哈希函数构建了一个包含 10 万个叶子节点的 Merkle 树。
    - 实现了为叶子节点生成和验证存在性证明（Inclusion Proof）和不存在性证明（Exclusion Proof）的逻辑。

---

### 5. SM2 算法的实现与优化

**目录: [`sm2_optimization/`](./sm2_optimization/)**

本项目提供了基于 Python 的 SM2 公钥密码系统实现，重点关注算法改进和常见误用的安全性分析。

**主要内容:**
- **Python 实现:** 一个清晰易懂的 SM2 算法实现，便于快速原型设计和算法实验。
- **误用漏洞分析 (PoC):**
    - 针对常见的签名算法误用场景，实现了 PoC 攻击。
    - 包含了详细的推导文档和对应的验证代码。
- **伪造中本聪签名:** 一个伪造中本聪风格数字签名的实践案例。

---

### 6. Google Password Checkup 协议实现

**目录: [`DDH-based_Private_Intersection-Sum_Protocol/`](./DDH-based_Private_Intersection-Sum_Protocol/)**

本项目实现了 Google Password Checkup 服务背后的核心密码学协议。该协议允许用户检查其凭据是否已泄露，而无需向 Google 透露这些凭据。

**主要内容:**
- **协议实现:** 实现了学术论文中图 2（第 3.1 节）所述的基于 DDH 的私有交集求和协议。
- **隐私保护:** 展示了如何利用私有集合交集（PSI）技术在真实世界的应用中实现强大的隐私保护。
- **参考文献:**
    - [Password Checkup 论文](https://eprint.iacr.org/2019/723.pdf)
