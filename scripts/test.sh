#!/bin/bash
# 保客通 (BaokeTong) 测试脚本
# 用法：./scripts/test.sh [OPTIONS]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 默认参数
COVERAGE=${COVERAGE:-true}
VERBOSE=${VERBOSE:-true}
STOP_ON_FIRST_FAILURE=${STOP_ON_FIRST_FAILURE:-false}
COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD:-85}

# 帮助信息
show_help() {
    cat << EOF
保客通 (BaokeTong) 测试脚本

用法：$0 [OPTIONS]

选项:
    -h, --help              显示帮助信息
    -n, --no-cov            不生成覆盖率报告
    -q, --quiet             静默模式，减少输出
    -x, --stop-on-failure   第一次失败后停止
    -t, --threshold NUM     覆盖率阈值 (默认：85)
    --unit-only             只运行单元测试
    --integration-only      只运行集成测试

示例:
    $0                      # 运行所有测试
    $0 --no-cov             # 不生成覆盖率报告
    $0 --unit-only          # 只运行单元测试
    $0 -x -t 90             # 第一次失败停止，覆盖率阈值 90%

环境变量:
    ENCRYPTION_KEY          加密密钥 (测试使用)
    DATABASE_URL            数据库连接 URL
    APP_ENV                 应用环境 (test/development)

EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--no-cov)
            COVERAGE=false
            shift
            ;;
        -q|--quiet)
            VERBOSE=false
            shift
            ;;
        -x|--stop-on-failure)
            STOP_ON_FIRST_FAILURE=true
            shift
            ;;
        -t|--threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --unit-only)
            PYTEST_MARKER="-m 'not integration'"
            shift
            ;;
        --integration-only)
            PYTEST_MARKER="-m integration"
            shift
            ;;
        *)
            echo -e "${RED}未知选项：$1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 打印信息
log_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${GREEN}[INFO]${NC} $1"
    fi
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 环境检查
log_info "=== 环境检查 ==="

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
log_info "Python 版本：$PYTHON_VERSION"

# 设置测试环境变量
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-test_encryption_key_32bytes!!!!}"
export APP_ENV="${APP_ENV:-test}"

log_info "加密密钥已设置"
log_info "应用环境：$APP_ENV"

# 安装依赖（如果需要）
if ! python3 -c "import pytest" 2>/dev/null; then
    log_warn "pytest 未安装，正在安装..."
    pip install -q -r requirements.txt
fi

# 构建 pytest 参数
PYTEST_ARGS=""

if [ "$VERBOSE" = false ]; then
    PYTEST_ARGS="$PYTEST_ARGS -q"
else
    PYTEST_ARGS="$PYTEST_ARGS -v"
fi

if [ "$STOP_ON_FIRST_FAILURE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -x"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=baoke_tong --cov=tests --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml --cov-fail-under=$COVERAGE_THRESHOLD"
fi

if [ -n "$PYTEST_MARKER" ]; then
    PYTEST_ARGS="$PYTEST_ARGS $PYTEST_MARKER"
fi

# 运行测试
log_info "=== 开始运行测试 ==="
echo ""

if pytest $PYTEST_ARGS; then
    echo ""
    log_info "=== 测试通过 ==="

    if [ "$COVERAGE" = true ]; then
        echo ""
        log_info "覆盖率报告已生成:"
        log_info "  - HTML: $PROJECT_ROOT/htmlcov/index.html"
        log_info "  - XML:  $PROJECT_ROOT/coverage.xml"

        # 在终端显示覆盖率摘要
        if [ -f "$PROJECT_ROOT/coverage.xml" ]; then
            echo ""
            log_info "=== 覆盖率摘要 ==="
            grep -A 5 "<coverage" "$PROJECT_ROOT/coverage.xml" | head -6 || true
        fi
    fi

    exit 0
else
    echo ""
    log_error "=== 测试失败 ==="

    if [ "$COVERAGE" = true ] && [ -f "$PROJECT_ROOT/coverage.xml" ]; then
        log_info "覆盖率报告仍可在以下位置查看:"
        log_info "  - HTML: $PROJECT_ROOT/htmlcov/index.html"
        log_info "  - XML:  $PROJECT_ROOT/coverage.xml"
    fi

    exit 1
fi
