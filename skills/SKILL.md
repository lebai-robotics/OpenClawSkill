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

## Usage

```python
from skills import connect_robot, movej, movel, get_current_position, disconnect_robot

# Connect
connect_robot(host="127.0.0.1", port=3030)

# Move to Cartesian position (dict: {x, y, z, rx, ry, rz} in meters and radians)
movel(p={"x": 0.2, "y": 0, "z": 0.2, "rx": 3.14159, "ry": 0, "rz": 0}, a=1, v=0.2)

# Get position (dict: {x, y, z, rx, ry, rz} in meters and radians)
pos = get_current_position()

# Disconnect
disconnect_robot()
```

## Features

- **Motion Control**: movej, movel, movec, move_pt, move_pvt, trajectory planning
- **System Control**: estop, reboot, powerdown, find_zero
- **I/O Control**: Digital/Analog I/O, Modbus, Serial communication
- **Gripper Control**: init, control, status
- **Pose Operations**: Forward/inverse kinematics, pose transformations
- **Task Management**: Start, pause, resume, cancel tasks

## Configuration

Edit `~/.openclaw/.env`:

```env
LEBAI_ROBOT_HOST=192.168.4.63
LEBAI_ROBOT_PORT=3030
```

## Author

Lebai Robotics

## License

MIT
