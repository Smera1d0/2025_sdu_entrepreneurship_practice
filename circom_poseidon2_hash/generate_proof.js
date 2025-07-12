const fs = require("fs");
const path = require("path");
const snarkjs = require("snarkjs");
const { calculatePoseidon2SimpleHash } = require("./calculate_hash.js");

async function generateProof() {
    console.log("🔧 生成Poseidon2哈希证明...");
    
    // 使用测试输入
    const input = {
        preimage: ["123", "456"]
    };
    
    // 使用Poseidon2算法计算哈希值
    const hash = calculatePoseidon2SimpleHash(input.preimage);
    input.hash = hash;
    
    console.log("📝 输入数据:");
    console.log("  原象:", input.preimage);
    console.log("  哈希值:", input.hash);
    
    // 保存输入到文件
    fs.writeFileSync("input.json", JSON.stringify(input, null, 2));
    
    try {
        // 生成证明
        console.log("🔐 生成证明...");
        const { proof, publicSignals } = await snarkjs.groth16.fullProve(
            input,
            "poseidon2_hash_js/poseidon2_hash.wasm",
            "poseidon2_hash_final.zkey"
        );
        
        // 保存证明和公开信号
        fs.writeFileSync("proof.json", JSON.stringify(proof, null, 2));
        fs.writeFileSync("public.json", JSON.stringify(publicSignals, null, 2));
        
        console.log("✅ 证明生成完成!");
        console.log("📁 生成的文件:");
        console.log("  - input.json: 输入数据");
        console.log("  - proof.json: Groth16证明");
        console.log("  - public.json: 公开信号");
        console.log("公开信号:", publicSignals);
        
        return { proof, publicSignals };
        
    } catch (error) {
        console.error("❌ 生成证明时出错:", error.message);
        throw error;
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    generateProof().catch(console.error);
}

module.exports = { generateProof }; 