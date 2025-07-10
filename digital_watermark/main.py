import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct
import os
import random
from PIL import Image, ImageEnhance
import argparse


class BlindWatermark:
    def __init__(self, alpha=0.1, block_size=8):
        """
        Initialize blind watermarking system
        
        Args:
            alpha (float): Watermark strength, larger values give better robustness but lower transparency
            block_size (int): DCT block size
        """
        self.alpha = alpha
        self.block_size = block_size
    
    def _dct2(self, block):
        """2D DCT transform"""
        return dct(dct(block.T, norm='ortho').T, norm='ortho')
    
    def _idct2(self, block):
        """2D inverse DCT transform"""
        return idct(idct(block.T, norm='ortho').T, norm='ortho')
    
    def _embed_watermark_block(self, dct_block, watermark_bit):
        """Embed a watermark bit in DCT block"""
        # Use middle frequency coefficients for watermark embedding
        pos1, pos2 = (3, 4), (4, 3)  # Select middle frequency positions
        
        # Calculate embedding strength
        strength = 20.0 * self.alpha  # Fixed strength for better predictability
        
        if watermark_bit == 1:
            # Ensure pos1 > pos2
            dct_block[pos1] = strength
            dct_block[pos2] = -strength
        else:
            # 确保pos1 < pos2
            dct_block[pos1] = -strength
            dct_block[pos2] = strength
        
        return dct_block
    
    def _extract_watermark_block(self, dct_block):
        """从DCT块中提取水印位"""
        pos1, pos2 = (3, 4), (4, 3)
        # 增加判断的鲁棒性，考虑相对差异
        diff = dct_block[pos1] - dct_block[pos2]
        return 1 if diff > 0 else 0
    
    def string_to_binary(self, text):
        """将字符串转换为二进制"""
        return ''.join(format(ord(char), '08b') for char in text)
    
    def binary_to_string(self, binary):
        """将二进制转换为字符串"""
        chars = []
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return ''.join(chars)
    
    def image_to_binary(self, image_path, target_size=(32, 32)):
        """将图像转换为二进制数据"""
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"无法读取水印图像: {image_path}")
            
            img_resized = cv2.resize(img, target_size)
            _, binary_img = cv2.threshold(img_resized, 127, 1, cv2.THRESH_BINARY)
            return binary_img.flatten().tolist()
        except Exception as e:
            raise ValueError(f"图像水印处理错误: {e}")
    
    def binary_to_image(self, binary_data, image_size=(32, 32), output_path=None):
        """将二进制数据转换回图像"""
        try:
            binary_array = np.array(binary_data).reshape(image_size)
            img_array = (binary_array * 255).astype(np.uint8)
            if output_path:
                cv2.imwrite(output_path, img_array)
            return img_array
        except Exception as e:
            raise ValueError(f"二进制数据转图像错误: {e}")
    
    def add_watermark(self, image_path, watermark_text, output_path):
        """
        向图像添加盲水印
        
        Args:
            image_path (str): 原始图像路径
            watermark_text (str): 水印文本
            output_path (str): 输出图像路径
        """
        # 读取图像
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        # 转换为浮点型
        img = img.astype(np.float32)
        
        # 添加结束标记符，确保提取的完整性
        watermark_with_end = watermark_text + '\x00'  # 添加空字符作为结束标记
        
        # 将水印文本转换为二进制
        watermark_binary = self.string_to_binary(watermark_with_end)
        watermark_bits = [int(bit) for bit in watermark_binary]
        
        # 计算可用的块数量
        h, w = img.shape
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        total_blocks = num_blocks_h * num_blocks_w
        
        if len(watermark_bits) > total_blocks:
            raise ValueError(f"Watermark too long, maximum supported: {total_blocks // 8 - 1} characters")
        
        # 创建随机种子序列用于位置置乱
        np.random.seed(42)  # 固定种子确保可重复性
        positions = list(range(total_blocks))
        np.random.shuffle(positions)
        
        watermarked_img = img.copy()
        
        # 处理每个块
        for i, bit in enumerate(watermark_bits):
            if i >= len(positions):
                break
                
            pos = positions[i]
            row = pos // num_blocks_w
            col = pos % num_blocks_w
            
            # 提取块
            block = img[row*self.block_size:(row+1)*self.block_size,
                       col*self.block_size:(col+1)*self.block_size]
            
            # DCT变换
            dct_block = self._dct2(block)
            
            # 嵌入水印
            watermarked_dct = self._embed_watermark_block(dct_block.copy(), bit)
            
            # 逆DCT变换
            watermarked_block = self._idct2(watermarked_dct)
            
            # 更新图像
            watermarked_img[row*self.block_size:(row+1)*self.block_size,
                           col*self.block_size:(col+1)*self.block_size] = watermarked_block
        
        # 保存水印图像
        watermarked_img = np.clip(watermarked_img, 0, 255).astype(np.uint8)
        cv2.imwrite(output_path, watermarked_img)
        
        print(f"Watermark embedding completed: {output_path}")
        return watermarked_img
    
    def extract_watermark(self, watermarked_image_path, watermark_length):
        """
        从图像中提取盲水印
        
        Args:
            watermarked_image_path (str): 含水印图像路径
            watermark_length (int): 水印文本长度（字符数）
        
        Returns:
            str: 提取的水印文本
        """
        # 读取图像
        img = cv2.imread(watermarked_image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"无法读取图像: {watermarked_image_path}")
        
        img = img.astype(np.float32)
        
        # 计算块数量
        h, w = img.shape
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        total_blocks = num_blocks_h * num_blocks_w
        
        # 使用相同的随机种子序列
        np.random.seed(42)
        positions = list(range(total_blocks))
        np.random.shuffle(positions)
        
        # 提取水印位，需要额外的位数来检测结束符
        watermark_bits = []
        max_bits = (watermark_length + 1) * 8  # +1为结束符
        
        for i in range(min(max_bits, len(positions))):
            pos = positions[i]
            row = pos // num_blocks_w
            col = pos % num_blocks_w
            
            # 提取块
            block = img[row*self.block_size:(row+1)*self.block_size,
                       col*self.block_size:(col+1)*self.block_size]
            
            # DCT变换
            dct_block = self._dct2(block)
            
            # 提取水印位
            bit = self._extract_watermark_block(dct_block)
            watermark_bits.append(str(bit))
        
        # 转换为字符串
        watermark_binary = ''.join(watermark_bits)
        full_text = self.binary_to_string(watermark_binary)
        
        # 查找结束符并截取
        end_pos = full_text.find('\x00')
        if end_pos != -1:
            watermark_text = full_text[:end_pos]
        else:
            watermark_text = full_text[:watermark_length]  # 如果没找到结束符，按长度截取
        
        return watermark_text
    
    def add_image_watermark(self, image_path, watermark_image_path, output_path, watermark_size=(32, 32)):
        """向图像添加图片水印"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        img = img.astype(np.float32)
        watermark_bits = self.image_to_binary(watermark_image_path, watermark_size)
        
        # 添加尺寸信息和结束标记
        size_bits = []
        for dim in watermark_size:
            size_bits.extend([int(b) for b in format(dim, '08b')])
        end_marker = [1, 0, 1, 0, 1, 0, 1, 0]
        all_watermark_bits = size_bits + watermark_bits + end_marker
        
        h, w = img.shape
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        total_blocks = num_blocks_h * num_blocks_w
        
        if len(all_watermark_bits) > total_blocks:
            max_pixels = (total_blocks - 16 - 8) // 1
            max_size = int(np.sqrt(max_pixels))
            raise ValueError(f"水印图像太大，建议尺寸不超过 {max_size}x{max_size}")
        
        np.random.seed(42)
        positions = list(range(total_blocks))
        np.random.shuffle(positions)
        
        watermarked_img = img.copy()
        
        for i, bit in enumerate(all_watermark_bits):
            if i >= len(positions):
                break
                
            pos = positions[i]
            row = pos // num_blocks_w
            col = pos % num_blocks_w
            
            block = img[row*self.block_size:(row+1)*self.block_size,
                       col*self.block_size:(col+1)*self.block_size]
            
            dct_block = self._dct2(block)
            watermarked_dct = self._embed_watermark_block(dct_block.copy(), bit)
            watermarked_block = self._idct2(watermarked_dct)
            
            watermarked_img[row*self.block_size:(row+1)*self.block_size,
                           col*self.block_size:(col+1)*self.block_size] = watermarked_block
        
        watermarked_img = np.clip(watermarked_img, 0, 255).astype(np.uint8)
        cv2.imwrite(output_path, watermarked_img)
        
        print(f"Image watermark embedding completed: {output_path}")
        print(f"Watermark image size: {watermark_size[0]}x{watermark_size[1]}")
        return watermarked_img
    
    def extract_image_watermark(self, watermarked_image_path, output_watermark_path=None):
        """从图像中提取图片水印"""
        img = cv2.imread(watermarked_image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"无法读取图像: {watermarked_image_path}")
        
        img = img.astype(np.float32)
        h, w = img.shape
        num_blocks_h = h // self.block_size
        num_blocks_w = w // self.block_size
        total_blocks = num_blocks_h * num_blocks_w
        
        np.random.seed(42)
        positions = list(range(total_blocks))
        np.random.shuffle(positions)
        
        # 提取尺寸信息
        size_bits = []
        for i in range(16):
            if i >= len(positions):
                break
            pos = positions[i]
            row = pos // num_blocks_w
            col = pos % num_blocks_w
            
            block = img[row*self.block_size:(row+1)*self.block_size,
                       col*self.block_size:(col+1)*self.block_size]
            dct_block = self._dct2(block)
            bit = self._extract_watermark_block(dct_block)
            size_bits.append(bit)
        
        try:
            width_bits = ''.join(map(str, size_bits[:8]))
            height_bits = ''.join(map(str, size_bits[8:16]))
            watermark_width = int(width_bits, 2)
            watermark_height = int(height_bits, 2)
            
            if watermark_width <= 0 or watermark_height <= 0 or watermark_width > 256 or watermark_height > 256:
                raise ValueError("提取的水印尺寸无效")
        except Exception as e:
            raise ValueError(f"无法解析水印尺寸: {e}")
        
        watermark_size = (watermark_width, watermark_height)
        total_watermark_bits = watermark_width * watermark_height
        
        # 提取水印数据
        watermark_bits = []
        for i in range(16, 16 + total_watermark_bits + 8):
            if i >= len(positions):
                break
            pos = positions[i]
            row = pos // num_blocks_w
            col = pos % num_blocks_w
            
            block = img[row*self.block_size:(row+1)*self.block_size,
                       col*self.block_size:(col+1)*self.block_size]
            dct_block = self._dct2(block)
            bit = self._extract_watermark_block(dct_block)
            watermark_bits.append(bit)
        
        actual_watermark_bits = watermark_bits[:total_watermark_bits]
        watermark_image = self.binary_to_image(actual_watermark_bits, watermark_size, output_watermark_path)
        
        print(f"Image watermark extraction completed")
        print(f"Extracted watermark size: {watermark_size[0]}x{watermark_size[1]}")
        if output_watermark_path:
            print(f"Saved to: {output_watermark_path}")
        
        return watermark_image


class RobustnessTest:
    """鲁棒性测试类"""
    
    def __init__(self, watermark_system):
        self.watermark_system = watermark_system
    
    def flip_horizontal(self, image_path, output_path):
        """水平翻转"""
        img = cv2.imread(image_path)
        flipped = cv2.flip(img, 1)
        cv2.imwrite(output_path, flipped)
        return output_path
    
    def flip_vertical(self, image_path, output_path):
        """垂直翻转"""
        img = cv2.imread(image_path)
        flipped = cv2.flip(img, 0)
        cv2.imwrite(output_path, flipped)
        return output_path
    
    def rotate(self, image_path, output_path, angle=45):
        """旋转"""
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        
        # 计算旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 应用旋转
        rotated = cv2.warpAffine(img, rotation_matrix, (w, h))
        cv2.imwrite(output_path, rotated)
        return output_path
    
    def crop(self, image_path, output_path, crop_ratio=0.8):
        """裁剪"""
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        
        # 计算裁剪区域
        new_h, new_w = int(h * crop_ratio), int(w * crop_ratio)
        start_h, start_w = (h - new_h) // 2, (w - new_w) // 2
        
        cropped = img[start_h:start_h+new_h, start_w:start_w+new_w]
        
        # 调整回原尺寸
        resized = cv2.resize(cropped, (w, h))
        cv2.imwrite(output_path, resized)
        return output_path
    
    def adjust_brightness(self, image_path, output_path, factor=1.5):
        """调整亮度"""
        img = Image.open(image_path)
        enhancer = ImageEnhance.Brightness(img)
        enhanced = enhancer.enhance(factor)
        enhanced.save(output_path)
        return output_path
    
    def adjust_contrast(self, image_path, output_path, factor=1.5):
        """调整对比度"""
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        enhanced = enhancer.enhance(factor)
        enhanced.save(output_path)
        return output_path
    
    def add_noise(self, image_path, output_path, noise_level=25):
        """添加高斯噪声"""
        img = cv2.imread(image_path)
        noise = np.random.normal(0, noise_level, img.shape).astype(np.int16)
        noisy = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        cv2.imwrite(output_path, noisy)
        return output_path
    
    def compress_jpeg(self, image_path, output_path, quality=50):
        """JPEG压缩"""
        img = cv2.imread(image_path)
        cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return output_path
    
    def resize(self, image_path, output_path, scale=0.5):
        """缩放"""
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        # 先缩小再放大
        resized_small = cv2.resize(img, (new_w, new_h))
        resized_back = cv2.resize(resized_small, (w, h))
        cv2.imwrite(output_path, resized_back)
        return output_path
    
    def translation(self, image_path, output_path, shift_x=50, shift_y=30):
        """平移"""
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        
        # 平移矩阵
        translation_matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        translated = cv2.warpAffine(img, translation_matrix, (w, h))
        cv2.imwrite(output_path, translated)
        return output_path
    
    def run_all_tests(self, watermarked_image_path, watermark_text, output_dir):
        """运行所有鲁棒性测试"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        tests = [
            ("Horizontal Flip", self.flip_horizontal, {}),
            ("Vertical Flip", self.flip_vertical, {}),
            ("Rotation 45°", self.rotate, {"angle": 45}),
            ("Rotation 90°", self.rotate, {"angle": 90}),
            ("Crop 80%", self.crop, {"crop_ratio": 0.8}),
            ("Crop 60%", self.crop, {"crop_ratio": 0.6}),
            ("Brightness +1.5x", self.adjust_brightness, {"factor": 1.5}),
            ("Brightness -0.7x", self.adjust_brightness, {"factor": 0.7}),
            ("Contrast +1.5x", self.adjust_contrast, {"factor": 1.5}),
            ("Contrast -0.7x", self.adjust_contrast, {"factor": 0.7}),
            ("Gaussian Noise", self.add_noise, {"noise_level": 25}),
            ("JPEG Quality 50", self.compress_jpeg, {"quality": 50}),
            ("JPEG Quality 30", self.compress_jpeg, {"quality": 30}),
            ("Scale 0.5x", self.resize, {"scale": 0.5}),
            ("Scale 0.7x", self.resize, {"scale": 0.7}),
            ("Translation", self.translation, {"shift_x": 50, "shift_y": 30}),
        ]
        
        results = []
        
        print("\n=== Robustness Testing Started ===")
        print(f"Original watermark text: '{watermark_text}'")
        print("-" * 60)
        
        for test_name, test_func, params in tests:
            try:
                # 生成攻击后的图像
                attacked_path = os.path.join(output_dir, f"attacked_{test_name.replace(' ', '_')}.png")
                test_func(watermarked_image_path, attacked_path, **params)
                
                # 提取水印
                extracted_text = self.watermark_system.extract_watermark(
                    attacked_path, len(watermark_text)
                )
                
                # 计算准确率
                accuracy = self._calculate_accuracy(watermark_text, extracted_text)
                
                results.append({
                    'test': test_name,
                    'extracted': extracted_text,
                    'accuracy': accuracy,
                    'success': accuracy > 0.7  # 70%以上认为成功
                })
                
                status = "✓" if accuracy > 0.7 else "✗"
                print(f"{status} {test_name:20s} | 提取: '{extracted_text:15s}' | 准确率: {accuracy:.2%}")
                
            except Exception as e:
                print(f"✗ {test_name:20s} | Error: {str(e)}")
                results.append({
                    'test': test_name,
                    'extracted': 'ERROR',
                    'accuracy': 0.0,
                    'success': False
                })
        
        # Statistical results
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        success_rate = success_count / total_count
        
        print("-" * 60)
        print(f"Testing completed: {success_count}/{total_count} passed, Success rate: {success_rate:.2%}")
        
        return results
    
    def _calculate_accuracy(self, original, extracted):
        """计算字符准确率"""
        if len(original) == 0:
            return 1.0 if len(extracted) == 0 else 0.0
        
        min_len = min(len(original), len(extracted))
        if min_len == 0:
            return 0.0
        
        correct = sum(1 for i in range(min_len) if original[i] == extracted[i])
        return correct / len(original)


