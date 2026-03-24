# AprilTag Skill 使用指南

AprilTag Detection Skill 用于检测 AprilTag 标签并获取相对于机器人底座的位置。

## 功能特点

- 支持两种通信方式：**Signal 模式**（推荐）和 **Modbus 模式**
- 可检测多个标签
- 支持批量查询特定标签
- 标准化返回格式

## 安装配置

### 1. 部署到机器人

```bash
# 打包
zip -r lebai-mcp.zip skills/ requirements.txt

# 复制到机器人
scp lebai-mcp.zip lebai@<robot_ip>:/home/lebai/

# SSH 登录机器人并解压
ssh lebai@<robot_ip>
cd /home/lebai && unzip -o lebai-mcp.zip
```

### 2. OpenClaw 配置

编辑 `~/.openclaw/settings.json` 添加此 skill：

```json
{
  "skills": [
    {
      "name": "lebai-robot",
      "description": "Lebai robot control with AprilTag detection",
      "path": "/home/lebai/skills",
      "module": "skills",
      "functions": [
        "connect_robot",
        "disconnect_robot",
        "movel",
        "get_current_position",
        "connect_camera",
        "find_tags",
        "get_tag_pose"
      ]
    }
  ]
}
```

## 使用示例

### Signal 模式（推荐）

```python
from skills import connect_robot, connect_camera, find_tags, get_tag_pose, movel

# 1. 连接机器人
result = connect_robot(host="192.168.4.63", port=False)
print(result)

# 2. 连接相机
result = connect_camera(camera_ip="127.0.0.1")
print(result)

# 3. 检测所有标签
result = find_tags(way="signal", signal_id=13)
if result["success"]:
    tags = result["data"]["tags"]
    for tag_id, pose in tags.items():
        print(f"Tag {tag_id}: x={pose['x']:.3f}, y={pose['y']:.3f}, z={pose['z']:.3f}")

# 4. 获取特定标签位置
result = get_tag_pose(tag_id=13, way="signal")
if result["success"]:
    pose = result["data"]["pose"]
    # 移动到标签上方 10cm
    movel(p={
        "x": pose["x"],
        "y": pose["y"],
        "z": pose["z"] + 0.1,  # 上方 10cm
        "rx": pose["rx"],
        "ry": pose["ry"],
        "rz": pose["rz"]
    }, a=1, v=0.2)

# 5. 批量检测多个标签
result = find_tags_batch(tag_ids=[13, 14, 15], way="signal")
if result["success"]:
    found = result["data"]["found"]
    missing = result["data"]["missing"]
    print(f"找到: {list(found.keys())}, 未找到: {missing}")
```

### Modbus 模式

```python
from skills import connect_robot, setup_modbus, find_tags, get_tag_pose

# 1. 连接机器人
connect_robot(host="192.168.4.63", port=False)

# 2. 设置 Modbus
result = setup_modbus(slave_id=0x07)
print(result)

# 3. 检测标签
result = find_tags(way="modbus")
if result["success"]:
    tags = result["data"]["tags"]
    for tag_id, pose in tags.items():
        print(f"Tag {tag_id}: {pose}")
```

## API 参考

### connect_camera(camera_ip, camera_id)
连接相机插件。

**参数:**
- `camera_ip`: 相机 IP 地址（默认: "127.0.0.1"）
- `camera_id`: 相机标识符（默认: "default"）

**返回:**
```json
{"success": true, "data": {"camera_ip": "127.0.0.1", "connected": true}}
```

### setup_modbus(slave_id, robot_id)
设置 Modbus 通信（Modbus 模式需要）。

**参数:**
- `slave_id`: Modbus 从机 ID（默认: 0x07）
- `robot_id`: 机器人标识符

### find_tags(way, signal_id, timeout, robot_id, camera_id)
检测 AprilTag 标签。

**参数:**
- `way`: 通信方式 - "signal" 或 "modbus"
- `signal_id`: 信号索引（Signal 模式，默认: 13）
- `timeout`: 超时时间秒数（默认: 30）

**返回:**
```json
{
  "success": true,
  "data": {
    "tags": {
      "13": {"x": 0.5, "y": 0.1, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0},
      "14": {"x": 0.6, "y": 0.2, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0}
    },
    "count": 2
  },
  "message": "Detected 2 tag(s)"
}
```

