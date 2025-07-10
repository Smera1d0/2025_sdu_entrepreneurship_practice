# 数字水印系统使用说明

## 文件结构

- `main.py` - 核心水印系统，支持文字水印和图片水印的嵌入、提取功能
- `benchmark.py` - 性能基准测试系统，专门用于性能评估和深度分析
- ## 功能对比

| 功能 | main.py | benchmark.py |
|------|---------|--------------|
| 文字水印嵌入/提取 | ✓ 核心实现 | ✓ 调用main.py |
| 图片水印嵌入/提取 | ✓ 核心实现 | ✓ 调用main.py |
| 基本鲁棒性测试 | ✓ | ✓ |
| 文字水印性能基准测试 | ✗ | ✓ |
| 图片水印性能基准测试 | ✗ | ✓ |
| Alpha值优化分析 | ✗ | ✓ |
| 图像质量评估 | ✗ | ✓ |
| 可视化报告 | 基础 | 详细 |

## 水印类型对比

| 特性 | 文字水印 | 图片水印 |
|------|----------|----------|
| 信息容量 | 小 (几个字符) | 大 (数千像素) |
| 处理速度 | 快 | 相对较慢 |
| 应用场景 | 版权标识、认证 | 品牌Logo、QR码 |
| 提取复杂度 | 低 | 中等 |
| 存储需求 | 低 | 高 |
| 视觉效果 | 文本信息 | 图像内容 |ermark_demo.py` - 图片水印功能演示脚本

## 基本使用

### 1. 使用main.py进行基本操作

#### 添加文字水印
```bash
python main.py --mode add --image input.png --watermark "SDU2025" --output watermarked.png --alpha 0.1
```

#### 提取文字水印
```bash
python main.py --mode extract --image watermarked.png --watermark "SDU2025"
```

#### 添加图片水印
```bash
python main.py --mode add-image --image input.png --watermark-image QRcode.png --output watermarked.png --watermark-size 32 32 --alpha 0.15
```

#### 提取图片水印
```bash
python main.py --mode extract-image --image watermarked.png --output extracted_watermark.png
```

#### 完整测试（包含鲁棒性测试）
```bash
# 使用默认的example.png进行测试
python main.py --mode test --watermark "SDU2025" --alpha 0.1

# 或者指定特定图像
python main.py --mode test --image your_image.png --watermark "SDU2025" --alpha 0.1
```

### 2. 使用benchmark.py进行性能测试

#### 运行所有基准测试
```bash
# 使用默认的example.png
python benchmark.py --test all --watermark "SDU2025"

# 或者指定特定图像
python benchmark.py --test all --image your_image.png --watermark "SDU2025"
```

#### 仅测试文字水印嵌入性能
```bash
python benchmark.py --test performance --watermark "SDU2025"
```

#### 仅测试图片水印嵌入性能
```bash
python benchmark.py --test image-performance --watermark-image QRcode.png
```

#### 仅测试Alpha值影响
```bash
python benchmark.py --test alpha --watermark "SDU2025"
```

#### 仅测试鲁棒性
```bash
python benchmark.py --test robustness --watermark "SDU2025"
```

### 3. 运行演示脚本

#### 运行图片水印演示
```bash
python image_watermark_demo.py
```

## 参数说明

### main.py参数
- `--mode`: 运行模式 (add/extract/test/add-image/extract-image)
- `--image`: 输入图像路径
- `--watermark`: 水印文本 (默认: "SDU2025")
- `--watermark-image`: 水印图像路径 (用于图片水印)
- `--output`: 输出路径
- `--alpha`: 水印强度 (默认: 0.1)
- `--watermark-size`: 水印图像尺寸 [宽度 高度] (默认: 32 32)

### benchmark.py参数
- `--test`: 测试类型 (performance/alpha/robustness/image-performance/all)
- `--image`: 测试图像路径
- `--watermark`: 水印文本 (默认: "SDU2025")
- `--watermark-image`: 水印图像路径 (默认: "QRcode.png")
- `--output-dir`: 结果输出目录 (默认: "benchmark_results")

## 输出文件

### main.py输出
- `watermarked_image.png` - 含水印的图像
- `robustness_test_results/` - 鲁棒性测试攻击后的图像
- `robustness_test_report.png` - 鲁棒性测试可视化报告

### benchmark.py输出
- `watermark_benchmark_report.png` - 性能基准测试报告
- `benchmark_robustness_results/` - 基准测试中的鲁棒性结果

## 功能对比

| 功能 | main.py | benchmark.py |
|------|---------|--------------|
| 水印嵌入/提取 | ✓ | ✓ (调用main.py) |
| 鲁棒性测试 | ✓ | ✓ |
| 性能基准测试 | ✗ | ✓ |
| Alpha值优化分析 | ✗ | ✓ |
| 图像质量评估 | ✗ | ✓ |
| 详细性能报告 | ✗ | ✓ |

## 建议的使用流程

1. 首先使用 `main.py` 进行基本的水印嵌入和提取测试
2. 使用 `benchmark.py` 进行详细的性能评估和参数优化
3. 根据benchmark结果选择最优的alpha值
4. 在实际应用中使用优化后的参数运行 `main.py`
