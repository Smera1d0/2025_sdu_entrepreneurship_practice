CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99 -Iinclude
OPT_CFLAGS = -Wall -Wextra -O3 -std=c99 -march=native -mtune=native -Iinclude

# 检测架构和指令集支持
ifeq ($(shell uname), Darwin)
    # macOS
    ifeq ($(shell uname -m), x86_64)
        # Intel Mac
        SSE2_CFLAGS = -msse2
        AVX2_CFLAGS = -mavx2
        NEON_CFLAGS = 
    else
        # ARM Mac (Apple Silicon)
        SSE2_CFLAGS = 
        AVX2_CFLAGS = 
        NEON_CFLAGS = -march=armv8-a+simd
    endif
else
    # Linux
    ifeq ($(shell uname -m), x86_64)
        SSE2_CFLAGS = -msse2
        AVX2_CFLAGS = -mavx2
        NEON_CFLAGS = 
    else
        SSE2_CFLAGS = 
        AVX2_CFLAGS = 
        NEON_CFLAGS = -march=armv8-a+simd
    endif
endif

# 构建目录
BUILD_DIR = build
SRC_DIR = src
TEST_DIR = tests
BENCHMARK_DIR = benchmark
INCLUDE_DIR = include

# 源文件
BASIC_SRCS = $(SRC_DIR)/basic/sm3_basic.c
OPTIMIZED_SRCS = $(SRC_DIR)/optimized/sm3_optimized.c
TEST_SRCS = $(TEST_DIR)/test_sm3.c
BENCHMARK_SRCS = $(BENCHMARK_DIR)/benchmark_sm3.c
EXAMPLE_SRCS = $(TEST_DIR)/example.c

# 目标文件
BASIC_OBJS = $(BUILD_DIR)/sm3_basic.o
OPTIMIZED_OBJS = $(BUILD_DIR)/sm3_optimized.o
TEST_OBJS = $(BUILD_DIR)/test_sm3.o
BENCHMARK_OBJS = $(BUILD_DIR)/benchmark_sm3.o
EXAMPLE_OBJS = $(BUILD_DIR)/example.o

# 可执行文件
TEST_TARGET = $(BUILD_DIR)/test_sm3
BENCHMARK_TARGET = $(BUILD_DIR)/benchmark_sm3
EXAMPLE_TARGET = $(BUILD_DIR)/example

# 默认目标
all: $(BUILD_DIR) $(TEST_TARGET) $(BENCHMARK_TARGET) $(EXAMPLE_TARGET)

# 创建构建目录
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# 基础版本编译
$(BASIC_OBJS): $(BASIC_SRCS) $(INCLUDE_DIR)/sm3_basic.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(BASIC_SRCS) -o $(BASIC_OBJS)

# 优化版本编译
$(OPTIMIZED_OBJS): $(OPTIMIZED_SRCS) $(INCLUDE_DIR)/sm3_optimized.h | $(BUILD_DIR)
	$(CC) $(OPT_CFLAGS) $(SSE2_CFLAGS) $(AVX2_CFLAGS) $(NEON_CFLAGS) -c $(OPTIMIZED_SRCS) -o $(OPTIMIZED_OBJS)

# 测试程序编译
$(TEST_OBJS): $(TEST_SRCS) $(INCLUDE_DIR)/sm3_basic.h $(INCLUDE_DIR)/sm3_optimized.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(TEST_SRCS) -o $(TEST_OBJS)

# benchmark程序编译
$(BENCHMARK_OBJS): $(BENCHMARK_SRCS) $(INCLUDE_DIR)/sm3_basic.h $(INCLUDE_DIR)/sm3_optimized.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(BENCHMARK_SRCS) -o $(BENCHMARK_OBJS)

# 示例程序编译
$(EXAMPLE_OBJS): $(EXAMPLE_SRCS) $(INCLUDE_DIR)/sm3_basic.h $(INCLUDE_DIR)/sm3_optimized.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(EXAMPLE_SRCS) -o $(EXAMPLE_OBJS)

