#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Watermark with Image Support Demo
演示支持图片水印的数字水印系统的使用
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
    print("数字水印系统 - 支持图片水印功能演示")
    print("这个脚本将演示文字水印和图片水印的功能")
    
    # 确保在正确的目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 第一部分：文字水印演示
    print("\n" + "="*80)
    print("第一部分：文字水印功能演示")
    print("="*80)
    
    # 1.1 添加文字水印
    run_command(
        "python main.py --mode add --image example.png --watermark 'DEMO2025' --output text_watermarked.png --alpha 0.15",
        "向图像添加文字水印"
    )
    
    # 1.2 提取文字水印
    run_command(
        "python main.py --mode extract --image text_watermarked.png --watermark 'DEMO2025'",
        "从图像提取文字水印"
    )
    
    # 第二部分：图片水印演示
    print("\n" + "="*80)
    print("第二部分：图片水印功能演示")
    print("="*80)
    
    # 2.1 添加图片水印
    run_command(
        "python main.py --mode add-image --image example.png --watermark-image QRcode.png --output image_watermarked.png --watermark-size 24 24 --alpha 0.2",
        "向图像添加QR码图片水印"
    )
    
    # 2.2 提取图片水印
    run_command(
        "python main.py --mode extract-image --image image_watermarked.png --output extracted_qr_demo.png",
        "从图像提取QR码水印"
    )
    
    # 第三部分：性能基准测试
    print("\n" + "="*80)
    print("第三部分：性能基准测试")
    print("="*80)
    
    # 3.1 文字水印性能测试
    run_command(
        "python benchmark.py --test performance --watermark 'DEMO2025'",
        "文字水印性能基准测试"
    )
    
    # 3.2 图片水印性能测试
    run_command(
        "python benchmark.py --test image-performance --watermark-image QRcode.png",
        "图片水印性能基准测试"
    )
    
    # 第四部分：功能对比和总结
    print("\n" + "="*80)
    print("第四部分：功能对比和总结")
    print("="*80)
    print("""
    功能对比总结：
    
    1. 文字水印 vs 图片水印：
       
       文字水印：
       ✓ 容量小，速度快
       ✓ 适合版权标识、认证信息
       ✓ 提取简单，错误率低
       ✓ 适合简短信息传递
       
       图片水印：
       ✓ 信息容量大
       ✓ 可嵌入QR码、Logo等复杂图像
       ✓ 视觉化信息传递
       ✓ 适合品牌标识、复杂数据
    
    2. 性能特点：
       - 文字水印处理速度更快
       - 图片水印需要更多存储空间
       - 两种方式都支持盲提取
       - 鲁棒性取决于alpha参数设置
    
    3. 应用场景：
       - 文字水印：数字版权保护、身份验证
       - 图片水印：品牌宣传、防伪标识、信息隐藏
    """)
    
    # 检查生成的文件
    print("\n生成的文件:")
    files_to_check = [
        "text_watermarked.png",
        "image_watermarked.png", 
        "extracted_qr_demo.png",
        "watermark_benchmark_report.png"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (未生成)")
    
    print("\n演示完成！现在你可以使用以下命令:")
    print("\n文字水印:")
    print("  添加: python main.py --mode add --image input.png --watermark 'YOUR_TEXT' --output output.png")
    print("  提取: python main.py --mode extract --image watermarked.png --watermark 'YOUR_TEXT'")
    
    print("\n图片水印:")
    print("  添加: python main.py --mode add-image --image input.png --watermark-image logo.png --output output.png --watermark-size 32 32")
    print("  提取: python main.py --mode extract-image --image watermarked.png --output extracted_logo.png")
    
    print("\n性能测试:")
    print("  文字水印: python benchmark.py --test performance")
    print("  图片水印: python benchmark.py --test image-performance")

if __name__ == "__main__":
    main()
