#include <stdio.h>
#include <string.h>
#include "../include/sm3_basic.h"
#include "../include/sm3_optimized.h"

int main() {
    const char *message = "Hello, SM3!";
    uint8_t basic_digest[SM3_DIGEST_SIZE];
    uint8_t optimized_digest[SM3_OPTIMIZED_DIGEST_SIZE];
    
    printf("=== SM3 哈希算法示例 ===\n\n");
    printf("输入消息: \"%s\"\n\n", message);
    
    // 使用基础版本计算哈希
    sm3_hash((const uint8_t*)message, strlen(message), basic_digest);
    printf("基础版本结果: ");
    sm3_print_digest(basic_digest);
    
    // 使用优化版本计算哈希
    sm3_optimized_hash((const uint8_t*)message, strlen(message), optimized_digest);
    printf("优化版本结果: ");
    sm3_optimized_print_digest(optimized_digest);
    
    // 验证结果一致性
    if (memcmp(basic_digest, optimized_digest, SM3_DIGEST_SIZE) == 0) {
        printf("\n✅ 两个版本的结果一致！\n");
    } else {
        printf("\n❌ 两个版本的结果不一致！\n");
    }
    
    // 流式处理示例
    printf("\n=== 流式处理示例 ===\n");
    sm3_ctx_t ctx;
    uint8_t stream_digest[SM3_DIGEST_SIZE];
    
    sm3_init(&ctx);
    sm3_update(&ctx, (const uint8_t*)"Hello, ", 7);
    sm3_update(&ctx, (const uint8_t*)"SM3!", 4);
    sm3_final(&ctx, stream_digest);
    
    printf("流式处理结果: ");
    sm3_print_digest(stream_digest);
    
    return 0;
}