def create_sample_image(width=512, height=512, output_path="sample.png"):
    """创建一个示例图像用于测试"""
    # 创建渐变背景
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    for i in range(height):
        for j in range(width):
            img[i, j] = [
                int(255 * i / height),
                int(255 * j / width),
                int(255 * (i + j) / (height + width))
            ]
    
    # 添加一些几何图形
    cv2.circle(img, (width//4, height//4), 50, (255, 255, 255), -1)
    cv2.rectangle(img, (width//2, height//2), (width//2 + 100, height//2 + 100), (0, 0, 0), -1)
    cv2.ellipse(img, (3*width//4, 3*height//4), (60, 40), 45, 0, 360, (128, 128, 128), -1)
    
    cv2.imwrite(output_path, img)
    print(f"示例图像已创建: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='数字盲水印系统')
    parser.add_argument('--mode', choices=['add', 'extract', 'test', 'add-image', 'extract-image'], default='test',
                       help='运行模式: add(添加文字水印), extract(提取文字水印), test(完整测试), add-image(添加图片水印), extract-image(提取图片水印)')
    parser.add_argument('--image', type=str, help='输入图像路径')
    parser.add_argument('--watermark', type=str, default='SDU2025', help='水印文本')
    parser.add_argument('--watermark-image', type=str, help='水印图像路径')
    parser.add_argument('--output', type=str, help='输出路径')
    parser.add_argument('--alpha', type=float, default=0.1, help='水印强度')
    parser.add_argument('--watermark-size', type=int, nargs=2, default=[32, 32], metavar=('WIDTH', 'HEIGHT'),
                       help='水印图像尺寸 (默认: 32 32)')
    
    args = parser.parse_args()
    
    # 创建水印系统
    watermark_system = BlindWatermark(alpha=args.alpha)
    
    if args.mode == 'add':
        if not args.image or not args.output:
            print("添加水印模式需要指定 --image 和 --output 参数")
            return
        
        watermark_system.add_watermark(args.image, args.watermark, args.output)
        
    elif args.mode == 'add-image':
        if not args.image or not args.output or not args.watermark_image:
            print("添加图片水印模式需要指定 --image, --watermark-image 和 --output 参数")
            return
        
        if not os.path.exists(args.watermark_image):
            print(f"水印图像文件不存在: {args.watermark_image}")
            return
        
        watermark_size = tuple(args.watermark_size)
        watermark_system.add_image_watermark(args.image, args.watermark_image, args.output, watermark_size)
        
    elif args.mode == 'extract':
        if not args.image:
            print("提取水印模式需要指定 --image 参数")
            return
        
        extracted = watermark_system.extract_watermark(args.image, len(args.watermark))
        print(f"提取的水印: '{extracted}'")
        
    elif args.mode == 'extract-image':
        if not args.image:
            print("提取图片水印模式需要指定 --image 参数")
            return
        
        output_watermark = args.output if args.output else "extracted_watermark.png"
        watermark_system.extract_image_watermark(args.image, output_watermark)
        
    elif args.mode == 'test':
        # 基础功能测试
        print("=== Digital Blind Watermark System Basic Test ===")
        
        # 使用example.png作为默认测试图像（如果没有指定输入图像）
        if not args.image:
            if os.path.exists("example.png"):
                args.image = "example.png"
                print("Using example.png as test image")
            else:
                args.image = create_sample_image()
                print("example.png not found, creating sample image")
        
        # 添加水印
        watermarked_path = "watermarked_image.png"
        print(f"\n1. Adding watermark '{args.watermark}' to image '{args.image}'...")
        watermark_system.add_watermark(args.image, args.watermark, watermarked_path)
        
        # 提取水印验证
        print(f"\n2. Extracting watermark from watermarked image...")
        extracted = watermark_system.extract_watermark(watermarked_path, len(args.watermark))
        print(f"Extraction result: '{extracted}'")
        
        if extracted == args.watermark:
            print("✓ Watermark embedding and extraction verification successful!")
        else:
            print("✗ Watermark verification failed, please check parameter settings")
            return
        
        # 鲁棒性测试
        print(f"\n3. Starting robustness testing...")
        robustness_test = RobustnessTest(watermark_system)
        results = robustness_test.run_all_tests(watermarked_path, args.watermark, "robustness_test_results")
        
        # 生成可视化报告
        print(f"\n4. Generating test report...")
        generate_report(args.watermark, results)
        
        print(f"\n5. For performance benchmarking, please run:")
        print(f"   python benchmark.py --test all --watermark '{args.watermark}'")


def generate_report(original_watermark, test_results):
    """Generate test report and visualization charts"""
    # Statistical data
    success_tests = [r for r in test_results if r['success']]
    failed_tests = [r for r in test_results if not r['success']]
    
    # Create charts
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Success rate pie chart
    labels = ['Success', 'Failed']
    sizes = [len(success_tests), len(failed_tests)]
    colors = ['#2ecc71', '#e74c3c']
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Overall Robustness Test Success Rate')
    
    # 2. Accuracy bar chart for each test
    test_names = [r['test'] for r in test_results]
    accuracies = [r['accuracy'] for r in test_results]
    colors_bar = ['#2ecc71' if acc > 0.7 else '#e74c3c' for acc in accuracies]
    
    bars = ax2.bar(range(len(test_names)), accuracies, color=colors_bar)
    ax2.set_xlabel('Attack Type')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Watermark Extraction Accuracy Under Different Attacks')
    ax2.set_xticks(range(len(test_names)))
    ax2.set_xticklabels(test_names, rotation=45, ha='right')
    ax2.axhline(y=0.7, color='orange', linestyle='--', label='Success Threshold (70%)')
    ax2.legend()
    
    # 3. Category statistics
    attack_types = {
        'Geometric Attacks': ['Horizontal Flip', 'Vertical Flip', 'Rotation 45°', 'Rotation 90°', 'Translation'],
        'Signal Processing': ['Brightness +1.5x', 'Brightness -0.7x', 'Contrast +1.5x', 'Contrast -0.7x', 'Gaussian Noise'],
        'Compression': ['JPEG Quality 50', 'JPEG Quality 30', 'Scale 0.5x', 'Scale 0.7x'],
        'Cropping': ['Crop 80%', 'Crop 60%']
    }
    
    category_success = {}
    for category, tests in attack_types.items():
        category_results = [r for r in test_results if r['test'] in tests]
        if category_results:
            success_rate = sum(1 for r in category_results if r['success']) / len(category_results)
            category_success[category] = success_rate
    
    categories = list(category_success.keys())
    success_rates = list(category_success.values())
    
    ax3.bar(categories, success_rates, color=['#3498db', '#9b59b6', '#f39c12', '#1abc9c'])
    ax3.set_ylabel('Success Rate')
    ax3.set_title('Success Rate by Attack Category')
    ax3.set_ylim(0, 1)
    for i, v in enumerate(success_rates):
        ax3.text(i, v + 0.02, f'{v:.2%}', ha='center')
    
    # 4. Watermark extraction quality distribution
    quality_ranges = {'High (>90%)': 0, 'Medium (70%-90%)': 0, 'Low (<70%)': 0}
    for result in test_results:
        acc = result['accuracy']
        if acc > 0.9:
            quality_ranges['High (>90%)'] += 1
        elif acc > 0.7:
            quality_ranges['Medium (70%-90%)'] += 1
        else:
            quality_ranges['Low (<70%)'] += 1
    
    ax4.bar(quality_ranges.keys(), quality_ranges.values(), 
            color=['#2ecc71', '#f39c12', '#e74c3c'])
    ax4.set_ylabel('Number of Tests')
    ax4.set_title('Watermark Extraction Quality Distribution')
    for i, (k, v) in enumerate(quality_ranges.items()):
        ax4.text(i, v + 0.1, str(v), ha='center')
    
    plt.tight_layout()
    plt.savefig('robustness_test_report.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Test report saved: robustness_test_report.png")


if __name__ == "__main__":
    main()