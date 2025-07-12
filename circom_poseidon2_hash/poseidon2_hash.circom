pragma circom 2.1.4;

include "poseidon2.circom";

template Poseidon2Hash() {
    // 公开输入：poseidon2哈希值（256位，分为两个128位字段元素）
    signal input hash[2];
    
    // 隐私输入：哈希原象（256位，分为两个128位字段元素）
    signal input preimage[2];
    
    // 使用主poseidon2哈希函数
    component hasher = Poseidon2();
    
    // 连接输入到哈希器
    hasher.in[0] <== preimage[0];
    hasher.in[1] <== preimage[1];
    
    // 验证计算出的哈希值是否等于公开输入的哈希值
    hasher.out[0] === hash[0];
    hasher.out[1] === hash[1];
}

component main { public [hash] } = Poseidon2Hash(); 