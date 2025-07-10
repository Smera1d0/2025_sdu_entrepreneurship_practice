#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Watermark Benchmark System
Performance testing and evaluation for the blind watermarking system
"""

import time
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from main import BlindWatermark, RobustnessTest, create_sample_image
import argparse


class WatermarkBenchmark:
    def __init__(self):
        self.results = []
    
    def benchmark_embedding_performance(self, image_sizes, watermark_text="SDU2025", alpha=0.1):
        """
        测试不同图像尺寸下的水印嵌入性能
        
        Args:
            image_sizes (list): 图像尺寸列表 [(width, height), ...]
            watermark_text (str): 水印文本
            alpha (float): 水印强度
        """
        print("=== Watermark Embedding Performance Benchmark ===")
        
        watermark_system = BlindWatermark(alpha=alpha)
        embedding_results = []
        
        for size in image_sizes:
            width, height = size
            print(f"\nTesting image size: {width}x{height}")
            
            # 创建测试图像
            test_image = f"test_{width}x{height}.png"
            create_sample_image(width, height, test_image)
            
            # 测试嵌入时间
            start_time = time.time()
            output_path = f"watermarked_{width}x{height}.png"
            
            try:
                watermark_system.add_watermark(test_image, watermark_text, output_path)
                embedding_time = time.time() - start_time
                
                # 验证提取
                extracted = watermark_system.extract_watermark(output_path, len(watermark_text))
                extraction_success = extracted == watermark_text
                
                # 计算图像质量指标
                psnr, ssim = self._calculate_image_quality(test_image, output_path)
                
                result = {
                    'size': f"{width}x{height}",
                    'width': width,
                    'height': height,
                    'pixels': width * height,
                    'embedding_time': embedding_time,
                    'extraction_success': extraction_success,
                    'psnr': psnr,
                    'ssim': ssim,
                    'extracted_text': extracted
                }
                
                embedding_results.append(result)
                
                print(f"  Embedding time: {embedding_time:.3f}s")
                print(f"  Extraction success: {extraction_success}")
                print(f"  PSNR: {psnr:.2f} dB")
                print(f"  SSIM: {ssim:.4f}")
                
                # 清理临时文件
                os.remove(test_image)
                os.remove(output_path)
                
            except Exception as e:
                print(f"  Error: {str(e)}")
                embedding_results.append({
                    'size': f"{width}x{height}",
                    'width': width,
                    'height': height,
                    'pixels': width * height,
                    'embedding_time': float('inf'),
                    'extraction_success': False,
                    'psnr': 0,
                    'ssim': 0,
                    'extracted_text': 'ERROR'
                })
        
        self.results.extend(embedding_results)
        return embedding_results
    
    def benchmark_alpha_values(self, alpha_values, image_path=None, watermark_text="SDU2025"):
        """
        测试不同alpha值对水印质量和鲁棒性的影响
        
        Args:
            alpha_values (list): alpha值列表
            image_path (str): 测试图像路径，如果为None则使用example.png
            watermark_text (str): 水印文本
        """
        print("\n=== Alpha Values Impact Benchmark ===")
        
        if image_path is None:
            if os.path.exists("example.png"):
                image_path = "example.png"
                print("Using example.png as test image")
            else:
                image_path = create_sample_image()
                print("example.png not found, creating sample image")
        
        alpha_results = []
        
        for alpha in alpha_values:
            print(f"\nTesting alpha = {alpha}")
            
            watermark_system = BlindWatermark(alpha=alpha)
            output_path = f"watermarked_alpha_{alpha}.png"
            
            try:
                # 嵌入水印
                start_time = time.time()
                watermark_system.add_watermark(image_path, watermark_text, output_path)
                embedding_time = time.time() - start_time
                
                # 提取验证
                extracted = watermark_system.extract_watermark(output_path, len(watermark_text))
                extraction_success = extracted == watermark_text
                
                # 图像质量
                psnr, ssim = self._calculate_image_quality(image_path, output_path)
                
                # 鲁棒性测试（简化版）
                robustness_test = RobustnessTest(watermark_system)
                robustness_score = self._quick_robustness_test(robustness_test, output_path, watermark_text)
                
                result = {
                    'alpha': alpha,
                    'embedding_time': embedding_time,
                    'extraction_success': extraction_success,
                    'psnr': psnr,
                    'ssim': ssim,
                    'robustness_score': robustness_score,
                    'extracted_text': extracted
                }
                
                alpha_results.append(result)
                
                print(f"  Embedding time: {embedding_time:.3f}s")
                print(f"  Extraction success: {extraction_success}")
                print(f"  PSNR: {psnr:.2f} dB")
                print(f"  SSIM: {ssim:.4f}")
                print(f"  Robustness score: {robustness_score:.2%}")
                
                # 清理
                os.remove(output_path)
                
            except Exception as e:
                print(f"  Error: {str(e)}")
                alpha_results.append({
                    'alpha': alpha,
                    'embedding_time': float('inf'),
                    'extraction_success': False,
                    'psnr': 0,
                    'ssim': 0,
                    'robustness_score': 0,
                    'extracted_text': 'ERROR'
                })
        
        self.results.extend(alpha_results)
        return alpha_results
    
    def benchmark_full_robustness(self, image_path=None, watermark_text="SDU2025", alpha=0.1):
        """
        完整的鲁棒性基准测试
        
        Args:
            image_path (str): 测试图像路径，如果为None则使用example.png
            watermark_text (str): 水印文本
            alpha (float): 水印强度
        """
        print("\n=== Full Robustness Benchmark ===")
        
        if image_path is None:
            if os.path.exists("example.png"):
                image_path = "example.png"
                print("Using example.png as test image")
            else:
                image_path = create_sample_image()
                print("example.png not found, creating sample image")
        
        watermark_system = BlindWatermark(alpha=alpha)
        watermarked_path = "benchmark_watermarked.png"
        
        # 嵌入水印
        watermark_system.add_watermark(image_path, watermark_text, watermarked_path)
        
        # 运行鲁棒性测试
        robustness_test = RobustnessTest(watermark_system)
        test_results = robustness_test.run_all_tests(
            watermarked_path, watermark_text, "benchmark_robustness_results"
        )
        
        # 清理
        os.remove(watermarked_path)
        
        return test_results
    
    def benchmark_image_watermark_performance(self, image_sizes, watermark_image_path="QRcode.png", alpha=0.1):
        """
        测试图片水印在不同图像尺寸下的性能
        
        Args:
            image_sizes (list): 图像尺寸列表 [(width, height), ...]
            watermark_image_path (str): 水印图像路径
            alpha (float): 水印强度
        """
        print("=== Image Watermark Performance Benchmark ===")
        
        if not os.path.exists(watermark_image_path):
            print(f"Warning: Watermark image {watermark_image_path} not found, skipping image watermark test")
            return []
        
        watermark_system = BlindWatermark(alpha=alpha)
        embedding_results = []
        
        # 不同的水印尺寸
        watermark_sizes = [(16, 16), (24, 24), (32, 32)]
        
        for size in image_sizes:
            width, height = size
            print(f"\nTesting image size: {width}x{height}")
            
            # 创建测试图像
            test_image = f"test_{width}x{height}.png"
            create_sample_image(width, height, test_image)
            
            for wm_size in watermark_sizes:
                print(f"  Watermark size: {wm_size[0]}x{wm_size[1]}")
                
                # 测试嵌入时间
                start_time = time.time()
                output_path = f"watermarked_img_{width}x{height}_wm_{wm_size[0]}x{wm_size[1]}.png"
                
                try:
                    watermark_system.add_image_watermark(test_image, watermark_image_path, output_path, wm_size)
                    embedding_time = time.time() - start_time
                    
                    # 验证提取
                    extracted_path = f"extracted_wm_{width}x{height}_{wm_size[0]}x{wm_size[1]}.png"
                    extracted_img = watermark_system.extract_image_watermark(output_path, extracted_path)
                    
                    # 计算图像质量指标
                    psnr, ssim = self._calculate_image_quality(test_image, output_path)
                    
                    # 计算水印相似度
                    original_wm = cv2.imread(watermark_image_path, cv2.IMREAD_GRAYSCALE)
                    original_wm_resized = cv2.resize(original_wm, wm_size)
                    watermark_similarity = self._calculate_watermark_similarity(original_wm_resized, extracted_img)
                    
                    result = {
                        'size': f"{width}x{height}",
                        'watermark_size': f"{wm_size[0]}x{wm_size[1]}",
                        'width': width,
                        'height': height,
                        'pixels': width * height,
                        'wm_pixels': wm_size[0] * wm_size[1],
                        'embedding_time': embedding_time,
                        'psnr': psnr,
                        'ssim': ssim,
                        'watermark_similarity': watermark_similarity
                    }
                    
                    embedding_results.append(result)
                    
                    print(f"    Embedding time: {embedding_time:.3f}s")
                    print(f"    PSNR: {psnr:.2f} dB")
                    print(f"    SSIM: {ssim:.4f}")
                    print(f"    Watermark similarity: {watermark_similarity:.4f}")
                    
                    # 清理临时文件
                    os.remove(output_path)
                    os.remove(extracted_path)
                    
                except Exception as e:
                    print(f"    Error: {str(e)}")
                    embedding_results.append({
                        'size': f"{width}x{height}",
                        'watermark_size': f"{wm_size[0]}x{wm_size[1]}",
                        'width': width,
                        'height': height,
                        'pixels': width * height,
                        'wm_pixels': wm_size[0] * wm_size[1],
                        'embedding_time': float('inf'),
                        'psnr': 0,
                        'ssim': 0,
                        'watermark_similarity': 0
                    })
            
            # 清理测试图像
            os.remove(test_image)
        
        self.results.extend(embedding_results)
        return embedding_results
    
    def _calculate_image_quality(self, original_path, watermarked_path):
        """计算图像质量指标：PSNR和SSIM"""
        try:
            # 读取图像
            img1 = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE).astype(np.float64)
            img2 = cv2.imread(watermarked_path, cv2.IMREAD_GRAYSCALE).astype(np.float64)
            
            # 计算PSNR
            mse = np.mean((img1 - img2) ** 2)
            if mse == 0:
                psnr = float('inf')
            else:
                psnr = 20 * np.log10(255.0 / np.sqrt(mse))
            
            # 简化的SSIM计算
            mu1 = np.mean(img1)
            mu2 = np.mean(img2)
            sigma1 = np.var(img1)
            sigma2 = np.var(img2)
            sigma12 = np.mean((img1 - mu1) * (img2 - mu2))
            
            c1 = (0.01 * 255) ** 2
            c2 = (0.03 * 255) ** 2
            
            ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
                   ((mu1**2 + mu2**2 + c1) * (sigma1 + sigma2 + c2))
            
            return psnr, ssim
            
        except Exception as e:
            print(f"Error calculating image quality: {e}")
            return 0, 0
    
    def _quick_robustness_test(self, robustness_test, watermarked_path, watermark_text):
        """快速鲁棒性测试（几个关键攻击）"""
        quick_tests = [
            ("JPEG_50", robustness_test.compress_jpeg, {"quality": 50}),
            ("Noise", robustness_test.add_noise, {"noise_level": 25}),
            ("Scale", robustness_test.resize, {"scale": 0.7}),
            ("Rotation", robustness_test.rotate, {"angle": 45})
        ]
        
        success_count = 0
        temp_dir = "temp_quick_test"
        os.makedirs(temp_dir, exist_ok=True)
        
        for test_name, test_func, params in quick_tests:
            try:
                attacked_path = os.path.join(temp_dir, f"{test_name}.png")
                test_func(watermarked_path, attacked_path, **params)
                
                extracted = robustness_test.watermark_system.extract_watermark(
                    attacked_path, len(watermark_text)
                )
                
                if extracted == watermark_text:
                    success_count += 1
                
                os.remove(attacked_path)
                
            except Exception:
                pass
        
        # 清理临时目录
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        return success_count / len(quick_tests)
    
    def _calculate_watermark_similarity(self, original, extracted):
        """计算水印相似度"""
        try:
            # 确保尺寸相同
            if original.shape != extracted.shape:
                extracted = cv2.resize(extracted, (original.shape[1], original.shape[0]))
            
            # 二值化
            _, orig_binary = cv2.threshold(original, 127, 1, cv2.THRESH_BINARY)
            _, extr_binary = cv2.threshold(extracted, 127, 1, cv2.THRESH_BINARY)
            
            # 计算匹配的像素比例
            correct_pixels = np.sum(orig_binary == extr_binary)
            total_pixels = orig_binary.size
            
            return correct_pixels / total_pixels
        except Exception:
            return 0.0
    
    def generate_benchmark_report(self):
        """生成基准测试报告"""
        if not self.results:
            print("No benchmark results to report")
            return
        
        # 创建可视化报告
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 嵌入时间 vs 图像尺寸
        embedding_results = [r for r in self.results if 'pixels' in r and r['embedding_time'] != float('inf')]
        if embedding_results:
            pixels = [r['pixels'] for r in embedding_results]
            times = [r['embedding_time'] for r in embedding_results]
            
            if len(pixels) == len(times) and len(times) > 0:
                axes[0,0].scatter(pixels, times)
                axes[0,0].set_xlabel('Image Size (pixels)')
                axes[0,0].set_ylabel('Embedding Time (seconds)')
                axes[0,0].set_title('Embedding Performance vs Image Size')
                axes[0,0].grid(True)
        
        # 2. Alpha值对PSNR的影响
        alpha_results = [r for r in self.results if 'alpha' in r and r['psnr'] > 0]
        if alpha_results:
            alphas = [r['alpha'] for r in alpha_results]
            psnrs = [r['psnr'] for r in alpha_results]
            
            if len(alphas) == len(psnrs) and len(psnrs) > 0:
                axes[0,1].plot(alphas, psnrs, 'o-')
                axes[0,1].set_xlabel('Alpha Value')
                axes[0,1].set_ylabel('PSNR (dB)')
                axes[0,1].set_title('Image Quality vs Watermark Strength')
                axes[0,1].grid(True)
        
        # 3. Alpha值对鲁棒性的影响
        if alpha_results:
            robustness_scores = [r['robustness_score'] for r in alpha_results if 'robustness_score' in r]
            alphas_robust = [r['alpha'] for r in alpha_results if 'robustness_score' in r]
            
            if len(alphas_robust) == len(robustness_scores) and len(robustness_scores) > 0:
                axes[1,0].plot(alphas_robust, robustness_scores, 'o-', color='orange')
                axes[1,0].set_xlabel('Alpha Value')
                axes[1,0].set_ylabel('Robustness Score')
                axes[1,0].set_title('Robustness vs Watermark Strength')
                axes[1,0].grid(True)
        
        # 4. 水印相似度分布（如果有图片水印结果）
        image_wm_results = [r for r in self.results if 'watermark_similarity' in r and r['watermark_similarity'] > 0]
        if image_wm_results:
            similarities = [r['watermark_similarity'] for r in image_wm_results]
            wm_sizes = [r['watermark_size'] if 'watermark_size' in r else 'Unknown' for r in image_wm_results]
            
            # 创建直方图
            axes[1,1].hist(similarities, bins=10, alpha=0.7, color='green')
            axes[1,1].set_xlabel('Watermark Similarity')
            axes[1,1].set_ylabel('Frequency')
            axes[1,1].set_title('Image Watermark Similarity Distribution')
            axes[1,1].grid(True)
        else:
            # 如果没有图片水印结果，显示PSNR vs SSIM散点图
            all_results = [r for r in self.results if 'psnr' in r and 'ssim' in r and r['psnr'] > 0 and r['ssim'] > 0]
            if all_results:
                psnrs = [r['psnr'] for r in all_results]
                ssims = [r['ssim'] for r in all_results]
                
                if len(psnrs) == len(ssims) and len(psnrs) > 0:
                    axes[1,1].scatter(psnrs, ssims)
                    axes[1,1].set_xlabel('PSNR (dB)')
                    axes[1,1].set_ylabel('SSIM')
                    axes[1,1].set_title('Image Quality Metrics Correlation')
                    axes[1,1].grid(True)
        
        plt.tight_layout()
        plt.savefig('watermark_benchmark_report.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Benchmark report saved: watermark_benchmark_report.png")


def main():
    parser = argparse.ArgumentParser(description='数字水印基准测试系统')
    parser.add_argument('--test', choices=['performance', 'alpha', 'robustness', 'image-performance', 'all'], 
                       default='all', help='基准测试类型')
    parser.add_argument('--image', type=str, help='测试图像路径')
    parser.add_argument('--watermark', type=str, default='SDU2025', help='水印文本')
    parser.add_argument('--watermark-image', type=str, default='QRcode.png', help='水印图像路径')
    parser.add_argument('--output-dir', type=str, default='benchmark_results', help='结果输出目录')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    benchmark = WatermarkBenchmark()
    
    print("=== Digital Watermark Benchmark System ===")
    print(f"Test type: {args.test}")
    print(f"Watermark text: '{args.watermark}'")
    print(f"Watermark image: '{args.watermark_image}'")
    print(f"Output directory: {args.output_dir}")
    
    if args.test in ['performance', 'all']:
        # 文字水印性能测试
        image_sizes = [(128, 128), (256, 256), (512, 512), (1024, 1024)]
        benchmark.benchmark_embedding_performance(image_sizes, args.watermark)
    
    if args.test in ['image-performance', 'all']:
        # 图片水印性能测试
        image_sizes = [(256, 256), (512, 512), (1024, 1024)]
        benchmark.benchmark_image_watermark_performance(image_sizes, args.watermark_image)
    
    if args.test in ['alpha', 'all']:
        # Alpha值测试
        alpha_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
        benchmark.benchmark_alpha_values(alpha_values, args.image, args.watermark)
    
    if args.test in ['robustness', 'all']:
        # 鲁棒性测试
        benchmark.benchmark_full_robustness(args.image, args.watermark)
    
    # 生成报告
    benchmark.generate_benchmark_report()
    
    print(f"\n=== Benchmark Testing Completed ===")
    print("Check the generated reports and charts for detailed results.")


if __name__ == "__main__":
    main()
