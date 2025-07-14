#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include "../include/sm3_basic.h"
#include "../include/sm3_optimized.h"

// 测试参数
#define WARMUP_ROUNDS 1000
#define BENCHMARK_ROUNDS 10000
#define MIN_TEST_SIZE 64
#define MAX_TEST_SIZE (1024 * 1024)  // 1MB

// 获取高精度时间戳（微秒）
static double get_time_us() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000000.0 + tv.tv_usec;
}

// 生成测试数据
static void generate_test_data(uint8_t *data, size_t size) {
    for (size_t i = 0; i < size; i++) {
        data[i] = (uint8_t)(i ^ (i >> 8) ^ 0x5A);
    }
}

// 验证结果一致性
static int verify_consistency(const uint8_t *data, size_t size) {
    uint8_t digest_basic[SM3_DIGEST_SIZE];
    uint8_t digest_optimized[SM3_OPTIMIZED_DIGEST_SIZE];
    
    sm3_hash(data, size, digest_basic);
    sm3_optimized_hash(data, size, digest_optimized);
    
    return memcmp(digest_basic, digest_optimized, SM3_DIGEST_SIZE) == 0;
}

// 单轮性能测试
static double benchmark_single(void (*hash_func)(const uint8_t*, size_t, uint8_t*), 
                              const uint8_t *data, size_t size, int rounds) {
    uint8_t digest[32];
    double start_time, end_time;
    
    // 预热
    for (int i = 0; i < WARMUP_ROUNDS; i++) {
        hash_func(data, size, digest);
    }
    
    // 正式测试
    start_time = get_time_us();
    for (int i = 0; i < rounds; i++) {
        hash_func(data, size, digest);
    }
    end_time = get_time_us();
    
    return (end_time - start_time) / rounds;  // 平均每次耗时（微秒）
}

// 吞吐量测试
static void benchmark_throughput(size_t test_size) {
    uint8_t *data = malloc(test_size);
    if (!data) {
        printf("内存分配失败\n");
        return;
    }
    
    generate_test_data(data, test_size);
    
    // 验证一致性
    if (!verify_consistency(data, test_size)) {
        printf("❌ 数据大小 %zu 字节: 哈希结果不一致！\n", test_size);
        free(data);
        return;
    }
    
    printf("✅ 数据大小: %zu 字节\n", test_size);
    
    // 基础版本测试
    double time_basic = benchmark_single(sm3_hash, data, test_size, BENCHMARK_ROUNDS);
    double throughput_basic = (test_size * BENCHMARK_ROUNDS) / (time_basic * BENCHMARK_ROUNDS / 1000000.0) / (1024 * 1024);
    
    // 优化版本测试
    double time_optimized = benchmark_single(sm3_optimized_hash, data, test_size, BENCHMARK_ROUNDS);
    double throughput_optimized = (test_size * BENCHMARK_ROUNDS) / (time_optimized * BENCHMARK_ROUNDS / 1000000.0) / (1024 * 1024);
    
    // 计算加速比
    double speedup = time_basic / time_optimized;
    
    printf("  基础版本: %.2f μs/次, %.2f MB/s\n", time_basic, throughput_basic);
    printf("  优化版本: %.2f μs/次, %.2f MB/s\n", time_optimized, throughput_optimized);
    printf("  加速比: %.2fx\n", speedup);
    printf("  性能提升: %.1f%%\n\n", (speedup - 1.0) * 100.0);
    
    free(data);
}

// 流式处理性能测试
static void benchmark_streaming(size_t total_size, size_t chunk_size) {
    uint8_t *data = malloc(total_size);
    if (!data) {
        printf("流式测试内存分配失败\n");
        return;
    }
    
    generate_test_data(data, total_size);
    
    printf("📊 流式处理测试 (总数据: %zu 字节, 分块: %zu 字节)\n", total_size, chunk_size);
    
    // 基础版本流式测试
    double start_time = get_time_us();
    for (int round = 0; round < BENCHMARK_ROUNDS; round++) {
        sm3_ctx_t ctx;
        sm3_init(&ctx);
        for (size_t offset = 0; offset < total_size; offset += chunk_size) {
            size_t current_chunk = (offset + chunk_size > total_size) ? (total_size - offset) : chunk_size;
            sm3_update(&ctx, data + offset, current_chunk);
        }
        uint8_t digest[SM3_DIGEST_SIZE];
        sm3_final(&ctx, digest);
    }
    double time_basic = (get_time_us() - start_time) / BENCHMARK_ROUNDS;
    
    // 优化版本流式测试
    start_time = get_time_us();
    for (int round = 0; round < BENCHMARK_ROUNDS; round++) {
        sm3_optimized_ctx_t ctx;
        sm3_optimized_init(&ctx);
        for (size_t offset = 0; offset < total_size; offset += chunk_size) {
            size_t current_chunk = (offset + chunk_size > total_size) ? (total_size - offset) : chunk_size;
            sm3_optimized_update(&ctx, data + offset, current_chunk);
        }
        uint8_t digest[SM3_OPTIMIZED_DIGEST_SIZE];
        sm3_optimized_final(&ctx, digest);
    }
    double time_optimized = (get_time_us() - start_time) / BENCHMARK_ROUNDS;
    
    double speedup = time_basic / time_optimized;
    printf("  基础版本: %.2f μs/次\n", time_basic);
    printf("  优化版本: %.2f μs/次\n", time_optimized);
    printf("  流式加速比: %.2fx\n\n", speedup);
    
    free(data);
}

// CPU信息检测
static void print_cpu_info() {
    printf("🖥️  系统信息:\n");
    printf("  处理器核心数: %d\n", (int)sysconf(_SC_NPROCESSORS_ONLN));
    
    // 尝试检测CPU特性
    #ifdef __x86_64__
        printf("  架构: x86_64\n");
        #ifdef __SSE2__
            printf("  SSE2支持: 是\n");
        #endif
        #ifdef __AVX2__
            printf("  AVX2支持: 是\n");
        #endif
    #elif defined(__aarch64__)
        printf("  架构: ARM64\n");
        printf("  NEON支持: 是\n");
    #else
        printf("  架构: 其他\n");
    #endif
    printf("\n");
}

int main() {
    printf("🚀 SM3 哈希算法性能基准测试\n");
    printf("=====================================\n\n");
    
    print_cpu_info();
    
    printf("📋 测试配置:\n");
    printf("  预热轮数: %d\n", WARMUP_ROUNDS);
    printf("  基准轮数: %d\n", BENCHMARK_ROUNDS);
    printf("\n");
    
    // 不同数据大小的吞吐量测试
    printf("📈 吞吐量基准测试:\n");
    printf("=====================================\n");
    
    size_t test_sizes[] = {64, 256, 1024, 4096, 16384, 65536, 262144, 1048576};
    int num_sizes = sizeof(test_sizes) / sizeof(test_sizes[0]);
    
    for (int i = 0; i < num_sizes; i++) {
        benchmark_throughput(test_sizes[i]);
    }
    
    // 流式处理测试
    printf("🌊 流式处理基准测试:\n");
    printf("=====================================\n");
    benchmark_streaming(1024 * 1024, 64);     // 1MB 数据，64字节分块
    benchmark_streaming(1024 * 1024, 1024);   // 1MB 数据，1KB分块
    benchmark_streaming(1024 * 1024, 8192);   // 1MB 数据，8KB分块
    
    printf("✨ 测试完成！\n");
    return 0;
} 