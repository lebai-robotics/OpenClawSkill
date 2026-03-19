#!/bin/bash
# 一键部署到机器人控制器
# 用法：./deploy_to_robot.sh [username] [host]

USERNAME="${1:-lebai}"
HOST="${2:-192.168.4.63}"
PACKAGE="lebai-robot-skill.tar.gz"

echo "============================================================"
echo "Lebai Robot Skill 部署到机器人"
echo "============================================================"
echo "目标：$USERNAME@$HOST"
echo

# 创建安装包（始终使用最新文件）
echo "正在创建安装包..."
tar -czvf "$PACKAGE" skills/ install_on_robot.sh
echo "   ✓ 安装包已创建：$PACKAGE"
echo

echo "1. 复制安装包到机器人..."
scp "$PACKAGE" "$USERNAME@$HOST:/home/$USERNAME/"
if [ $? -ne 0 ]; then
    echo "✗ scp 失败，请检查网络连接和密码"
    exit 1
fi
echo "   ✓ 复制成功"

echo
echo "2. 在机器人上解压和安装..."
ssh "$USERNAME@$HOST" << 'ENDSSH'
cd /home/$USER
tar -xzf lebai-robot-skill.tar.gz
./install_on_robot.sh
ENDSSH

if [ $? -eq 0 ]; then
    echo
    echo "============================================================"
    echo "✓ 部署完成!"
    echo "============================================================"
else
    echo
    echo "============================================================"
    echo "⚠️  部署可能失败，请手动 SSH 到机器人检查"
    echo "============================================================"
fi
