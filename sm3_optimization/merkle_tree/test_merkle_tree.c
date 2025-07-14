#include "sm3_merkle_tree.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/sm3_basic.h"

#define LEAF_COUNT 100000

int main() {
    // 1. 构造10万叶子节点（内容为leaf000001~leaf100000）
    uint8_t leaves[LEAF_COUNT][SM3_HASH_SIZE];
    char buf[32];
    for (size_t i = 0; i < LEAF_COUNT; ++i) {
        snprintf(buf, sizeof(buf), "leaf%06zu", i+1);
        sm3_hash((uint8_t*)buf, strlen(buf), leaves[i]);
    }
    printf("已生成10万叶子节点哈希。\n");

    // 2. 构建Merkle树
    MerkleTree *tree = merkle_tree_build(leaves, LEAF_COUNT);
    if (!tree) { printf("Merkle树构建失败！\n"); return 1; }
    printf("Merkle树构建完成。\n");

    // 3. 获取根哈希
    uint8_t root[SM3_HASH_SIZE];
    merkle_tree_get_root(tree, root);
    printf("Merkle树根哈希: ");
    for (int i = 0; i < SM3_HASH_SIZE; ++i) printf("%02x", root[i]);
    printf("\n");

    // 4. 生成并验证存在性证明（如第88888个叶子）
    size_t test_idx = 88887;
    uint8_t proof[32][SM3_HASH_SIZE];
    size_t proof_len = merkle_tree_prove_inclusion(tree, test_idx, proof);
    int ok = merkle_tree_verify_inclusion(root, leaves[test_idx], test_idx, LEAF_COUNT, proof, proof_len);
    printf("存在性证明验证: %s\n", ok ? "成功" : "失败");

    // 5. 生成并验证不存在性证明（如leaf999999）
    char not_exist[] = "leaf999999";
    uint8_t not_exist_hash[SM3_HASH_SIZE];
    sm3_hash((uint8_t*)not_exist, strlen(not_exist), not_exist_hash);
    uint8_t nonproof[2][SM3_HASH_SIZE];
    size_t neighbor_idx;
    size_t nonproof_len = merkle_tree_prove_non_inclusion(tree, not_exist_hash, nonproof, &neighbor_idx);
    int nonok = merkle_tree_verify_non_inclusion(root, not_exist_hash, LEAF_COUNT, nonproof, nonproof_len, neighbor_idx);
    printf("不存在性证明验证: %s\n", nonok ? "成功" : "失败");

    merkle_tree_free(tree);
    return 0;
} 