### get_tag_pose(tag_id, way, signal_id, timeout, robot_id, camera_id)
获取特定标签的位置。

**返回:**
```json
{
  "success": true,
  "data": {
    "tag_id": 13,
    "pose": {"x": 0.5, "y": 0.1, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0}
  }
}
```

### find_tags_batch(tag_ids, way, signal_id, timeout, robot_id, camera_id)
批量检测指定标签。

**返回:**
```json
{
  "success": true,
  "data": {
    "found": {"13": {...}, "14": {...}},
    "missing": [15],
    "found_count": 2,
    "requested_count": 3
  }
}
```

## 坐标系说明

- **位置**: X, Y, Z 单位为米 (m)
- **姿态**: RX, RY, RZ 单位为弧度 (rad)
- **参考系**: 相对于机器人底座坐标系

## 与 Lua 版本对比

| 特性 | Lua (apriltag.lua) | Python (apriltag.py) |
|------|-------------------|---------------------|
| 通信方式 | signal / modbus | signal / modbus |
| 返回值 | 原始字典 | 标准化响应格式 |
| 相机连接 | 内置 | 需调用 connect_camera |
| 批量查询 | 不支持 | 支持 find_tags_batch |
| 特定标签查询 | 手动实现 | get_tag_pose 内置 |
| 错误处理 | 简单 | 标准化错误响应 |

## 故障排查

### "Camera not connected"
- 确保先调用 `connect_camera()`
- 检查相机 IP 地址是否正确

### "Modbus not setup"
- Modbus 模式需要先调用 `setup_modbus()`

### "No tags detected"
- 检查 AprilTag 是否在相机视野内
- 检查相机插件是否正确安装
- 增加 `timeout` 参数

### "Timeout waiting for tag detection"
- 检查相机插件是否正在运行
- 检查信号 ID 是否正确
- 增加 `timeout` 参数

---

# AprilTag Offset Teaching 使用指南

AprilTag Offset Teaching Skill 引导用户示教抓取位置与 AprilTag 标签的相对位置。

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 接近标签                                                  │
│     ├── 移动到标签前方 10cm                                  │
│     └── 移动到标签前方 7cm (最佳相机视野)                     │
├─────────────────────────────────────────────────────────────┤
│  2. 检测标签                                                  │
│     └── 记录 tag_pose (标签中心位置)                          │
├─────────────────────────────────────────────────────────────┤
│  3. 示教模式                                                  │
│     └── 用户手动引导机器人到真实抓取点                        │
├─────────────────────────────────────────────────────────────┤
│  4. 确认位置                                                  │
│     └── 按下肩部按钮 (SHOULDER DI:0) 确认                   │
├─────────────────────────────────────────────────────────────┤
│  5. 计算偏移                                                  │
│     └── offset = pose_trans(pose_inverse(tag_pose), good_pose)│
└─────────────────────────────────────────────────────────────┘
```

## 使用示例

### 完整示教流程

```python
from skills import (
    connect_robot, connect_camera,
    teach_grasp_offset, grasp_with_offset,
    save_offset_config, load_offset_config
)

# 1. 连接机器人和相机
connect_robot(host="192.168.4.63", port=False)
connect_camera(camera_ip="127.0.0.1")

# 2. 示教偏移量
print("=== 开始示教 ===")
print("机器人将自动移动到标签位置，然后进入示教模式")
print("请引导机器人到抓取位置，然后按下肩部按钮确认")

result = teach_grasp_offset(
    tag_id=13,           # AprilTag ID
    way="signal",        # 通信方式
    signal_id=13,        # 信号索引
    open_gripper=True    # 开始前打开夹爪
)

if result["success"]:
    data = result["data"]
    print(f"\n示教完成!")
    print(f"标签位置: {data['tag_pose']}")
    print(f"抓取位置: {data['grasp_pose']}")
    print(f"偏移量: {data['offset']}")

    # 3. 保存配置
    save_offset_config(
        name="box_grasp",    # 配置名称
        tag_id=13,
        offset=data['offset']
    )
    print("\n配置已保存")
```

### 使用偏移量抓取

```python
from skills import grasp_with_offset, load_offset_config

# 方式1: 使用内存中的偏移量
grasp_with_offset(
    tag_id=13,
    offset=offset,           # 之前示教的偏移量
    approach_height=0.1,     # 抓取前上方 10cm
    grasp_height=0.0,        # 标签高度
    way="signal"
)