# 链接测试程序
$(TEST_TARGET): $(BASIC_OBJS) $(OPTIMIZED_OBJS) $(TEST_OBJS)
	$(CC) $(CFLAGS) -o $(TEST_TARGET) $(BASIC_OBJS) $(OPTIMIZED_OBJS) $(TEST_OBJS) -lm

# 链接benchmark程序
$(BENCHMARK_TARGET): $(BASIC_OBJS) $(OPTIMIZED_OBJS) $(BENCHMARK_OBJS)
	$(CC) $(CFLAGS) -o $(BENCHMARK_TARGET) $(BASIC_OBJS) $(OPTIMIZED_OBJS) $(BENCHMARK_OBJS) -lm

# 链接示例程序
$(EXAMPLE_TARGET): $(BASIC_OBJS) $(OPTIMIZED_OBJS) $(EXAMPLE_OBJS)
	$(CC) $(CFLAGS) -o $(EXAMPLE_TARGET) $(BASIC_OBJS) $(OPTIMIZED_OBJS) $(EXAMPLE_OBJS) -lm

# 运行测试
test: $(TEST_TARGET)
	./$(TEST_TARGET)

# 运行benchmark
benchmark: $(BENCHMARK_TARGET)
	./$(BENCHMARK_TARGET)

# 运行示例
example: $(EXAMPLE_TARGET)
	./$(EXAMPLE_TARGET)

# 快速性能测试
quick_benchmark: $(BENCHMARK_TARGET)
	@echo "运行快速性能测试..."
	./$(BENCHMARK_TARGET) | grep -E "(加速比|性能提升|流式加速比)"

# 静态库
libsm3.a: $(BASIC_OBJS) $(OPTIMIZED_OBJS) | $(BUILD_DIR)
	ar rcs $(BUILD_DIR)/libsm3.a $(BASIC_OBJS) $(OPTIMIZED_OBJS)

# 共享库
libsm3.so: $(BASIC_OBJS) $(OPTIMIZED_OBJS) | $(BUILD_DIR)
	$(CC) -shared -o $(BUILD_DIR)/libsm3.so $(BASIC_OBJS) $(OPTIMIZED_OBJS)

# 安装
install: $(TEST_TARGET) $(BENCHMARK_TARGET)
	cp $(TEST_TARGET) /usr/local/bin/sm3_test
	cp $(BENCHMARK_TARGET) /usr/local/bin/sm3_benchmark
	cp $(INCLUDE_DIR)/*.h /usr/local/include/

# 卸载
uninstall:
	rm -f /usr/local/bin/sm3_test
	rm -f /usr/local/bin/sm3_benchmark
	rm -f /usr/local/include/sm3_basic.h
	rm -f /usr/local/include/sm3_optimized.h

# 清理
clean:
	rm -rf $(BUILD_DIR)
	rm -f *.o test_sm3 test_basic test_optimized benchmark_sm3 sm3_simd.o

# 帮助信息
help:
	@echo "可用的目标:"
	@echo "  all            - 编译所有目标"
	@echo "  test           - 编译并运行测试程序"
	@echo "  benchmark      - 编译并运行性能测试程序"
	@echo "  example        - 编译并运行示例程序"
	@echo "  quick_benchmark - 运行快速性能测试"
	@echo "  libsm3.a       - 创建静态库"
	@echo "  libsm3.so      - 创建共享库"
	@echo "  install        - 安装到系统"
	@echo "  uninstall      - 从系统卸载"
	@echo "  clean          - 清理编译文件"
	@echo "  help           - 显示此帮助信息"

# 检查编译器支持
check_compiler:
	@echo "检查编译器支持..."
	@echo "GCC版本: $(shell gcc --version | head -1)"
	@echo "支持SSE2: $(shell gcc -msse2 -E - < /dev/null > /dev/null 2>&1 && echo "是" || echo "否")"
	@echo "支持AVX2: $(shell gcc -mavx2 -E - < /dev/null > /dev/null 2>&1 && echo "是" || echo "否")"

.PHONY: all test benchmark example clean install uninstall help check_compiler quick_benchmark
