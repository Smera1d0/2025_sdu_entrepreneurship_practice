const fs = require("fs");

// Poseidon2哈希值计算脚本（与circom主电路一致，5轮简化版）
// 参数：(n,t,d) = (256,3,5)

function calculatePoseidon2SimpleHash(preimage) {
    console.log("🔍 计算Poseidon2哈希值...");
    console.log("输入:", preimage);
    
    // 转换为BigInt
    let state = [
        BigInt(preimage[0]),
        BigInt(preimage[1]),
        BigInt(0) // 填充为0
    ];
    
    console.log("初始状态:", state.map(s => s.toString()));
    
    // 有限字段模数 (使用circom的默认字段)
    const FIELD_MODULUS = BigInt("21888242871839275222246405745257275088548364400416034343698204186575808495617");
    
    // 模运算函数
    function mod(x) {
        return ((x % FIELD_MODULUS) + FIELD_MODULUS) % FIELD_MODULUS;
    }
    
    // S-box函数 (x^5)
    function sbox(x) {
        let x2 = mod(x * x);
        let x4 = mod(x2 * x2);
        return mod(x4 * x);
    }
    
    // 执行5轮
    for (let round = 1; round <= 5; round++) {
        console.log(`\n轮 ${round}/5:`);
        
        // 添加轮常数
        let temp_state = [
            mod(state[0] + BigInt(round)),
            mod(state[1] + BigInt(round)),
            mod(state[2] + BigInt(round))
        ];
        
        console.log("  添加轮常数后:", temp_state.map(s => s.toString()));
        
        // S-box层 (所有元素都应用S-box)
        let sbox_result = [
            sbox(temp_state[0]),
            sbox(temp_state[1]),
            sbox(temp_state[2])
        ];
        
        console.log("  S-box后:", sbox_result.map(s => s.toString()));
        
        // MDS矩阵乘法
        let mds_temp = [
            mod(2n * sbox_result[0] + 3n * sbox_result[1] + 1n * sbox_result[2]),
            mod(1n * sbox_result[0] + 2n * sbox_result[1] + 3n * sbox_result[2]),
            mod(3n * sbox_result[0] + 1n * sbox_result[1] + 2n * sbox_result[2])
        ];
        
        state = mds_temp;
        console.log("  MDS矩阵乘法后:", state.map(s => s.toString()));
    }
    
    // 输出前两个状态元素作为256位哈希值
    const hash = [state[0].toString(), state[1].toString()];
    
    console.log("\n✅ 哈希值计算完成!");
    console.log("输出哈希值:", hash);
    
    return hash;
}

// 测试函数
function testPoseidon2Simple() {
    console.log("🧪 测试Poseidon2哈希算法");
    console.log("=" * 50);
    
    // 测试用例
    const testCases = [
        {
            name: "简单测试",
            input: ["123", "456"]
        },
        {
            name: "零值测试",
            input: ["0", "0"]
        },
        {
            name: "大数测试",
            input: ["999999999", "888888888"]
        }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n📝 ${testCase.name}:`);
        const hash = calculatePoseidon2SimpleHash(testCase.input);
        
        // 保存到文件
        const output = {
            preimage: testCase.input,
            hash: hash
        };
        
        const filename = `test_${testCase.name.replace(/\s+/g, '_').toLowerCase()}.json`;
        fs.writeFileSync(filename, JSON.stringify(output, null, 2));
        console.log(`💾 保存到 ${filename}`);
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    testPoseidon2Simple();
}

module.exports = { calculatePoseidon2SimpleHash }; 