# 方式2: 加载保存的偏移量
config = load_offset_config(name="box_grasp")
if config["success"]:
    offset_data = config["data"]
    grasp_with_offset(
        tag_id=offset_data["tag_id"],
        offset=offset_data["offset"],
        approach_height=0.1
    )
```

## API 参考

### teach_grasp_offset(tag_id, way, signal_id, open_gripper)

引导用户示教抓取偏移量。

**参数:**
- `tag_id`: AprilTag ID (必需)
- `way`: 通信方式 - "signal" 或 "modbus" (默认: "signal")
- `signal_id`: 信号索引 (默认: 13)
- `open_gripper`: 开始前是否打开夹爪 (默认: True)

**返回:**
```json
{
  "success": true,
  "data": {
    "tag_id": 13,
    "tag_pose": {"x": 0.5, "y": 0.1, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0},
    "grasp_pose": {"x": 0.52, "y": 0.12, "z": 0.15, "rx": 3.14, "ry": 0, "rz": 0.1},
    "offset": {"x": 0.02, "y": 0.02, "z": -0.05, "rx": 0, "ry": 0, "rz": 0.1}
  },
  "message": "Successfully taught grasp offset for tag 13"
}
```

**工作流程细节:**

1. **打开夹爪** (如果 `open_gripper=True`)
2. **接近标签**: 自动移动到标签前方 10cm，再移动到 7cm（最佳相机视野）
3. **检测标签**: 获取并记录标签位姿
4. **进入示教模式**: 机器人进入可手动引导状态
5. **等待确认**: 监控肩部按钮 (SHOULDER DI:0)，按下后退出示教模式
6. **记录抓取位姿**: 获取当前 TCP 位置作为抓取点
7. **计算偏移量**: `offset = pose_trans(pose_inverse(tag_pose), grasp_pose)`

### grasp_with_offset(tag_id, offset, way, approach_height, grasp_height)

使用示教的偏移量执行抓取。

**参数:**
- `tag_id`: AprilTag ID (必需)
- `offset`: 偏移量字典 {x, y, z, rx, ry, rz} (必需)
- `way`: 通信方式 (默认: "signal")
- `signal_id`: 信号索引 (默认: 13)
- `approach_height`: 抓取前上方高度 (米，默认: 0.1)
- `grasp_height`: 抓取高度相对标签的偏移 (米，默认: 0)

**工作流程:**

1. 检测标签获取 `tag_pose`
2. 计算抓取位姿: `grasp_pose = pose_trans(tag_pose, offset)`
3. 计算接近位姿: `approach_pose = grasp_pose + (0, 0, approach_height, 0, 0, 0)`
4. 打开夹爪
5. 线性运动到接近位姿
6. 线性运动到抓取位姿
7. 关闭夹爪
8. 线性运动回接近位姿（提起物体）

### save_offset_config(name, tag_id, offset)

保存偏移量配置到机器人。

**参数:**
- `name`: 配置名称 (必需)
- `tag_id`: AprilTag ID (必需)
- `offset`: 偏移量字典 (必需)

### load_offset_config(name)

从机器人加载偏移量配置。

**参数:**
- `name`: 配置名称 (必需)

**返回:**
```json
{
  "success": true,
  "data": {
    "tag_id": 13,
    "offset": {"x": 0.02, "y": 0.02, "z": -0.05, "rx": 0, "ry": 0, "rz": 0.1}
  }
}
```

## 实际应用示例

### 多位置示教与抓取

```python
from skills import *

# 连接设备
connect_robot("192.168.4.63")
connect_camera("127.0.0.1")

# 示教多个抓取位置
teaching_tasks = [
    ("box_front", 13),
    ("box_side", 14),
    ("cylinder_top", 15)
]

for name, tag_id in teaching_tasks:
    print(f"\n示教 {name} (Tag {tag_id})...")
    result = teach_grasp_offset(tag_id=tag_id)
    if result["success"]:
        save_offset_config(name, tag_id, result["data"]["offset"])
        print(f"已保存 {name}")

