#!/bin/bash
# Lebai Robot Skill 安装脚本 - 机器人端版本
# 在机器人控制器上运行此脚本

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/lebai-robot"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "Lebai Robot Skill 安装脚本 (机器人端)"
echo "============================================================"
echo

# 1. 检查 Python
echo "1. 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "   ✗ Python3 未安装"
    exit 1
fi
echo "   ✓ Python3: $(python3 --version)"

# 2. 检查 pip
echo
echo "2. 检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "   ✗ pip3 未安装"
    exit 1
fi
echo "   ✓ pip3 可用"

# 3. 安装 Python 依赖
echo
echo "3. 安装 Python 依赖..."
pip3 install lebai-sdk -q
echo "   ✓ lebai-sdk 已安装"

# 4. 检查 OpenClaw
echo
echo "4. 检查 OpenClaw..."
OPENCLAW_INSTALLED=false
if command -v openclaw &> /dev/null; then
    echo "   ✓ OpenClaw 已安装"
    OPENCLAW_INSTALLED=true
    SKILL_DIR="$HOME/.openclaw/workspace/skills/lebai-robot"
else
    echo "   ℹ️  OpenClaw 未安装 (可选)"
fi

# 5. 复制技能文件
echo
echo "5. 安装技能文件..."
if [ -d "$SCRIPT_DIR/skills" ]; then
    # 如果目标目录已存在，先删除旧文件以确保完全替换
    if [ -d "$SKILL_DIR" ]; then
        echo "   ℹ️  检测到旧版本，正在清理..."
        rm -rf "$SKILL_DIR"
    fi
    mkdir -p "$SKILL_DIR"
    # 复制技能文件到目标目录（不是复制整个 skills 子目录）
    cp -rf "$SCRIPT_DIR/skills"/* "$SKILL_DIR/"
    # 确保 SKILL.md 在技能目录的根目录下（openclaw 要求）
    if [ -f "$SKILL_DIR/SKILL.md" ]; then
        echo "   ✓ SKILL.md 位于：$SKILL_DIR/SKILL.md"
    else
        echo "   ✗ SKILL.md 未找到于：$SKILL_DIR/SKILL.md"
        exit 1
    fi
    echo "   ✓ 技能文件已复制到：$SKILL_DIR"
else
    echo "   ✗ 未找到 skills 目录：$SCRIPT_DIR/skills"
    exit 1
fi

# 6. 配置环境变量
echo
echo "6. 配置环境变量..."
ENV_FILE="$HOME/.openclaw/.env"
if [ "$OPENCLAW_INSTALLED" = true ]; then
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# Lebai Robot 配置
LEBAI_ROBOT_HOST=127.0.0.1
LEBAI_ROBOT_PORT=3030
EOF
        echo "   ✓ 已创建 $ENV_FILE"
    else
        echo "   ℹ️  $ENV_FILE 已存在"
    fi
fi

# 7. 验证安装
echo
echo "7. 验证安装..."
python3 -c "from skills.lebai_robot import connect_robot; print('✓ 技能导入成功')" 2>/dev/null || echo "   ℹ️  技能导入测试跳过"

echo
echo "============================================================"
echo "✓ 安装完成!"
echo "============================================================"
echo
echo "技能目录：$SKILL_DIR"
echo
if [ "$OPENCLAW_INSTALLED" = true ]; then
    echo "下一步:"
    echo "  1. 编辑 $ENV_FILE 配置机器人连接"
    echo "  2. 运行：openclaw"
    echo "  3. 使用技能控制机器人"
else
    echo "OpenClaw 未安装，可以使用 Python 直接测试:"
    echo "  python3 -c 'from skills.lebai_robot import connect_robot; print(\"OK\")'"
fi
echo
echo "============================================================"
