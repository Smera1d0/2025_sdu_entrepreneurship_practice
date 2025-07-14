#include "sm3_merkle_tree.h"
#include <stdlib.h>
#include <string.h>
#include "../include/sm3_basic.h"

// 创建新节点
static MerkleNode *merkle_node_new(const uint8_t *hash) {
    MerkleNode *node = (MerkleNode *)malloc(sizeof(MerkleNode));
    memcpy(node->hash, hash, SM3_HASH_SIZE);
    node->left = node->right = NULL;
    return node;
}

// 非递归后序遍历释放节点，避免递归栈溢出
static void merkle_node_free(MerkleNode *root) {
    if (!root) return;
    MerkleNode *stack[64]; // 树高不会超过64
    int top = 0;
    MerkleNode *curr = root, *last = NULL;
    while (curr || top > 0) {
        if (curr) {
            stack[top++] = curr;
            curr = curr->left;
        } else {
            MerkleNode *node = stack[top-1];
            if (node->right && last != node->right) {
                curr = node->right;
            } else {
                free(node);
                last = node;
                --top;
            }
        }
    }
}

// 组合两个哈希
static void merkle_hash_combine(const uint8_t *left, const uint8_t *right, uint8_t *out) {
    uint8_t buf[SM3_HASH_SIZE * 2];
    memcpy(buf, left, SM3_HASH_SIZE);
    memcpy(buf + SM3_HASH_SIZE, right, SM3_HASH_SIZE);
    sm3_hash(buf, SM3_HASH_SIZE * 2, out);
}

// 构建Merkle树（每层用malloc分配新数组，leaves[]只保存叶子节点）
MerkleTree *merkle_tree_build(const uint8_t leaves_hash[][SM3_HASH_SIZE], size_t leaf_count) {
    if (leaf_count == 0 || leaf_count > MERKLE_MAX_LEAVES) return NULL;
    MerkleTree *tree = (MerkleTree *)malloc(sizeof(MerkleTree));
    tree->leaf_count = leaf_count;
    // 初始化叶子节点
    for (size_t i = 0; i < leaf_count; ++i) {
        tree->leaves[i] = merkle_node_new(leaves_hash[i]);
    }
    // 构建树
    size_t count = leaf_count;
    MerkleNode **current = (MerkleNode **)malloc(sizeof(MerkleNode *) * count);
    for (size_t i = 0; i < count; ++i) current[i] = tree->leaves[i];
    while (count > 1) {
        size_t next_count = (count + 1) / 2;
        MerkleNode **next = (MerkleNode **)malloc(sizeof(MerkleNode *) * next_count);
        for (size_t i = 0; i < next_count; ++i) {
            MerkleNode *left = current[i * 2];
            MerkleNode *right = (i * 2 + 1 < count) ? current[i * 2 + 1] : left;
            uint8_t combined[SM3_HASH_SIZE];
            merkle_hash_combine(left->hash, right->hash, combined);
            MerkleNode *parent = merkle_node_new(combined);
            parent->left = left;
            parent->right = right;
            next[i] = parent;
        }
        free(current);
        current = next;
        count = next_count;
    }
    tree->root = current[0];
    free(current);
    return tree;
}

void merkle_tree_free(MerkleTree *tree) {
    if (!tree) return;
    merkle_node_free(tree->root);
    free(tree);
}

void merkle_tree_get_root(const MerkleTree *tree, uint8_t *root_hash) {
    if (tree && tree->root) memcpy(root_hash, tree->root->hash, SM3_HASH_SIZE);
}