# 执行抓取任务
def pick_object(config_name):
    """根据配置名称抓取物体"""
    config = load_offset_config(config_name)
    if not config["success"]:
        print(f"加载配置失败: {config_name}")
        return

    data = config["data"]
    result = grasp_with_offset(
        tag_id=data["tag_id"],
        offset=data["offset"],
        approach_height=0.15
    )
    return result

# 抓取 box_front
pick_object("box_front")
# 放置到其他地方...

# 抓取 box_side
pick_object("box_side")
# 放置到其他地方...
```

### 动态调整抓取高度

```python
# 同一标签，不同高度抓取
base_offset = load_offset_config("box_grasp")["data"]["offset"]

# 抓取顶部（偏移量 z + 0.05）
top_offset = base_offset.copy()
top_offset["z"] += 0.05
grasp_with_offset(tag_id=13, offset=top_offset, grasp_height=0.05)

# 抓取底部（偏移量 z - 0.05）
bottom_offset = base_offset.copy()
bottom_offset["z"] -= 0.05
grasp_with_offset(tag_id=13, offset=bottom_offset, grasp_height=-0.05)
```

## 与 Lua 版本对比

| 特性 | Lua (apriltag-offset.lua) | Python (apriltag_offset.py) |
|------|---------------------------|------------------------------|
| 工作流 | 自动接近→检测→示教→计算 | 相同，但封装为可调用的函数 |
| 错误处理 | pcall 简单处理 | 标准化响应格式 |
| 可复用性 | 单次使用 | 支持保存/加载配置 |
| 批量操作 | 需手动实现 | `grasp_with_offset` 直接调用 |
| 高度调整 | 手动计算 | `approach_height` 参数 |

## 故障排查

### "Failed to enter teach mode"
- 检查机器人状态是否在 IDLE
- 检查是否有其他任务正在运行

### "Shoulder button not responding"
- 检查 DI "SHOULDER" 0 是否配置正确
- 手动测试 `get_di("SHOULDER", 0)` 返回值

### "Offset calculation error"
- 检查 tag_pose 和 grasp_pose 是否有效
- 验证机器人是否支持 `pose_trans` 和 `pose_inverse` 方法
- 程序会自动回退到手动计算

### 抓取位置不准确
- 重新示教偏移量
- 检查 AprilTag 是否平整、清晰
- 调整 `approach_height` 避免碰撞

---

# YOLO Object Detection 使用指南

YOLO Object Detection Skill 使用 YOLO 模型检测物体并获取相对于机器人底座的位置。

## 功能特点

- 支持两种通信方式：**Signal 模式**（推荐）和 **Modbus 模式**
- 检测多个物体
- 支持按类别筛选物体
- 支持获取最高置信度的物体
- 标准化返回格式

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 连接相机/YOLO插件                                         │
│     └── connect_yolo_camera()                                │
├─────────────────────────────────────────────────────────────┤
│  2. 触发检测                                                  │
│     └── 设置信号或 Modbus 寄存器触发 YOLO 推理               │
├─────────────────────────────────────────────────────────────┤
│  3. 等待结果                                                  │
│     └── 轮询信号或寄存器直到检测完成                         │
├─────────────────────────────────────────────────────────────┤
│  4. 解析结果                                                  │
│     └── 从 plugin_yolo_tags 获取 JSON 数据                  │
├─────────────────────────────────────────────────────────────┤
│  5. 返回物体列表                                              │
│     └── {object_id: {pose, class, confidence}, ...}         │
└─────────────────────────────────────────────────────────────┘
```

## 使用示例

### 基本检测流程

```python
from skills import (
    connect_robot, connect_yolo_camera,
    detect_objects, get_object_pose, get_best_object
)

# 1. 连接机器人和相机
connect_robot(host="192.168.4.63", port=False)
connect_yolo_camera(camera_ip="127.0.0.1")

# 2. 检测所有物体
result = detect_objects(way="signal", signal_id=13)
if result["success"]:
    objects = result["data"]["objects"]
    print(f"检测到 {len(objects)} 个物体")

    for obj_id, obj_data in objects.items():
        print(f"  Object {obj_id}:")
        print(f"    类别: {obj_data['class']}")
        print(f"    置信度: {obj_data['confidence']:.2f}")
        print(f"    位置: x={obj_data['pose']['x']:.3f}, "
              f"y={obj_data['pose']['y']:.3f}, "
              f"z={obj_data['pose']['z']:.3f}")

# 3. 获取最佳检测结果（最高置信度）
result = get_best_object(way="signal")
if result["success"]:
    best = result["data"]["object"]
    print(f"\n最佳检测: {best['class']} (置信度: {best['confidence']:.2f})")
```

