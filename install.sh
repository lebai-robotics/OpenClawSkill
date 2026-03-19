#!/bin/bash
# Lebai Robot Skill 安装脚本 for OpenClaw

set -e

SKILL_NAME="lebai-robot"
SKILL_DIR="$HOME/.openclaw/workspace/skills/$SKILL_NAME"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "Lebai Robot Skill 安装脚本"
echo "============================================================"
echo

# 1. 检查 OpenClaw 是否安装
echo "1. 检查 OpenClaw 安装状态..."
if ! command -v openclaw &> /dev/null; then
    echo "   ⚠️  openclaw 未安装"
    echo
    echo "   请先安装 OpenClaw:"
    echo "   curl -fsSL https://openclaw.ai/install.sh | bash"
    echo
    exit 1
fi
echo "   ✓ openclaw 已安装：$(openclaw --version 2>/dev/null || echo 'unknown')"

# 2. 创建技能目录
echo
echo "2. 创建技能目录..."
mkdir -p "$SKILL_DIR"
echo "   ✓ 目录已创建：$SKILL_DIR"

# 3. 复制技能文件
echo
echo "3. 复制技能文件..."
cp -r "$SOURCE_DIR"/* "$SKILL_DIR/"
echo "   ✓ 文件已复制"

# 4. 安装 Python 依赖
echo
echo "4. 安装 Python 依赖..."
pip3 install lebai-sdk -q
echo "   ✓ 依赖已安装"

# 5. 验证安装
echo
echo "5. 验证安装..."
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "   ✓ SKILL.md 存在"
else
    echo "   ✗ SKILL.md 不存在"
    exit 1
fi

if [ -f "$SKILL_DIR/lebai_robot.py" ]; then
    echo "   ✓ lebai_robot.py 存在"
else
    echo "   ✗ lebai_robot.py 不存在"
    exit 1
fi

# 6. 创建/更新 .env 配置
echo
echo "6. 配置环境变量..."
ENV_FILE="$HOME/.openclaw/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << EOF
# Lebai Robot 配置
LEBAI_ROBOT_HOST=192.168.4.63
LEBAI_ROBOT_PORT=3030
EOF
    echo "   ✓ 已创建 $ENV_FILE"
else
    echo "   ℹ️  $ENV_FILE 已存在，跳过创建"
fi

# 完成
echo
echo "============================================================"
echo "✓ 安装完成!"
echo "============================================================"
echo
echo "技能已安装到：$SKILL_DIR"
echo
echo "下一步:"
echo "  1. 编辑 $ENV_FILE 配置机器人 IP 和端口"
echo "  2. 运行 openclaw 启动"
echo "  3. 使用以下命令测试:"
echo "     - 连接机器人：connect_robot(host='192.168.4.63', port=3030)"
echo "     - 获取位置：get_current_position()"
echo "     - 移动：movel(p={'x': 0.2, 'y': 0, 'z': 0.2, 'rx': 3.14159}, a=25, v=25)"
echo
echo "卸载命令:"
echo "  rm -rf $SKILL_DIR"
echo "============================================================"
