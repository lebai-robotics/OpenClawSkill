---
name: lebai-robot
description: Full-featured robotic arm control skill for Lebai robots with 135+ functions
---

# Lebai Robot Skill

Comprehensive Lebai robot control skill exposing all lebai-sdk interfaces (135+ functions).

## Description

Full-featured robotic arm control skill for Lebai robots. Provides access to motion control, system management, I/O operations, and advanced features.

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
movel(p={"x": 0.2, "y": 0, "z": 0.2, "rx": 3.14159, "ry": 0, "rz": 0}, a=25, v=25)

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
