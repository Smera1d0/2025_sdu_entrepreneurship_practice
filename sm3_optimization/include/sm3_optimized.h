#ifndef SM3_OPTIMIZED_H
#define SM3_OPTIMIZED_H

#include <stdint.h>
#include <stddef.h>

// SM3常量定义
#define SM3_OPTIMIZED_BLOCK_SIZE 64
#define SM3_OPTIMIZED_DIGEST_SIZE 32
#define SM3_OPTIMIZED_STATE_SIZE 8

// SM3初始向量
extern const uint32_t SM3_OPTIMIZED_IV[SM3_OPTIMIZED_STATE_SIZE];

// SM3上下文结构
typedef struct {
    uint32_t state[SM3_OPTIMIZED_STATE_SIZE];  // 哈希状态
    uint64_t count;                  // 消息长度（位）
    uint8_t buffer[SM3_OPTIMIZED_BLOCK_SIZE];  // 消息缓冲区
    size_t buffer_len;               // 缓冲区中字节数
} sm3_optimized_ctx_t;

// 函数声明
void sm3_optimized_init(sm3_optimized_ctx_t *ctx);
void sm3_optimized_update(sm3_optimized_ctx_t *ctx, const uint8_t *data, size_t len);
void sm3_optimized_final(sm3_optimized_ctx_t *ctx, uint8_t *digest);
void sm3_optimized_hash(const uint8_t *data, size_t len, uint8_t *digest);

// 辅助函数
void sm3_optimized_print_digest(const uint8_t *digest);
int sm3_optimized_verify(const uint8_t *data, size_t len, const uint8_t *expected_digest);

#endif // SM3_OPTIMIZED_H 