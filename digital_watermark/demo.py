#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of the separated watermark system
这个脚本展示了如何使用分离后的main.py和benchmark.py
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    print("数字水印系统分离后的使用示例")
    print("这个脚本将演示main.py和benchmark.py的主要功能")
    
    # 确保在正确的目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. 使用main.py进行基本的水印操作
    print("\n" + "="*80)
    print("第一部分：使用main.py进行基本水印操作")
    print("="*80)
    
    # 1.1 创建并添加水印
    run_command(
        "python main.py --mode add --image example.png --watermark 'DEMO2025' --output demo_watermarked.png --alpha 0.15",
        "向图像添加水印"
    )
    
    # 1.2 提取水印
    run_command(
        "python main.py --mode extract --image demo_watermarked.png --watermark 'DEMO2025'",
        "从图像提取水印"
    )
    
    # 1.3 完整测试
    run_command(
        "python main.py --mode test --image example.png --watermark 'DEMO2025' --alpha 0.15",
        "运行完整的水印测试（使用example.png）"
    )
    
    # 2. 使用benchmark.py进行性能分析
    print("\n" + "="*80)
    print("第二部分：使用benchmark.py进行性能分析")
    print("="*80)
    
    # 2.1 性能基准测试
    run_command(
        "python benchmark.py --test performance --watermark 'DEMO2025'",
        "嵌入性能基准测试"
    )
    
    # 2.2 Alpha值影响分析
    run_command(
        "python benchmark.py --test alpha --image example.png --watermark 'DEMO2025'",
        "Alpha值对水印质量和鲁棒性的影响分析（使用example.png）"
    )
    
    # 2.3 鲁棒性基准测试
    run_command(
        "python benchmark.py --test robustness --image example.png --watermark 'DEMO2025'",
        "完整鲁棒性基准测试（使用example.png）"
    )
    
    # 3. 总结
    print("\n" + "="*80)
    print("总结：文件分离的优势")
    print("="*80)
    print("""
    文件分离后的优势：
    
    1. main.py - 核心功能模块
       - 专注于水印的嵌入和提取核心算法
       - 提供基本的鲁棒性测试
       - 适合日常使用和集成到其他系统
    
    2. benchmark.py - 性能评估模块  
       - 专门用于性能测试和参数优化
       - 提供详细的图像质量分析
       - 生成可视化的基准测试报告
       - 适合研究和开发阶段的深度分析
    
    3. 模块化设计的好处：
       - 代码职责分离，更易维护
       - 可以独立使用各个模块
       - benchmark.py可以调用main.py的功能，避免代码重复
       - 更好的可扩展性
    """)
    
    # 检查生成的文件
    print("\n生成的文件:")
    files_to_check = [
        "demo_watermarked.png",
        "watermarked_image.png", 
        "watermark_benchmark_report.png",
        "robustness_test_report.png"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (未生成)")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    main()
