#!/bin/bash

# 配置验证脚本
# 用于验证配置文件是否正确设置

set -e

echo "=================================="
echo "配置验证脚本"
echo "=================================="
echo ""

# 检查项目根目录
if [ ! -f "Makefile" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "✅ 项目根目录检查通过"
echo ""

# 检查配置文件
echo "检查配置文件..."
echo ""

if [ -f "user_config.py" ]; then
    echo "✅ 找到 user_config.py"
    
    # 检查语法
    if python3 -m py_compile user_config.py 2>/dev/null; then
        echo "   ✅ 语法检查通过"
    else
        echo "   ❌ 语法错误！请检查 user_config.py"
        exit 1
    fi
else
    echo "❌ 未找到 user_config.py"
    echo ""
    echo "请创建配置文件："
    echo "  cp user_config_template.py user_config.py"
    echo ""
    exit 1
fi

echo ""

# 运行配置测试
echo "运行配置测试..."
echo ""

if make test-config; then
    echo ""
    echo "=================================="
    echo "✅ 配置验证通过！"
    echo "=================================="
    echo ""
    echo "下一步："
    echo "  make dev      # 启动前后端"
    echo "  make backend  # 只启动后端"
    echo ""
else
    echo ""
    echo "=================================="
    echo "❌ 配置验证失败"
    echo "=================================="
    echo ""
    echo "请检查配置文件并重试"
    exit 1
fi
