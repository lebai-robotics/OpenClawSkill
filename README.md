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
from skills import connect_robot, move_to_position, get_current_position, disconnect_robot

# 连接机器人
connect_robot(host="127.0.0.1", simu=True)

# 移动到位置
move_to_position(x=200, y=0, z=200, rx=180, ry=0, rz=0, speed=50)

# 获取当前位置
pos = get_current_position()
print(f"位置：{pos['position']}")

# 断开
disconnect_robot()
```

## 接口分类

### 连接管理
- `connect_robot`, `disconnect_robot`, `is_connected`, `wait_disconnect`

### 运动控制
- **基本**: `towardj`, `movej`, `movel`, `movec`, `move_to_position`, `move_to_joint_angles`
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

详见：[API_REFERENCE.md](API_REFERENCE.md)

## 测试

```bash
# 运行完整测试
python3 test_full_api.py

# 测试机器人连接
python3 test_robot.py
```

## 文件结构

```
OpenClawSkill
├── skills/
│   ├── __init__.py          # 技能包入口
│   ├── lebai_robot.py       # 完整 API (135+ 函数)
│   ├── lebai_batch.py       # 批量操作
│   └── SKILL.md             # OpenClaw 元数据
├── tests/
│   ├── test_full_api.py     # API 测试
│   ├── test_robot.py        # 机器人测试
│   └── test_skills.py       # 单元测试
├── install.sh               # 安装脚本
├── install_on_robot.sh      # 机器人端安装脚本
├── deploy_to_robot.sh       # 一键部署脚本
├── API_REFERENCE.md         # 完整 API 文档
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
- 测试：ssh lebai@192.168.4.63
