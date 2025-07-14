#ifndef SM3_MERKLE_TREE_H
#define SM3_MERKLE_TREE_H
#include <stdint.h>
#include <stddef.h>
#define MERKLE_MAX_LEAVES 100000
#define SM3_HASH_SIZE 32

// Merkle树节点
typedef struct MerkleNode {
    uint8_t hash[SM3_HASH_SIZE];
    struct MerkleNode *left, *right;
} MerkleNode;

// Merkle树结构
typedef struct {
    MerkleNode *root;
    size_t leaf_count;
    MerkleNode *leaves[MERKLE_MAX_LEAVES];
} MerkleTree;

// 构建Merkle树
MerkleTree *merkle_tree_build(const uint8_t leaves[][SM3_HASH_SIZE], size_t leaf_count);
// 释放Merkle树
void merkle_tree_free(MerkleTree *tree);
// 获取根哈希
void merkle_tree_get_root(const MerkleTree *tree, uint8_t *root_hash);
// 生成存在性证明
size_t merkle_tree_prove_inclusion(const MerkleTree *tree, size_t leaf_idx, uint8_t proof[][SM3_HASH_SIZE]);
// 验证存在性证明
int merkle_tree_verify_inclusion(const uint8_t *root, const uint8_t *leaf, size_t leaf_idx, size_t leaf_count, const uint8_t proof[][SM3_HASH_SIZE], size_t proof_len);
// 生成不存在性证明（RFC6962语义）
size_t merkle_tree_prove_non_inclusion(const MerkleTree *tree, const uint8_t *target, uint8_t proof[][SM3_HASH_SIZE], size_t *neighbor_idx);
// 验证不存在性证明
int merkle_tree_verify_non_inclusion(const uint8_t *root, const uint8_t *target, size_t leaf_count, const uint8_t proof[][SM3_HASH_SIZE], size_t proof_len, size_t neighbor_idx);

#endif // SM3_MERKLE_TREE_H 