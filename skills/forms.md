# Form Filling Guidelines

This document provides guidelines for using Lebai Robot skill functions effectively.

## Connection Forms

### discover_devices

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `timeout` | integer | No | 3 | Discovery timeout in seconds |

**Example:**
```json
{"timeout": 5}
```

### connect_robot

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `host` | string | No | "127.0.0.1" | Robot IP address or hostname |
| `port` | integer | No | 3030 | Port number |
| `robot_id` | string | No | "default" | Robot identifier |

**Example:**
```json
{"host": "192.168.4.63", "port": 3030}
```

---

## Motion Control Forms

### movej (Joint Motion)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `p` | array | Yes | Target joint angles [j1, j2, j3, j4, j5, j6] in radians |
| `a` | number | Yes | Joint acceleration in rad/s² |
| `v` | number | Yes | Joint velocity in rad/s |
| `t` | number | No | Timeout |
| `r` | number | No | Blend radius |

**Example:**
```json
{"p": [0, 0.5, -0.3, 0, 0.5, 0], "a": 10, "v": 10}
```

### movel (Linear Motion)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `p` | object | Yes | Target position {x, y, z, rx, ry, rz} in meters and radians |
| `a` | number | Yes | Cartesian acceleration in m/s² |
| `v` | number | Yes | Cartesian velocity in m/s |
| `t` | number | No | Timeout |
| `r` | number | No | Blend radius |

**Example:**
```json
{"p": {"x": 0.2, "y": 0, "z": 0.2, "rx": 3.14159, "ry": 0, "rz": 0}, "a": 1, "v": 0.2}
```

### movec (Circular Motion)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `via` | object | Yes | Via point {x, y, z, rx, ry, rz} in meters and radians |
| `p` | object | Yes | Target position {x, y, z, rx, ry, rz} in meters and radians |
| `rad` | number | Yes | Radius in meters |
| `a` | number | Yes | Cartesian acceleration in m/s² |
| `v` | number | Yes | Cartesian velocity in m/s |

**Example:**
```json
{"via": {"x": 0.1, "y": 0, "z": 0.2}, "p": {"x": 0.2, "y": 0.1, "z": 0.2}, "rad": 0.05, "a": 1, "v": 0.2}
```

---

## Gripper Control Forms

### control_gripper

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `force` | integer | No | Gripper force (0-100) |
| `amplitude` | integer | No | Position 0-100 (0=closed, 100=open) |

**Examples:**
```json
{"amplitude": 100}
{"amplitude": 0, "force": 100}
{"amplitude": 50, "force": 80}
```

---

## Configuration Forms

### set_payload

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mass` | number | Yes | Payload mass in kg |
| `cog` | object | Yes | Center of gravity {x, y, z} in meters |

**Example:**
```json
{"mass": 0.5, "cog": {"x": 0, "y": 0, "z": 0.05}}
```

### set_tcp

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pose` | object | Yes | TCP offset {x, y, z, rx, ry, rz} relative to flange |

**Example:**
```json
{"pose": {"x": 0, "y": 0, "z": 0.1, "rx": 0, "ry": 0, "rz": 0}}
```

---

## Digital I/O Forms

### set_do

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device` | string | Yes | Device name (e.g., "do1", "do2") |
| `pin` | integer | Yes | Pin number |
| `value` | integer | Yes | Value: 0 (off) or 1 (on) |

**Example:**
```json
{"device": "do1", "pin": 0, "value": 1}
```

---

## Modbus Forms

### write_multiple_registers

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device` | string | Yes | Modbus device name |
| `pin` | integer | Yes | Starting register address |
| `values` | array | Yes | Array of register values |

**Example:**
```json
{"device": "modbus0", "pin": 0, "values": [100, 200, 300]}
```

---

## Tips

1. **Always check connection** before sending motion commands
2. **Use appropriate acceleration** - start low and increase gradually
3. **Verify gripper action** with `get_gripper()` after control commands
4. **Set payload** before using teach mode or collision detection
5. **Use radians** for all angular values (not degrees)
6. **Use meters** for all linear positions (not millimeters)

## Common Patterns

### Pick and Place Sequence

```json
// 1. Move to pick position
{"name": "movel", "arguments": {"p": {"x": 0.2, "y": 0, "z": 0.1}, "a": 1, "v": 0.2}}

// 2. Close gripper
{"name": "control_gripper", "arguments": {"amplitude": 0}}

// 3. Move to place position
{"name": "movel", "arguments": {"p": {"x": 0.3, "y": 0.2, "z": 0.1}, "a": 1, "v": 0.2}}

// 4. Open gripper
{"name": "control_gripper", "arguments": {"amplitude": 100}}
```

### Home Position

```json
{"name": "movej", "arguments": {"p": [0, 0, 0, 0, 0, 0], "a": 10, "v": 10}}
```
