#include "sm3_basic.h"
#include <string.h>
#include <stdio.h>

// SM3初始向量（大端序）
const uint32_t SM3_IV[SM3_STATE_SIZE] = {
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
};

// SM3常量T
static const uint32_t T[64] = {
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
static uint32_t bytes_to_word(const uint8_t *bytes) {
    return ((uint32_t)bytes[0] << 24) | ((uint32_t)bytes[1] << 16) |
           ((uint32_t)bytes[2] << 8) | bytes[3];
}

static void word_to_bytes(uint32_t word, uint8_t *bytes) {
    bytes[0] = (uint8_t)(word >> 24);
    bytes[1] = (uint8_t)(word >> 16);
    bytes[2] = (uint8_t)(word >> 8);
    bytes[3] = (uint8_t)word;
}

// 循环左移
static uint32_t rotate_left(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

// SM3布尔函数
static uint32_t FF(uint32_t x, uint32_t y, uint32_t z, int j) {
    if (j < 16) {
        return x ^ y ^ z;
    } else {
        return (x & y) | (x & z) | (y & z);
    }
}

static uint32_t GG(uint32_t x, uint32_t y, uint32_t z, int j) {
    if (j < 16) {
        return x ^ y ^ z;
    } else {
        return (x & y) | (~x & z);
    }
}

// SM3置换函数
static uint32_t P0(uint32_t x) {
    return x ^ rotate_left(x, 9) ^ rotate_left(x, 17);
}

static uint32_t P1(uint32_t x) {
    return x ^ rotate_left(x, 15) ^ rotate_left(x, 23);
}

// 消息扩展
static void message_expansion(const uint8_t *block, uint32_t *W, uint32_t *W1) {
    uint32_t temp;
    
    // 前16个字直接复制
    for (int i = 0; i < 16; i++) {
        W[i] = bytes_to_word(block + i * 4);
    }
    
    // 扩展剩余48个字
    for (int i = 16; i < 68; i++) {
        temp = W[i-16] ^ W[i-9] ^ rotate_left(W[i-3], 15);
        W[i] = P1(temp) ^ rotate_left(W[i-13], 7) ^ W[i-6];
    }
    
    // 计算W'
    for (int i = 0; i < 64; i++) {
        W1[i] = W[i] ^ W[i+4];
    }
}

// SM3压缩函数
static void sm3_compress(uint32_t *state, const uint8_t *block) {
    uint32_t W[68], W1[64];
    uint32_t A, B, C, D, E, F, G, H;
    uint32_t SS1, SS2, TT1, TT2;
    
    // 消息扩展
    message_expansion(block, W, W1);
    
    // 初始化工作变量
    A = state[0]; B = state[1]; C = state[2]; D = state[3];
    E = state[4]; F = state[5]; G = state[6]; H = state[7];
    
    // 64轮迭代
    for (int j = 0; j < 64; j++) {
        SS1 = rotate_left(rotate_left(A, 12) + E + rotate_left(T[j], j), 7);
        SS2 = SS1 ^ rotate_left(A, 12);
        TT1 = FF(A, B, C, j) + D + SS2 + W1[j];
        TT2 = GG(E, F, G, j) + H + SS1 + W[j];
        
        D = C;
        C = rotate_left(B, 9);
        B = A;
        A = TT1;
        H = G;
        G = rotate_left(F, 19);
        F = E;
        E = P0(TT2);
    }
    
    // 更新状态
    state[0] ^= A; state[1] ^= B; state[2] ^= C; state[3] ^= D;
    state[4] ^= E; state[5] ^= F; state[6] ^= G; state[7] ^= H;
}

// 初始化SM3上下文
void sm3_init(sm3_ctx_t *ctx) {
    memcpy(ctx->state, SM3_IV, sizeof(SM3_IV));
    ctx->count = 0;
    ctx->buffer_len = 0;
    memset(ctx->buffer, 0, SM3_BLOCK_SIZE);
}

// 更新SM3上下文
void sm3_update(sm3_ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t i = 0;
    if (len == 0) return;
    // 只统计原始消息长度
    ctx->count += len * 8;
    // 处理缓冲区中已有的数据
    if (ctx->buffer_len > 0) {
        size_t copy_len = SM3_BLOCK_SIZE - ctx->buffer_len;
        if (copy_len > len) copy_len = len;
        memcpy(ctx->buffer + ctx->buffer_len, data, copy_len);
        ctx->buffer_len += copy_len;
        i += copy_len;
        if (ctx->buffer_len == SM3_BLOCK_SIZE) {
            sm3_compress(ctx->state, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
    // 处理完整的数据块
    while (i + SM3_BLOCK_SIZE <= len) {
        sm3_compress(ctx->state, data + i);
        i += SM3_BLOCK_SIZE;
    }
    // 保存剩余数据到缓冲区
    if (i < len) {
        memcpy(ctx->buffer, data + i, len - i);
        ctx->buffer_len = len - i;
    }
}

// 完成SM3哈希计算
void sm3_final(sm3_ctx_t *ctx, uint8_t *digest) {
    uint8_t block[SM3_BLOCK_SIZE];
    size_t rest = ctx->buffer_len;
    uint64_t bit_count = ctx->count;
    // 1. 拷贝剩余数据
    memcpy(block, ctx->buffer, rest);
    // 2. 填充0x80
    block[rest] = 0x80;
    rest++;
    // 3. 填充0x00直到还剩8字节
    if (rest > 56) {
        memset(block + rest, 0, SM3_BLOCK_SIZE - rest);
        sm3_compress(ctx->state, block);
        memset(block, 0, 56);
        rest = 0;
    } else {
        memset(block + rest, 0, 56 - rest);
        rest = 56;
    }
    // 4. 填写长度（大端序）
    for (int i = 0; i < 8; i++) {
        block[rest + i] = (uint8_t)(bit_count >> (56 - 8 * i));
    }
    sm3_compress(ctx->state, block);
    // 5. 输出结果
    for (int i = 0; i < SM3_STATE_SIZE; i++) {
        word_to_bytes(ctx->state[i], digest + i * 4);
    }
}

// 一次性哈希函数
void sm3_hash(const uint8_t *data, size_t len, uint8_t *digest) {
    sm3_ctx_t ctx;
    sm3_init(&ctx);
    sm3_update(&ctx, data, len);
    sm3_final(&ctx, digest);
}

// 打印摘要
void sm3_print_digest(const uint8_t *digest) {
    for (int i = 0; i < SM3_DIGEST_SIZE; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");
}

// 验证摘要
int sm3_verify(const uint8_t *data, size_t len, const uint8_t *expected_digest) {
    uint8_t computed_digest[SM3_DIGEST_SIZE];
    sm3_hash(data, len, computed_digest);
    return memcmp(computed_digest, expected_digest, SM3_DIGEST_SIZE) == 0;
} 