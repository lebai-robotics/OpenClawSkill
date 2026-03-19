#!/usr/bin/env python3
"""
Lebai Robot 测试脚本

使用 .env 中的配置连接并测试机器人。

用法：python3 tests/test_robot.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from skills.lebai_robot import (
    connect_robot,
    disconnect_robot,
    movel,
    get_robot_status,
    get_current_position,
    get_current_joints,
    control_gripper,
    init_gripper,
    emergency_stop,
)


def main():
    # 获取配置
    host = os.getenv('LEBAI_ROBOT_HOST', '192.168.4.63')
    port = int(os.getenv('LEBAI_ROBOT_PORT', '3030'))

    print('=' * 60)
    print(f'Lebai Robot 测试')
    print('=' * 60)
    print(f'配置：{host}:{port}')
    print()

    # 1. 连接
    print('1. 连接机器人...')
    result = connect_robot(host=host, port=port)
    print(f'   结果：{result["message"]}')

    if not result.get('success'):
        print()
        print('连接失败，可能原因:')
        print('  - 机器人未开机')
        print('  - IP 地址/端口不正确')
        print('  - 网络不可达')
        return 1

    # 2. 获取状态
    print()
    print('2. 获取机器人状态...')
    status = get_robot_status()
    print(f'   状态：{status.get("status", "unknown")}')

    # 3. 获取当前位置
    print()
    print('3. 获取当前 TCP 位置...')
    pos = get_current_position()
    if pos.get('success'):
        p = pos['position']
        print(f'   位置：X={p["x"]:.1f}, Y={p["y"]:.1f}, Z={p["z"]:.1f}')
        print(f'   姿态：RX={p["rx"]:.1f}, RY={p["ry"]:.1f}, RZ={p["rz"]:.1f}')

    # 4. 获取关节角度
    print()
    print('4. 获取当前关节角度...')
    joints = get_current_joints()
    if joints.get('success'):
        j = joints['joints']
        angles = ', '.join([f'J{i}={j[i-1]:.1f}' for i in range(1, 7)])
        print(f'   {angles}')

    # 5. 测试移动（可选）
    print()
    print('5. 测试移动 (Z 轴 +10mm)...')
    if pos.get('success'):
        p = pos['position']
        move_result = movel(
            p={"x": p['x'], "y": p['y'], "z": p['z'] + 0.01,
               "rx": p['rx'], "ry": p['ry'], "rz": p['rz']},
            a=15, v=15
        )
        print(f'   结果：{move_result["message"]}')

    # 6. 初始化并测试夹爪
    print()
    print('6. 测试夹爪...')
    init_result = init_gripper()
    if init_result.get('success'):
        print(f'   初始化：{init_result["message"]}')
        gripper = control_gripper(action='open')
        print(f'   打开：{gripper["message"]}')
    else:
        print(f'   初始化失败：{init_result["message"]}')
        print(f'   (夹爪可能未连接或已初始化)')

    # 7. 断开
    print()
    print('7. 断开连接...')
    disconnect_robot()
    print('   已断开')

    print()
    print('=' * 60)
    print('测试完成!')
    print('=' * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
