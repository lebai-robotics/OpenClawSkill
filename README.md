# Lebai Robot Skill 文档

完整的 Lebai 机器人控制技能，暴露 lebai-sdk 所有接口（135+ 函数）。

## 快速开始

### 1. 安装

```bash
# 在机器人上运行
cd /home/lebai
tar -xzf lebai-robot-skill.tar.gz
./install_on_robot.sh
```

### 2. 使用

```python
from skills import connect_robot, movej, movel, get_current_position, disconnect_robot

# 连接机器人
result = connect_robot(host="127.0.0.1", port=3030)
if result["success"]:
    print(f"连接成功：{result['data']['host']}")

# 移动到笛卡尔位置 (字典格式：{x, y, z, rx, ry, rz})
move_result = movel(p={"x": 0.2, "y": 0, "z": 0.2, "rx": 3.14159, "ry": 0, "rz": 0}, a=1, v=0.2)
if move_result["success"]:
    print(f"运动 ID: {move_result['data']['id']}")

# 获取当前位置
pos_result = get_current_position()
if pos_result["success"]:
    pos = pos_result["data"]
    print(f"位置：X={pos['x']:.3f}m, Y={pos['y']:.3f}m, Z={pos['z']:.3f}m")

# 断开连接
disconnect_robot()
```

## 返回格式

所有函数返回统一的标准化格式：

### 成功响应
```python
# 带数据的成功响应
{
    "success": True,
    "data": {...},      # 可选，返回的数据
    "message": "..."    # 可选，描述信息
}

# 示例
{"success": True, "data": {"status": "RUNNING"}, "message": "Success"}
```

### 错误响应
```python
{
    "success": False,
    "message": "...",   # 错误描述
    "error": "..."      # 可选，详细错误信息
}

# 示例
{"success": False, "message": "Robot not connected", "error": "Not connected"}
```

## 接口分类

### 连接管理
- `connect_robot`, `disconnect_robot`, `is_connected`, `wait_disconnect`

### 运动控制
- **基本**: `towardj`, `movej`, `movel`, `movec`
- **高级**: `move_pt`, `move_pvt`, `move_pvat`, `speedj`, `speedl`, `move_trajectory`
- **状态**: `wait_move`, `pause_move`, `resume_move`, `stop_move`, `get_running_motion`

### 系统控制
- `estop`, `get_estop_reason`, `start_sys`, `stop_sys`, `reboot`, `powerdown`, `find_zero`

### 状态读取
- `get_robot_state`, `get_tcp`, `get_current_position`, `get_current_joints`
- `get_kin_data`, `get_phy_data`, `get_payload`, `get_gravity`

### 配置设置
- `set_payload`, `set_gravity`, `set_tcp`, `set_velocity_factor`
- `enable_joint_limits`, `disable_joint_limits`
- `enable_collision_detector`, `disable_collision_detector`

### 夹爪控制
- `init_gripper`, `get_gripper`, `control_gripper`

### 位姿操作
- `save_pose`, `load_pose`, `load_tcp`, `load_frame`
- `kinematics_forward`, `kinematics_inverse`, `pose_inverse`, `pose_add`

### 任务管理
- `start_task`, `get_task_list`, `get_task_state`, `pause_task`, `cancel_task`

### I/O 控制
- **数字**: `set_do`, `get_do`, `set_dio_mode`, `get_di`
- **模拟**: `set_ao`, `get_ao`, `get_ai`
- **Modbus**: `read_coils`, `write_register`, `read_holding_registers`

### 其他
- **串口**: `write_serial`, `read_serial`, `set_serial_baud_rate`
- **LED**: `set_led`, `set_led_style`, `set_fan`, `set_voice`
- **存储**: `set_item`, `get_item`, `get_items`
- **高级**: `call`, `subscribe`, `run_plugin_cmd`

## 完整 API

详见：[skills/references/api.md](skills/references/api.md)

## 测试

```bash
# 运行完整测试
python3 tests/test_full_api.py

# 测试机器人连接
python3 tests/test_robot.py

# 运行单元测试
python3 tests/test_skills.py
```

## 文件结构

```
lebai-mcp/
├── skills/
│   ├── __init__.py          # 技能包入口
│   ├── lebai_robot.py       # 完整 API (135+ 函数)
│   ├── SKILL.md             # OpenClaw 元数据
│   └── references/
│       └── api.md           # 完整 API 文档
├── tests/
│   ├── test_full_api.py     # API 测试
│   ├── test_robot.py        # 机器人测试
│   └── test_skills.py       # 单元测试
├── install.sh               # 安装脚本
├── install_on_robot.sh      # 机器人端安装脚本
├── deploy_to_robot.sh       # 一键部署脚本
└── README.md                # 本文档
```

## 部署到机器人

```bash
# 1. 打包
tar -czvf lebai-robot-skill.tar.gz skills/ install_on_robot.sh

# 2. 复制到机器人
scp lebai-robot-skill.tar.gz lebai@192.168.4.63:/home/lebai/

# 3. SSH 登录并安装
ssh lebai@192.168.4.63
cd /home/lebai && tar -xzf lebai-robot-skill.tar.gz && ./install_on_robot.sh
```

## 环境配置

编辑 `~/.openclaw/.env`:

```env
LEBAI_ROBOT_HOST=127.0.0.1
LEBAI_ROBOT_PORT=3030
```

## 支持

- GitHub: https://github.com/lebai-robotics/OpenClawSkill
- 官方文档：https://help.lebai.ltd
