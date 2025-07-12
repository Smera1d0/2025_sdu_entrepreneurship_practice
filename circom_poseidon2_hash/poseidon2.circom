pragma circom 2.1.4;

// Poseidon2哈希算法实现（5轮简化版，变量唯一命名）
// 参数：(n,t,d) = (256,3,5)

template Poseidon2() {
    signal input in[2];
    signal output out[2];

    // 初始状态
    signal state0[3];
    state0[0] <== in[0];
    state0[1] <== in[1];
    state0[2] <== 0;

    // 第一轮
    signal temp_state1[3];
    temp_state1[0] <== state0[0] + 1;
    temp_state1[1] <== state0[1] + 1;
    temp_state1[2] <== state0[2] + 1;
    signal sbox0_2_1, sbox0_4_1, sbox0_5_1;
    signal sbox1_2_1, sbox1_4_1, sbox1_5_1;
    signal sbox2_2_1, sbox2_4_1, sbox2_5_1;
    sbox0_2_1 <== temp_state1[0] * temp_state1[0];
    sbox0_4_1 <== sbox0_2_1 * sbox0_2_1;
    sbox0_5_1 <== sbox0_4_1 * temp_state1[0];
    sbox1_2_1 <== temp_state1[1] * temp_state1[1];
    sbox1_4_1 <== sbox1_2_1 * sbox1_2_1;
    sbox1_5_1 <== sbox1_4_1 * temp_state1[1];
    sbox2_2_1 <== temp_state1[2] * temp_state1[2];
    sbox2_4_1 <== sbox2_2_1 * sbox2_2_1;
    sbox2_5_1 <== sbox2_4_1 * temp_state1[2];
    signal mds1[3];
    mds1[0] <== 2 * sbox0_5_1 + 3 * sbox1_5_1 + 1 * sbox2_5_1;
    mds1[1] <== 1 * sbox0_5_1 + 2 * sbox1_5_1 + 3 * sbox2_5_1;
    mds1[2] <== 3 * sbox0_5_1 + 1 * sbox1_5_1 + 2 * sbox2_5_1;
    signal state1[3];
    state1[0] <== mds1[0];
    state1[1] <== mds1[1];
    state1[2] <== mds1[2];

    // 第二轮
    signal temp_state2[3];
    temp_state2[0] <== state1[0] + 2;
    temp_state2[1] <== state1[1] + 2;
    temp_state2[2] <== state1[2] + 2;
    signal sbox0_2_2, sbox0_4_2, sbox0_5_2;
    signal sbox1_2_2, sbox1_4_2, sbox1_5_2;
    signal sbox2_2_2, sbox2_4_2, sbox2_5_2;
    sbox0_2_2 <== temp_state2[0] * temp_state2[0];
    sbox0_4_2 <== sbox0_2_2 * sbox0_2_2;
    sbox0_5_2 <== sbox0_4_2 * temp_state2[0];
    sbox1_2_2 <== temp_state2[1] * temp_state2[1];
    sbox1_4_2 <== sbox1_2_2 * sbox1_2_2;
    sbox1_5_2 <== sbox1_4_2 * temp_state2[1];
    sbox2_2_2 <== temp_state2[2] * temp_state2[2];
    sbox2_4_2 <== sbox2_2_2 * sbox2_2_2;
    sbox2_5_2 <== sbox2_4_2 * temp_state2[2];
    signal mds2[3];
    mds2[0] <== 2 * sbox0_5_2 + 3 * sbox1_5_2 + 1 * sbox2_5_2;
    mds2[1] <== 1 * sbox0_5_2 + 2 * sbox1_5_2 + 3 * sbox2_5_2;
    mds2[2] <== 3 * sbox0_5_2 + 1 * sbox1_5_2 + 2 * sbox2_5_2;
    signal state2[3];
    state2[0] <== mds2[0];
    state2[1] <== mds2[1];
    state2[2] <== mds2[2];

    // 第三轮
    signal temp_state3[3];
    temp_state3[0] <== state2[0] + 3;
    temp_state3[1] <== state2[1] + 3;
    temp_state3[2] <== state2[2] + 3;
    signal sbox0_2_3, sbox0_4_3, sbox0_5_3;
    signal sbox1_2_3, sbox1_4_3, sbox1_5_3;
    signal sbox2_2_3, sbox2_4_3, sbox2_5_3;
    sbox0_2_3 <== temp_state3[0] * temp_state3[0];
    sbox0_4_3 <== sbox0_2_3 * sbox0_2_3;
    sbox0_5_3 <== sbox0_4_3 * temp_state3[0];
    sbox1_2_3 <== temp_state3[1] * temp_state3[1];
    sbox1_4_3 <== sbox1_2_3 * sbox1_2_3;
    sbox1_5_3 <== sbox1_4_3 * temp_state3[1];
    sbox2_2_3 <== temp_state3[2] * temp_state3[2];
    sbox2_4_3 <== sbox2_2_3 * sbox2_2_3;
    sbox2_5_3 <== sbox2_4_3 * temp_state3[2];
    signal mds3[3];
    mds3[0] <== 2 * sbox0_5_3 + 3 * sbox1_5_3 + 1 * sbox2_5_3;
    mds3[1] <== 1 * sbox0_5_3 + 2 * sbox1_5_3 + 3 * sbox2_5_3;
    mds3[2] <== 3 * sbox0_5_3 + 1 * sbox1_5_3 + 2 * sbox2_5_3;
    signal state3[3];
    state3[0] <== mds3[0];
    state3[1] <== mds3[1];
    state3[2] <== mds3[2];

    // 第四轮
    signal temp_state4[3];
    temp_state4[0] <== state3[0] + 4;
    temp_state4[1] <== state3[1] + 4;
    temp_state4[2] <== state3[2] + 4;
    signal sbox0_2_4, sbox0_4_4, sbox0_5_4;
    signal sbox1_2_4, sbox1_4_4, sbox1_5_4;
    signal sbox2_2_4, sbox2_4_4, sbox2_5_4;
    sbox0_2_4 <== temp_state4[0] * temp_state4[0];
    sbox0_4_4 <== sbox0_2_4 * sbox0_2_4;
    sbox0_5_4 <== sbox0_4_4 * temp_state4[0];
    sbox1_2_4 <== temp_state4[1] * temp_state4[1];
    sbox1_4_4 <== sbox1_2_4 * sbox1_2_4;
    sbox1_5_4 <== sbox1_4_4 * temp_state4[1];
    sbox2_2_4 <== temp_state4[2] * temp_state4[2];
    sbox2_4_4 <== sbox2_2_4 * sbox2_2_4;
    sbox2_5_4 <== sbox2_4_4 * temp_state4[2];
    signal mds4[3];
    mds4[0] <== 2 * sbox0_5_4 + 3 * sbox1_5_4 + 1 * sbox2_5_4;
    mds4[1] <== 1 * sbox0_5_4 + 2 * sbox1_5_4 + 3 * sbox2_5_4;
    mds4[2] <== 3 * sbox0_5_4 + 1 * sbox1_5_4 + 2 * sbox2_5_4;
    signal state4[3];
    state4[0] <== mds4[0];
    state4[1] <== mds4[1];
    state4[2] <== mds4[2];

    // 第五轮
    signal temp_state5[3];
    temp_state5[0] <== state4[0] + 5;
    temp_state5[1] <== state4[1] + 5;
    temp_state5[2] <== state4[2] + 5;
    signal sbox0_2_5, sbox0_4_5, sbox0_5_5;
    signal sbox1_2_5, sbox1_4_5, sbox1_5_5;
    signal sbox2_2_5, sbox2_4_5, sbox2_5_5;
    sbox0_2_5 <== temp_state5[0] * temp_state5[0];
    sbox0_4_5 <== sbox0_2_5 * sbox0_2_5;
    sbox0_5_5 <== sbox0_4_5 * temp_state5[0];
    sbox1_2_5 <== temp_state5[1] * temp_state5[1];
    sbox1_4_5 <== sbox1_2_5 * sbox1_2_5;
    sbox1_5_5 <== sbox1_4_5 * temp_state5[1];
    sbox2_2_5 <== temp_state5[2] * temp_state5[2];
    sbox2_4_5 <== sbox2_2_5 * sbox2_2_5;
    sbox2_5_5 <== sbox2_4_5 * temp_state5[2];
    signal mds5[3];
    mds5[0] <== 2 * sbox0_5_5 + 3 * sbox1_5_5 + 1 * sbox2_5_5;
    mds5[1] <== 1 * sbox0_5_5 + 2 * sbox1_5_5 + 3 * sbox2_5_5;
    mds5[2] <== 3 * sbox0_5_5 + 1 * sbox1_5_5 + 2 * sbox2_5_5;
    signal state5[3];
    state5[0] <== mds5[0];
    state5[1] <== mds5[1];
    state5[2] <== mds5[2];

    // 输出
    out[0] <== state5[0];
    out[1] <== state5[1];
} 