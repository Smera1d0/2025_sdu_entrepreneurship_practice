#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>
#include "../include/sm3_basic.h"
#include "../include/sm3_optimized.h"

// 测试向量（已知的SM3哈希值）
static const struct {
    const char *message;
    const char *expected_hash;
} test_vectors[] = {
    {"", "1ab21d8355cfa17f8e61194831e81a8f22bec8c728fefb747ed035eb5082aa2b"},
    {"abc", "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"},
    {"abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd", 
     "debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732"},
    {"abcdefghijklmnopqrstuvwxyz", 
     "b80fe97a4da24afc277564f66a359ef440462ad28dcc6d63adb24d5c20a61595"},
    {NULL, NULL}
};

// 性能测试函数
void performance_test(const char *test_name, void (*hash_func)(const uint8_t*, size_t, uint8_t*)) {
    const size_t data_size = 1024 * 1024 * 100; // 100MB
    const size_t iterations = 20;
    
    // 分配测试数据
    uint8_t *data = malloc(data_size);
    uint8_t digest[SM3_DIGEST_SIZE];
    
    if (!data) {
        printf("内存分配失败\n");
        return;
    }
    
    // 填充测试数据
    for (size_t i = 0; i < data_size; i++) {
        data[i] = (uint8_t)(i & 0xFF);
    }
    
    // 预热
    for (int i = 0; i < 10; i++) {
        hash_func(data, data_size, digest);
    }
    
    // 性能测试
    clock_t start = clock();
    for (size_t i = 0; i < iterations; i++) {
        hash_func(data, data_size, digest);
    }
    clock_t end = clock();
    
    double total_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    double throughput = (double)(data_size * iterations) / total_time / (1024 * 1024); // MB/s
    
    printf("%s 性能测试:\n", test_name);
    printf("  总时间: %.3f 秒\n", total_time);
    printf("  吞吐量: %.2f MB/s\n", throughput);
    printf("  平均时间: %.3f 毫秒/次\n", total_time * 1000 / iterations);
    printf("\n");
    
    free(data);
}

// 批量测试函数
void batch_test() {
    const size_t batch_size = 10000;
    const size_t data_size = 10240; // 10KB per message
    
    // 分配内存
    uint8_t **data_array = malloc(batch_size * sizeof(uint8_t*));
    size_t *len_array = malloc(batch_size * sizeof(size_t));
    uint8_t **digest_array = malloc(batch_size * sizeof(uint8_t*));
    
    if (!data_array || !len_array || !digest_array) {
        printf("内存分配失败\n");
        return;
    }
    
    // 初始化数据
    for (size_t i = 0; i < batch_size; i++) {
        data_array[i] = malloc(data_size);
        digest_array[i] = malloc(SM3_DIGEST_SIZE);
        len_array[i] = data_size;
        
        if (!data_array[i] || !digest_array[i]) {
            printf("内存分配失败\n");
            return;
        }
        
        // 填充测试数据
        for (size_t j = 0; j < data_size; j++) {
            data_array[i][j] = (uint8_t)((i + j) & 0xFF);
        }
    }
    
    // 测试基础版本批量处理
    clock_t start = clock();
    for (size_t i = 0; i < batch_size; i++) {
        sm3_hash(data_array[i], len_array[i], digest_array[i]);
    }
    clock_t end = clock();
    double basic_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    
    // 测试优化版本批量处理
    start = clock();
    for (size_t i = 0; i < batch_size; i++) {
        sm3_optimized_hash(data_array[i], len_array[i], digest_array[i]);
    }
    end = clock();
    double opt_time = ((double)(end - start)) / CLOCKS_PER_SEC;
    
    printf("批量处理测试 (%zu 个消息，每个 %zu 字节):\n", batch_size, data_size);
    printf("  基础版本: %.3f 秒\n", basic_time);
    printf("  优化版本: %.3f 秒\n", opt_time);
    printf("  性能提升: %.2fx\n", basic_time / opt_time);
    printf("\n");
    
    // 清理内存
    for (size_t i = 0; i < batch_size; i++) {
        free(data_array[i]);
        free(digest_array[i]);
    }
    free(data_array);
    free(len_array);
    free(digest_array);
}

// 验证测试向量
void verify_test_vectors() {
    printf("验证测试向量:\n");
    
    for (int i = 0; test_vectors[i].message != NULL; i++) {
        const char *message = test_vectors[i].message;
        const char *expected = test_vectors[i].expected_hash;
        size_t len = strlen(message);
        
        uint8_t basic_digest[SM3_DIGEST_SIZE];
        uint8_t opt_digest[SM3_DIGEST_SIZE];
        
        // 计算哈希值
        sm3_hash((const uint8_t*)message, len, basic_digest);
        sm3_optimized_hash((const uint8_t*)message, len, opt_digest);
        
        // 转换为十六进制字符串进行比较
        char basic_hex[65], opt_hex[65];
        for (int j = 0; j < SM3_DIGEST_SIZE; j++) {
            sprintf(basic_hex + j * 2, "%02x", basic_digest[j]);
            sprintf(opt_hex + j * 2, "%02x", opt_digest[j]);
        }
        basic_hex[64] = opt_hex[64] = '\0';
        
        printf("测试 %d: \"%s\"\n", i + 1, message);
        printf("  基础版本: %s\n", basic_hex);
        printf("  优化版本: %s\n", opt_hex);
        printf("  期望结果: %s\n", expected);
        
        if (strcmp(basic_hex, expected) == 0 && strcmp(opt_hex, expected) == 0) {
            printf("  ✓ 通过\n");
        } else {
            printf("  ✗ 失败\n");
        }
        printf("\n");
    }
}

// 随机数据测试
void random_data_test() {
    printf("随机数据测试:\n");
    
    const size_t test_count = 10;
    const size_t max_size = 1024;
    
    srand(time(NULL));
    
    for (size_t i = 0; i < test_count; i++) {
        size_t data_size = rand() % max_size + 1;
        uint8_t *data = malloc(data_size);
        
        if (!data) {
            printf("内存分配失败\n");
            continue;
        }
        
        // 生成随机数据
        for (size_t j = 0; j < data_size; j++) {
            data[j] = (uint8_t)(rand() % 256);
        }
        
        uint8_t basic_digest[SM3_DIGEST_SIZE];
        uint8_t opt_digest[SM3_DIGEST_SIZE];
        
        sm3_hash(data, data_size, basic_digest);
        sm3_optimized_hash(data, data_size, opt_digest);
        
        if (memcmp(basic_digest, opt_digest, SM3_DIGEST_SIZE) == 0) {
            printf("  测试 %zu (%zu 字节): ✓ 通过\n", i + 1, data_size);
        } else {
            printf("  测试 %zu (%zu 字节): ✗ 失败\n", i + 1, data_size);
        }
        
        free(data);
    }
    printf("\n");
}

int main() {
    printf("=== SM3 哈希算法测试程序 ===\n\n");
    
    // 验证测试向量
    verify_test_vectors();
    
    // 随机数据测试
    random_data_test();
    
    // 性能测试
    printf("=== 性能测试 ===\n");
    performance_test("基础版本", sm3_hash);
    performance_test("优化版本", sm3_optimized_hash);
    
    // 批量处理测试
    batch_test();
    
    printf("测试完成！\n");
    return 0;
} 