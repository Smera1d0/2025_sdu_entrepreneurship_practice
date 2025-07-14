#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "../include/sm3_basic.h"

// 生成与SM3内部一致的padding，返回padding长度
size_t sm3_generate_padding(uint8_t *buf, size_t msg_len) {
    size_t rest = 0;
    uint64_t bit_count = msg_len * 8;
    buf[rest++] = 0x80;
    size_t pad_zero = ((msg_len + 1) % 64 > 56) ? (120 - (msg_len + 1) % 64) : (56 - (msg_len + 1) % 64);
    memset(buf + rest, 0, pad_zero);
    rest += pad_zero;
    for (int i = 0; i < 8; i++) {
        buf[rest + i] = (uint8_t)(bit_count >> (56 - 8 * i));
    }
    rest += 8;
    return rest;
}

// 伪造哈希状态继续计算
void sm3_set_state(sm3_ctx_t *ctx, const uint32_t *state, uint64_t total_bits) {
    memcpy(ctx->state, state, sizeof(ctx->state));
    ctx->count = total_bits;
    ctx->buffer_len = 0;
    memset(ctx->buffer, 0, SM3_BLOCK_SIZE);
}

int main() {
    // 攻击目标消息 M
    const char *M = "original_message";
    size_t M_len = strlen(M);
    // 攻击者想要追加的数据 M2
    const char *M2 = "_attack";
    size_t M2_len = strlen(M2);

    // 1. 计算原始哈希
    uint8_t digest[SM3_DIGEST_SIZE];
    sm3_hash((const uint8_t *)M, M_len, digest);
    printf("原始消息: %s\n原始哈希: ", M);
    sm3_print_digest(digest);

    // 2. 伪造padding
    uint8_t forged[512];
    memcpy(forged, M, M_len);
    size_t pad_len = sm3_generate_padding(forged + M_len, M_len);
    memcpy(forged + M_len + pad_len, M2, M2_len);
    size_t forged_len = M_len + pad_len + M2_len;

    // 3. 恢复中间状态，继续哈希M2
    sm3_ctx_t attack_ctx;
    for (int i = 0; i < 8; ++i) {
        attack_ctx.state[i] = ((uint32_t)digest[i*4] << 24) |
                              ((uint32_t)digest[i*4+1] << 16) |
                              ((uint32_t)digest[i*4+2] << 8) |
                              ((uint32_t)digest[i*4+3]);
    }
    attack_ctx.count = (M_len + pad_len) * 8; // 伪造消息前的总比特数
    attack_ctx.buffer_len = 0;
    memset(attack_ctx.buffer, 0, SM3_BLOCK_SIZE);
    sm3_update(&attack_ctx, (const uint8_t *)M2, M2_len);
    uint8_t attack_digest[SM3_DIGEST_SIZE];
    sm3_final(&attack_ctx, attack_digest);
    printf("攻击者伪造哈希: ");
    sm3_print_digest(attack_digest);

    // 4. 验证攻击是否成立
    uint8_t verify_digest[SM3_DIGEST_SIZE];
    sm3_hash(forged, forged_len, verify_digest);
    printf("直接哈希伪造消息: ");
    sm3_print_digest(verify_digest);
    if (memcmp(attack_digest, verify_digest, SM3_DIGEST_SIZE) == 0) {
        printf("[成功] 长度扩展攻击成立！\n");
    } else {
        printf("[失败] 长度扩展攻击失败。\n");
    }
    return 0;
} 