### 按类别筛选物体

```python
from skills import find_objects_by_class, get_best_object

# 查找所有瓶子
result = find_objects_by_class(obj_class="bottle", way="signal")
if result["success"]:
    bottles = result["data"]["objects"]
    print(f"找到 {len(bottles)} 个瓶子")
    for obj_id, obj_data in bottles.items():
        print(f"  Bottle {obj_id}: {obj_data['pose']}")

# 获取最佳盒子检测结果
result = get_best_object(obj_class="box", way="signal")
if result["success"]:
    box = result["data"]["object"]
    pose = box["pose"]

    # 移动到物体上方并抓取
    from skills import movel, control_gripper

    # 打开夹爪
    control_gripper(amplitude=100)

    # 移动到物体上方
    movel(p={
        "x": pose["x"],
        "y": pose["y"],
        "z": pose["z"] + 0.1,  # 上方 10cm
        "rx": pose["rx"],
        "ry": pose["ry"],
        "rz": pose["rz"]
    }, a=1, v=0.2)

    # 下降到抓取位置
    movel(p={
        "x": pose["x"],
        "y": pose["y"],
        "z": pose["z"],
        "rx": pose["rx"],
        "ry": pose["ry"],
        "rz": pose["rz"]
    }, a=1, v=0.1)

    # 关闭夹爪
    control_gripper(amplitude=0)
```

### Modbus 模式

```python
from skills import connect_robot, setup_yolo_modbus, detect_objects

# 1. 连接机器人
connect_robot(host="192.168.4.63", port=False)

# 2. 设置 Modbus
result = setup_yolo_modbus(slave_id=0x07)
print(result)

# 3. 检测物体
result = detect_objects(way="modbus")
if result["success"]:
    objects = result["data"]["objects"]
    for obj_id, obj_data in objects.items():
        print(f"Object {obj_id}: {obj_data['pose']}")
        # Note: Modbus 模式不包含 class 和 confidence 信息
```

## API 参考

### connect_yolo_camera(camera_ip, camera_id)

连接 YOLO 相机插件。

**参数:**
- `camera_ip`: 相机 IP 地址（默认: "127.0.0.1"）
- `camera_id`: 相机标识符（默认: "default"）

**返回:**
```json
{"success": true, "data": {"camera_ip": "127.0.0.1", "connected": true}}
```

### setup_yolo_modbus(slave_id, robot_id)

设置 Modbus 通信（Modbus 模式需要）。

**参数:**
- `slave_id`: Modbus 从机 ID（默认: 0x07）
- `robot_id`: 机器人标识符

### detect_objects(way, signal_id, timeout, robot_id, camera_id)

检测所有物体。

**参数:**
- `way`: 通信方式 - "signal" 或 "modbus"
- `signal_id`: 信号索引（Signal 模式，默认: 13）
- `timeout`: 超时时间秒数（默认: 30）

**返回:**
```json
{
  "success": true,
  "data": {
    "objects": {
      "1": {
        "pose": {"x": 0.5, "y": 0.1, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0},
        "class": "bottle",
        "confidence": 0.95
      },
      "2": {
        "pose": {"x": 0.6, "y": 0.2, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0},
        "class": "cup",
        "confidence": 0.87
      }
    },
    "count": 2
  },
  "message": "Detected 2 object(s)"
}
```

### get_object_pose(object_id, way, signal_id, timeout, robot_id, camera_id)

获取特定物体的位置和类别信息。

**返回:**
```json
{
  "success": true,
  "data": {
    "object_id": "1",
    "object": {
      "pose": {"x": 0.5, "y": 0.1, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0},
      "class": "bottle",
      "confidence": 0.95
    }
  }
}
```

### find_objects_by_class(obj_class, way, signal_id, timeout, robot_id, camera_id)

按类别名称查找物体。

**参数:**
- `obj_class`: 物体类别名称（如 "bottle", "box", "cup"）

**返回:**
```json
{
  "success": true,
  "data": {
    "objects": {
      "1": {"pose": {...}, "class": "bottle", "confidence": 0.95},
      "3": {"pose": {...}, "class": "bottle", "confidence": 0.82}
    },
    "count": 2,
    "requested_class": "bottle"
  }
}
```

