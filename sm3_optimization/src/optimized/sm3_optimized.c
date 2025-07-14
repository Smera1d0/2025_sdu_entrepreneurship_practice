// sm3_optimized.c
#include "sm3_optimized.h"
#include <string.h>
#include <stdio.h>

// SM3初始向量（大端序）
const uint32_t SM3_OPTIMIZED_IV[SM3_OPTIMIZED_STATE_SIZE] = {
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
};

// SM3常量T
static const uint32_t T_optimized[64] = {
    0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519,
    0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A
};

// 字节序转换函数
static inline uint32_t bytes_to_word_optimized(const uint8_t *bytes) {
    return ((uint32_t)bytes[0] << 24) | ((uint32_t)bytes[1] << 16) |
           ((uint32_t)bytes[2] << 8) | bytes[3];
}

static inline void word_to_bytes_optimized(uint32_t word, uint8_t *bytes) {
    bytes[0] = (uint8_t)(word >> 24);
    bytes[1] = (uint8_t)(word >> 16);
    bytes[2] = (uint8_t)(word >> 8);
    bytes[3] = (uint8_t)word;
}

// 循环左移
static inline uint32_t rotate_left_optimized(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

// 优化的布尔函数，使用位运算技巧
static inline uint32_t FF_opt(uint32_t x, uint32_t y, uint32_t z, int j) {
    if (j < 16) {
        return x ^ y ^ z;
    } else {
        // (x & y) | (x & z) | (y & z) = (x & (y | z)) | (y & z)
        return (x & (y | z)) | (y & z);
    }
}

static inline uint32_t GG_opt(uint32_t x, uint32_t y, uint32_t z, int j) {
    if (j < 16) {
        return x ^ y ^ z;
    } else {
        // (x & y) | (~x & z) = (x & y) | ((~x) & z)
        return (x & y) | ((~x) & z);
    }
}

// SM3置换函数
static inline uint32_t P0_optimized(uint32_t x) {
    return x ^ rotate_left_optimized(x, 9) ^ rotate_left_optimized(x, 17);
}

static inline uint32_t P1_optimized(uint32_t x) {
    return x ^ rotate_left_optimized(x, 15) ^ rotate_left_optimized(x, 23);
}

// 修复后的消息扩展
static void message_expansion_optimized(const uint8_t *block, uint32_t *W, uint32_t *W1) {
    int i;
    
    // 前16个字直接复制并转换字节序
    for (i = 0; i < 16; i++) {
        W[i] = bytes_to_word_optimized(block + i * 4);
    }
    
    // 扩展剩余52个字，保持正确的依赖关系
    for (i = 16; i < 68; i++) {
        uint32_t temp = W[i-16] ^ W[i-9] ^ rotate_left_optimized(W[i-3], 15);
        W[i] = P1_optimized(temp) ^ rotate_left_optimized(W[i-13], 7) ^ W[i-6];
    }
    
    // 计算W'
    for (i = 0; i < 64; i++) {
        W1[i] = W[i] ^ W[i+4];
    }
}

// 简化但仍然优化的压缩函数
static void sm3_compress_optimized(uint32_t *state, const uint8_t *block) {
    uint32_t W[68], W1[64];
    uint32_t A = state[0], B = state[1], C = state[2], D = state[3];
    uint32_t E = state[4], F = state[5], G = state[6], H = state[7];
    
    message_expansion_optimized(block, W, W1);
    
    // 64轮迭代，使用简单循环但内联函数
    for (int j = 0; j < 64; j++) {
        uint32_t SS1, SS2, TT1, TT2;
        uint32_t A12 = rotate_left_optimized(A, 12);
        SS1 = rotate_left_optimized(A12 + E + rotate_left_optimized(T_optimized[j], j), 7);
        SS2 = SS1 ^ A12;
        TT1 = FF_opt(A, B, C, j) + D + SS2 + W1[j];
        TT2 = GG_opt(E, F, G, j) + H + SS1 + W[j];
        
        D = C;
        C = rotate_left_optimized(B, 9);
        B = A;
        A = TT1;
        H = G;
        G = rotate_left_optimized(F, 19);
        F = E;
        E = P0_optimized(TT2);
    }
    
    // 更新状态
    state[0] ^= A; state[1] ^= B; state[2] ^= C; state[3] ^= D;
    state[4] ^= E; state[5] ^= F; state[6] ^= G; state[7] ^= H;
}

void sm3_optimized_init(sm3_optimized_ctx_t *ctx) {
    memcpy(ctx->state, SM3_OPTIMIZED_IV, sizeof(SM3_OPTIMIZED_IV));
    ctx->count = 0;
    ctx->buffer_len = 0;
    memset(ctx->buffer, 0, SM3_OPTIMIZED_BLOCK_SIZE);
}

void sm3_optimized_update(sm3_optimized_ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t i = 0;
    if (len == 0) return;
    ctx->count += len * 8;
    if (ctx->buffer_len > 0) {
        size_t copy_len = SM3_OPTIMIZED_BLOCK_SIZE - ctx->buffer_len;
        if (copy_len > len) copy_len = len;
        memcpy(ctx->buffer + ctx->buffer_len, data, copy_len);
        ctx->buffer_len += copy_len;
        i += copy_len;
        if (ctx->buffer_len == SM3_OPTIMIZED_BLOCK_SIZE) {
            sm3_compress_optimized(ctx->state, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
    while (i + SM3_OPTIMIZED_BLOCK_SIZE <= len) {
        sm3_compress_optimized(ctx->state, data + i);
        i += SM3_OPTIMIZED_BLOCK_SIZE;
    }
    if (i < len) {
        memcpy(ctx->buffer, data + i, len - i);
        ctx->buffer_len = len - i;
    }
}

void sm3_optimized_final(sm3_optimized_ctx_t *ctx, uint8_t *digest) {
    uint8_t block[SM3_OPTIMIZED_BLOCK_SIZE];
    size_t rest = ctx->buffer_len;
    uint64_t bit_count = ctx->count;
    memcpy(block, ctx->buffer, rest);
    block[rest] = 0x80;
    rest++;
    if (rest > 56) {
        memset(block + rest, 0, SM3_OPTIMIZED_BLOCK_SIZE - rest);
        sm3_compress_optimized(ctx->state, block);
        memset(block, 0, 56);
        rest = 0;
    } else {
        memset(block + rest, 0, 56 - rest);
        rest = 56;
    }
    for (int i = 0; i < 8; i++) {
        block[rest + i] = (uint8_t)(bit_count >> (56 - 8 * i));
    }
    sm3_compress_optimized(ctx->state, block);
    for (int i = 0; i < SM3_OPTIMIZED_STATE_SIZE; i++) {
        word_to_bytes_optimized(ctx->state[i], digest + i * 4);
    }
}

void sm3_optimized_hash(const uint8_t *data, size_t len, uint8_t *digest) {
    sm3_optimized_ctx_t ctx;
    sm3_optimized_init(&ctx);
    sm3_optimized_update(&ctx, data, len);
    sm3_optimized_final(&ctx, digest);
}

void sm3_optimized_print_digest(const uint8_t *digest) {
    for (int i = 0; i < SM3_OPTIMIZED_DIGEST_SIZE; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");
}

int sm3_optimized_verify(const uint8_t *data, size_t len, const uint8_t *expected_digest) {
    uint8_t computed_digest[SM3_OPTIMIZED_DIGEST_SIZE];
    sm3_optimized_hash(data, len, computed_digest);
    return memcmp(computed_digest, expected_digest, SM3_OPTIMIZED_DIGEST_SIZE) == 0;
} 