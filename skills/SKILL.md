---
name: lebai-robot
description: Full-featured robotic arm control skill for Lebai robots with 135+ functions including AprilTag detection
---

# Lebai Robot Skill

Comprehensive Lebai robot control skill exposing all lebai-sdk interfaces (135+ functions) plus AprilTag detection.

## Quick Start

### 1. Discover Robots on Network

```python
discover_devices(timeout=3)
# Returns: {"success": True, "devices": [{"ip": "192.168.4.63"}, ...], "count": 1}
```

### 2. Connect to Robot

```python
# Simulation mode (port=True or port=3030)
connect_robot(host="127.0.0.1", port=True)

# Real robot mode (port=False or port=3031, default)
connect_robot(host="192.168.4.63", port=False)
connect_robot(host="192.168.4.63")  # Defaults to real robot mode
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
control_gripper(amplitude=100)

# Close gripper (amplitude=0)
control_gripper(amplitude=0)
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

## AprilTag Detection

Detect AprilTag markers and get their positions relative to robot base frame.

### Quick Start

```python
from skills import connect_camera, find_tags, get_tag_pose

# Signal Mode (default)
connect_camera("127.0.0.1")
result = find_tags(way="signal", signal_id=13)
if result["success"]:
    tags = result["data"]["tags"]
    for tag_id, pose in tags.items():
        print(f"Tag {tag_id}: x={pose['x']:.3f}m, y={pose['y']:.3f}m, z={pose['z']:.3f}m")

# Get specific tag
result = get_tag_pose(tag_id=13, way="signal")
if result["success"]:
    pose = result["data"]["pose"]
    # Use pose for robot motion
    movel(p={"x": pose["x"], "y": pose["y"], "z": pose["z"]+0.1,
             "rx": pose["rx"], "ry": pose["ry"], "rz": pose["rz"]}, a=1, v=0.2)
```

### Communication Methods

| Method | Description | Setup Required |
|--------|-------------|----------------|
| `signal` | Uses robot signals and plugin items | `connect_camera()` |
| `modbus` | Uses flange Modbus communication | `setup_modbus()` |

### Functions

| Function | Description |
|----------|-------------|
| `connect_camera(camera_ip)` | Connect to camera plugin |
| `setup_modbus(slave_id)` | Setup Modbus communication |
| `find_tags(way, signal_id)` | Detect all AprilTags |
| `get_tag_pose(tag_id, way)` | Get specific tag pose |
| `find_tags_batch(tag_ids, way)` | Find multiple specific tags |

## AprilTag Offset Teaching

Guide users to teach grasp positions relative to AprilTag markers.

### Teaching Workflow

```python
from skills import teach_grasp_offset, grasp_with_offset, save_offset_config

# 1. Teach offset for a tag
result = teach_grasp_offset(tag_id=13, way="signal")
if result["success"]:
    tag_pose = result["data"]["tag_pose"]
    grasp_pose = result["data"]["grasp_pose"]
    offset = result["data"]["offset"]
    print(f"Offset from tag to grasp: {offset}")

# 2. Save offset for later use
save_offset_config(name="box_grasp", tag_id=13, offset=offset)

# 3. Later: use offset to grasp
grasp_with_offset(
    tag_id=13,
    offset=offset,
    approach_height=0.1,  # 10cm above
    grasp_height=0.0      # At tag height
)
```

### Functions

| Function | Description |
|----------|-------------|
| `teach_grasp_offset(tag_id, way)` | Guide user to teach grasp offset |
| `grasp_with_offset(tag_id, offset, way)` | Grasp using taught offset |
| `save_offset_config(name, tag_id, offset)` | Save offset to robot |
| `load_offset_config(name)` | Load saved offset from robot |

## YOLO Object Detection

Detect objects using YOLO and get their positions relative to robot base frame.

### Quick Start

```python
from skills import connect_yolo_camera, detect_objects, get_object_pose, get_best_object

# Signal Mode (default)
connect_yolo_camera("127.0.0.1")
result = detect_objects(way="signal", signal_id=13)
if result["success"]:
    objects = result["data"]["objects"]
    for obj_id, obj_data in objects.items():
        print(f"Object {obj_id}: {obj_data['class']} at x={obj_data['pose']['x']:.3f}")

# Get specific object
result = get_object_pose(object_id=1, way="signal")
if result["success"]:
    obj = result["data"]["object"]
    print(f"Object {obj['class']}: {obj['pose']}")

# Find objects by class
result = find_objects_by_class(obj_class="bottle", way="signal")
if result["success"]:
    bottles = result["data"]["objects"]
    print(f"Found {len(bottles)} bottle(s)")

# Get best detection (highest confidence)
result = get_best_object(obj_class="box", way="signal")
if result["success"]:
    best = result["data"]["object"]
    print(f"Best box: {best['pose']} (confidence: {best['confidence']})")
```

### Communication Methods

| Method | Description | Setup Required |
|--------|-------------|----------------|
| `signal` | Uses robot signals and plugin items | `connect_yolo_camera()` |
| `modbus` | Uses flange Modbus communication | `setup_yolo_modbus()` |

### Functions

| Function | Description |
|----------|-------------|
| `connect_yolo_camera(camera_ip)` | Connect to YOLO camera plugin |
| `setup_yolo_modbus(slave_id)` | Setup Modbus for YOLO |
| `detect_objects(way, signal_id)` | Detect all objects |
| `get_object_pose(obj_id, way)` | Get specific object pose |
| `find_objects_by_class(class, way)` | Find objects by class name |
| `get_best_object(class, way)` | Get highest confidence object |