### get_best_object(obj_class, way, signal_id, timeout, robot_id, camera_id)

获取置信度最高的物体。

**参数:**
- `obj_class`: 可选类别过滤（如果为 None，则考虑所有类别）

**返回:**
```json
{
  "success": true,
  "data": {
    "object_id": "1",
    "object": {
      "pose": {"x": 0.5, "y": 0.1, "z": 0.2, "rx": 3.14, "ry": 0, "rz": 0},
      "class": "bottle",
      "confidence": 0.95
    }
  },
  "message": "Best object: bottle with confidence 0.95"
}
```

## 实际应用示例

### 智能分拣系统

```python
from skills import *

# 连接设备
connect_robot("192.168.4.63")
connect_yolo_camera("127.0.0.1")

# 定义分类规则
categories = {
    "bottle": {"place_x": 0.3, "place_y": 0.3},
    "box": {"place_x": 0.3, "place_y": 0.0},
    "cup": {"place_x": 0.3, "place_y": -0.3}
}

def pick_and_place(obj_class):
    """抓取指定类别的物体并放置到对应位置"""

    # 检测物体
    result = find_objects_by_class(obj_class=obj_class)
    if not result["success"] or result["data"]["count"] == 0:
        print(f"未找到 {obj_class}")
        return False

    # 获取第一个物体
    objects = result["data"]["objects"]
    obj_id = list(objects.keys())[0]
    obj_data = objects[obj_id]
    pose = obj_data["pose"]

    print(f"抓取 {obj_class} (Object {obj_id}) 置信度: {obj_data['confidence']:.2f}")

    # 抓取流程
    control_gripper(amplitude=100)  # 打开夹爪

    # 移动到物体上方
    movel(p={
        "x": pose["x"], "y": pose["y"], "z": pose["z"] + 0.1,
        "rx": pose["rx"], "ry": pose["ry"], "rz": pose["rz"]
    }, a=1, v=0.2)

    # 下降抓取
    movel(p={
        "x": pose["x"], "y": pose["y"], "z": pose["z"],
        "rx": pose["rx"], "ry": pose["ry"], "rz": pose["rz"]
    }, a=1, v=0.1)

    control_gripper(amplitude=0)  # 关闭夹爪
    time.sleep(0.5)

    # 提起
    movel(p={
        "x": pose["x"], "y": pose["y"], "z": pose["z"] + 0.1,
        "rx": pose["rx"], "ry": pose["ry"], "rz": pose["rz"]
    }, a=1, v=0.2)

    # 移动到放置位置
    place_pos = categories[obj_class]
    movel(p={
        "x": place_pos["place_x"], "y": place_pos["place_y"], "z": 0.2,
        "rx": 3.14159, "ry": 0, "rz": 0
    }, a=1, v=0.3)

    # 放置
    control_gripper(amplitude=100)  # 打开夹爪

    return True

# 执行分拣
for category in categories.keys():
    while pick_and_place(category):
        print(f"继续抓取下一个 {category}")
    print(f"{category} 分拣完成")
```

## 与 Lua 版本对比

| 特性 | Lua (yolo.lua) | Python (yolo.py) |
|------|----------------|------------------|
| 通信方式 | signal / modbus | signal / modbus |
| 返回值 | 原始字典 | 标准化响应格式 |
| 类别筛选 | 手动实现 | `find_objects_by_class` 内置 |
| 最佳检测 | 手动实现 | `get_best_object` 内置 |
| 错误处理 | 简单 | 标准化错误响应 |

## 故障排查

### "Camera not connected"
- 确保先调用 `connect_yolo_camera()`
- 检查相机 IP 地址是否正确
- 确认 YOLO 插件已正确安装

### "No objects detected"
- 检查物体是否在相机视野内
- 检查 YOLO 模型是否正确加载
- 调整相机曝光和焦距
- 增加 `timeout` 参数

### 检测到的物体类别为 "unknown"
- Signal 模式支持类别信息
- Modbus 模式由于寄存器限制，不包含类别信息
- 如需类别信息，请使用 Signal 模式

### 置信度为 0
- 这是 Modbus 模式的正常现象
- Modbus 模式不传输置信度信息
- 如需置信度，请使用 Signal 模式
