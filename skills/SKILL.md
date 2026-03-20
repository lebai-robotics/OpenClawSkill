---
name: lebai-robot
description: Full-featured robotic arm control skill for Lebai robots with 135+ functions
---

# Lebai Robot Skill

Comprehensive Lebai robot control skill exposing all lebai-sdk interfaces (135+ functions).

## Description

Full-featured robotic arm control skill for Lebai robots. Provides access to motion control, system management, I/O operations, and advanced features.

## Documentation

For detailed usage instructions and API reference, see:
- **Official Documentation**: [https://help.lebai.ltd](https://help.lebai.ltd)
- **Python SDK Guide**: [https://help.lebai.ltd/SDK/Python SDK/](https://help.lebai.ltd/SDK/Python%20SDK/)
- **Programming Examples**: [https://help.lebai.ltd/编程示例/Python 例程.html](https://help.lebai.ltd/%E7%BC%96%E7%A8%8B%E7%A4%BA%E4%BE%8B/Python%20%E4%BE%8B%E7%A8%8B.html)
- **FAQ**: [https://help.lebai.ltd/faq/](https://help.lebai.ltd/faq/)

## Quick Start

### 1. Discover Robots on Network

```python
discover_devices(timeout=3)
# Returns: {"success": True, "devices": [{"ip": "192.168.4.63"}, ...], "count": 1}
```

### 2. Connect to Robot

```python
connect_robot(host="192.168.4.63", port=3030)
```

### 3. Basic Motion Control

```python
# Joint motion (radians)
movej(p=[0, 0, 0, 0, 0, 0], a=10, v=10)

# Linear motion (meters, radians)
movel(p={"x": 0.2, "y": 0, "z": 0.2, "rx": 3.14159, "ry": 0, "rz": 0}, a=1, v=0.2)
```

### 4. Gripper Control

```python
# Initialize gripper
init_gripper()

# Open gripper (amplitude=100)
control_gripper(action="open")

# Close gripper (amplitude=0)
control_gripper(action="close")

# Set specific position
control_gripper(action="set", amplitude=50, force=80)

# Get gripper status
get_gripper()
```

### 5. Get Robot Status

```python
# Get current TCP position
get_current_position()

# Get current joint angles
get_current_joints()

# Get robot state
get_robot_state()
```

### 6. Disconnect

```python
disconnect_robot()
```

## API Categories

| Category | Functions |
|----------|-----------|
| **Connection** | `discover_devices`, `connect_robot`, `disconnect_robot`, `is_connected`, `wait_disconnect` |
| **Motion - Basic** | `movej`, `movel`, `movec`, `towardj` |
| **Motion - Advanced** | `move_pt`, `move_pvt`, `move_pvat`, `speedj`, `speedl`, `move_trajectory` |
| **Motion - Status** | `wait_move`, `pause_move`, `resume_move`, `stop_move`, `get_running_motion`, `get_motion_state`, `can_move` |
| **System** | `estop`, `get_estop_reason`, `start_sys`, `stop_sys`, `reboot`, `powerdown`, `find_zero` |
| **Teaching Mode** | `teach_mode`, `end_teach_mode` |
| **Status** | `get_robot_state`, `get_tcp`, `get_current_position`, `get_current_joints`, `get_kin_data`, `get_phy_data`, `get_payload`, `get_gravity`, `get_velocity_factor` |
| **Configuration** | `set_payload`, `set_gravity`, `set_tcp`, `set_velocity_factor`, `enable_joint_limits`, `disable_joint_limits`, `enable_collision_detector`, `disable_collision_detector`, `set_collision_detector_sensitivity` |
| **Gripper** | `init_gripper`, `get_gripper`, `control_gripper` |
| **Pose Operations** | `save_pose`, `load_pose`, `load_tcp`, `load_frame`, `pose_inverse`, `pose_add`, `kinematics_forward`, `kinematics_inverse`, `in_pose`, `measure_manipulation` |
| **Task Management** | `start_task`, `get_task_list`, `get_main_task_id`, `get_task_state`, `pause_task`, `resume_task`, `cancel_task`, `wait_task` |
| **Digital I/O** | `set_dio_mode`, `get_dio_mode`, `set_do`, `get_do`, `get_dos`, `get_di`, `get_dis` |
| **Analog I/O** | `set_ao`, `get_ao`, `get_aos`, `get_ai`, `get_ais` |
| **Signals** | `set_signal`, `add_signal`, `get_signal`, `get_signals`, `set_signals` |
| **Serial** | `set_serial_baud_rate`, `set_serial_timeout`, `set_serial_parity`, `set_flange_baud_rate`, `write_serial`, `read_serial`, `clear_serial` |
| **Modbus** | `read_coils`, `read_discrete_inputs`, `read_holding_registers`, `read_input_registers`, `write_single_coil`, `write_single_register`, `write_multiple_coils`, `write_multiple_registers`, `set_modbus_timeout`, `set_modbus_retry`, `disconnect_modbus` |
| **LED/Audio** | `set_led`, `set_led_style`, `set_fan`, `set_voice` |
| **Advanced** | `run_plugin_cmd`, `call`, `subscribe` |

## FAQ

Common questions and solutions:

| Question | Description |
|----------|-------------|
| **机械臂运动指令有哪些** | Overview of all motion commands: MoveL, MoveC, MoveJ, SpeedL, SpeedJ, MovePT, MovePVT, MovePVAT, TowardJ |
| **为什么直线运动总是报错** | Troubleshooting linear motion errors |
| **为什么要设置末端负载** | Why payload configuration is required for teach mode and collision detection |
| **如何手动控制碰撞检测** | How to enable/disable collision detection and monitor collision torque |
| **为什么没有示教器** | Explanation of the teach pendant-free design |
| **新夹爪 IO 使用说明** | New gripper I/O wiring and configuration guide |
| **夹爪安装说明** | Gripper installation instructions |

## Installation

```bash
./install.sh
```

## Configuration

Edit `~/.openclaw/.env`:

```env
LEBAI_ROBOT_HOST=192.168.4.63
LEBAI_ROBOT_PORT=3030
```

## Coordinate System

- **Position**: X, Y, Z in meters (m)
- **Orientation**: RX, RY, RZ in radians (rad)
- **Joint Angles**: All joints in radians (rad)
- **Velocity**: Linear in m/s, Joint in rad/s
- **Acceleration**: Linear in m/s², Joint in rad/s²

## Gripper Control

| Action | Amplitude | Description |
|--------|-----------|-------------|
| `open` | 100 | Fully open gripper |
| `close` | 0 | Fully close gripper |
| `set` | 0-100 | Set specific position |

## Author

Lebai Robotics

## License

MIT
