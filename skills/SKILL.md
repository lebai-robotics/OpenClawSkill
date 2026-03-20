---
name: lebai-robot
description: Full-featured robotic arm control skill for Lebai robots with 135+ functions
---

# Lebai Robot Skill

Comprehensive Lebai robot control skill exposing all lebai-sdk interfaces (135+ functions).

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
```

### 5. Get Robot Status

```python
get_current_position()
get_current_joints()
get_robot_state()
```

### 6. Disconnect

```python
disconnect_robot()
```

## Documentation

| Document | Description |
|----------|-------------|
| [references/api.md](references/api.md) | Complete API reference with all 135+ functions |
| [forms.md](forms.md) | Form filling guidelines |
| [Official Docs](https://help.lebai.ltd) | Lebai official documentation |

## Coordinate System

- **Position**: X, Y, Z in meters (m)
- **Orientation**: RX, RY, RZ in radians (rad)
- **Joint Angles**: All joints in radians (rad)

## Gripper Control

| Action | Amplitude | Description |
|--------|-----------|-------------|
| `open` | 100 | Fully open gripper |
| `close` | 0 | Fully close gripper |
| `set` | 0-100 | Set specific position |