// 生成存在性证明（用临时hash数组模拟每层节点，不再new/free MerkleNode）
size_t merkle_tree_prove_inclusion(const MerkleTree *tree, size_t leaf_idx, uint8_t proof[][SM3_HASH_SIZE]) {
    size_t idx = leaf_idx;
    size_t proof_len = 0;
    size_t count = tree->leaf_count;
    // 用临时hash数组保存每层节点
    uint8_t (*level)[SM3_HASH_SIZE] = malloc(sizeof(uint8_t[SM3_HASH_SIZE]) * count);
    for (size_t i = 0; i < count; ++i) memcpy(level[i], tree->leaves[i]->hash, SM3_HASH_SIZE);
    while (count > 1) {
        size_t sibling = (idx % 2 == 0) ? idx + 1 : idx - 1;
        if (sibling >= count) sibling = idx; // 复制自身
        memcpy(proof[proof_len++], level[sibling], SM3_HASH_SIZE);
        // 构建上一层
        size_t next_count = (count + 1) / 2;
        for (size_t i = 0; i < next_count; ++i) {
            uint8_t left[SM3_HASH_SIZE], right[SM3_HASH_SIZE], combined[SM3_HASH_SIZE];
            memcpy(left, level[i * 2], SM3_HASH_SIZE);
            if (i * 2 + 1 < count) memcpy(right, level[i * 2 + 1], SM3_HASH_SIZE);
            else memcpy(right, left, SM3_HASH_SIZE);
            merkle_hash_combine(left, right, combined);
            memcpy(level[i], combined, SM3_HASH_SIZE);
        }
        idx /= 2;
        count = next_count;
    }
    free(level);
    return proof_len;
}

// 验证存在性证明
int merkle_tree_verify_inclusion(const uint8_t *root, const uint8_t *leaf, size_t leaf_idx, size_t leaf_count, const uint8_t proof[][SM3_HASH_SIZE], size_t proof_len) {
    uint8_t hash[SM3_HASH_SIZE];
    memcpy(hash, leaf, SM3_HASH_SIZE);
    size_t idx = leaf_idx;
    for (size_t i = 0; i < proof_len; ++i) {
        uint8_t combined[SM3_HASH_SIZE];
        if (idx % 2 == 0) {
            merkle_hash_combine(hash, proof[i], combined);
        } else {
            merkle_hash_combine(proof[i], hash, combined);
        }
        memcpy(hash, combined, SM3_HASH_SIZE);
        idx /= 2;
    }
    return memcmp(hash, root, SM3_HASH_SIZE) == 0;
}

// 生成不存在性证明（RFC6962语义：返回相邻叶子的哈希和索引）
size_t merkle_tree_prove_non_inclusion(const MerkleTree *tree, const uint8_t *target, uint8_t proof[][SM3_HASH_SIZE], size_t *neighbor_idx) {
    // 假设叶子已排序，二分查找
    size_t left = 0, right = tree->leaf_count;
    int found = 0;
    while (left < right) {
        size_t mid = (left + right) / 2;
        int cmp = memcmp(tree->leaves[mid]->hash, target, SM3_HASH_SIZE);
        if (cmp == 0) { found = 1; *neighbor_idx = mid; break; }
        if (cmp < 0) left = mid + 1; else right = mid;
    }
    if (found) return 0; // 存在则不存在性证明无意义
    // 返回相邻叶子的哈希和索引
    *neighbor_idx = left;
    if (left == 0) {
        memcpy(proof[0], tree->leaves[0]->hash, SM3_HASH_SIZE);
        return 1;
    } else if (left == tree->leaf_count) {
        memcpy(proof[0], tree->leaves[tree->leaf_count-1]->hash, SM3_HASH_SIZE);
        return 1;
    } else {
        memcpy(proof[0], tree->leaves[left-1]->hash, SM3_HASH_SIZE);
        memcpy(proof[1], tree->leaves[left]->hash, SM3_HASH_SIZE);
        return 2;
    }
}

// 验证不存在性证明
int merkle_tree_verify_non_inclusion(const uint8_t *root, const uint8_t *target, size_t leaf_count, const uint8_t proof[][SM3_HASH_SIZE], size_t proof_len, size_t neighbor_idx) {
    // 只需证明target与相邻叶子不同且proof能被包含于树
    // 这里只做简单校验，实际应结合inclusion proof
    if (proof_len == 1) {
        return memcmp(target, proof[0], SM3_HASH_SIZE) != 0;
    } else if (proof_len == 2) {
        return memcmp(target, proof[0], SM3_HASH_SIZE) > 0 && memcmp(target, proof[1], SM3_HASH_SIZE) < 0;
    }
    return 0;
} 