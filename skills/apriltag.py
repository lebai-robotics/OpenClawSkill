"""
AprilTag Detection Skill for Lebai Robot

Provides functionality to detect AprilTag markers and get their positions
relative to the robot base frame.

Supports two communication methods:
- "signal": Uses robot signals and plugin items (default)
- "modbus": Uses flange Modbus communication
"""

import json
import time
import math
from typing import Dict, Any, List, Optional, Union
from functools import wraps

# Global registry for camera connections
_camera_registry: Dict[str, Any] = {}
_modbus_registry: Dict[str, Any] = {}


def _get_camera(camera_id: str = "default"):
    """Get camera instance from registry."""
    return _camera_registry.get(camera_id)


def _set_camera(camera_id: str, camera: Any):
    """Store camera instance in registry."""
    _camera_registry[camera_id] = camera


def _get_modbus(modbus_id: str = "default"):
    """Get modbus instance from registry."""
    return _modbus_registry.get(modbus_id)


def _set_modbus(modbus_id: str, modbus: Any):
    """Store modbus instance in registry."""
    _modbus_registry[modbus_id] = modbus


# Standardized return format helpers
def _success(data: Any = None, message: str = None) -> Dict[str, Any]:
    """Create standardized success response."""
    result = {"success": True}
    if data is not None:
        result["data"] = data
    if message:
        result["message"] = message
    return result


def _error(message: str, error: str = None) -> Dict[str, Any]:
    """Create standardized error response."""
    result = {"success": False, "message": message}
    if error:
        result["error"] = error
    return result


def _robot_required(func):
    """Decorator to check robot connection before executing function."""
    @wraps(func)
    def wrapper(robot_id: str = "default", *args, **kwargs):
        from .lebai_robot import _get_robot
        robot = _get_robot(robot_id)
        if not robot:
            return _error("Robot not connected", "Not connected")
        try:
            return func(robot=robot, robot_id=robot_id, *args, **kwargs)
        except Exception as e:
            return _error(f"Error: {str(e)}", str(e))
    return wrapper


# ============================================================================
# Helper Functions
# ============================================================================

def i16_to_u16(i: int) -> int:
    """Convert signed 16-bit integer to unsigned 16-bit integer."""
    if i < 0:
        return i + 65536
    return i


def u16_to_i16(x: int) -> int:
    """Convert unsigned 16-bit integer to signed 16-bit integer."""
    if x > 32767:
        return x - 65536
    return x


def pose_to_registers(pose: List[float]) -> List[int]:
    """
    Convert pose to Modbus registers.

    Args:
        pose: [x, y, z, rz, ry, rx] in meters and radians

    Returns:
        List of 6 register values (unsigned 16-bit integers)
    """
    x = i16_to_u16(int(pose[0] * 1000))
    y = i16_to_u16(int(pose[1] * 1000))
    z = i16_to_u16(int(pose[2] * 1000))
    rz = i16_to_u16(int(pose[3] / (2 * math.pi) * 65536))
    ry = i16_to_u16(int(pose[4] / (2 * math.pi) * 65536))
    rx = i16_to_u16(int(pose[5] / (2 * math.pi) * 65536))
    return [x, y, z, rz, ry, rx]


def registers_to_pose(registers: List[int], start: int = 0) -> Dict[str, float]:
    """
    Convert Modbus registers to pose.

    Args:
        registers: List of register values
        start: Starting index in the registers list

    Returns:
        Pose dict {x, y, z, rx, ry, rz} in meters and radians
    """
    x = u16_to_i16(registers[start + 0]) / 1000.0
    y = u16_to_i16(registers[start + 1]) / 1000.0
    z = u16_to_i16(registers[start + 2]) / 1000.0
    rz = u16_to_i16(registers[start + 3]) / 65536.0 * (2 * math.pi)
    ry = u16_to_i16(registers[start + 4]) / 65536.0 * (2 * math.pi)
    rx = u16_to_i16(registers[start + 5]) / 65536.0 * (2 * math.pi)
    return {"x": x, "y": y, "z": z, "rx": rx, "ry": ry, "rz": rz}


# ============================================================================
# Camera Connection (Signal Mode)
# ============================================================================

def connect_camera(camera_ip: str = "127.0.0.1", camera_id: str = "default") -> Dict[str, Any]:
    """
    Connect to the camera plugin for AprilTag detection.

    Args:
        camera_ip: Camera IP address (default: "127.0.0.1" for local)
        camera_id: Camera identifier for registry

    Returns:
        Success response with connection details
    """
    try:
        import lebai_sdk
        camera = lebai_sdk.connect(camera_ip, True)
        time.sleep(0.5)

        if camera.is_connected():
            _set_camera(camera_id, camera)
            return _success(
                data={"camera_ip": camera_ip, "connected": True, "camera_id": camera_id},
                message=f"Connected to camera at {camera_ip}"
            )
        return _error(f"Failed to connect to camera at {camera_ip}")
    except Exception as e:
        return _error(f"Failed to connect to camera: {str(e)}", str(e))


def disconnect_camera(camera_id: str = "default") -> Dict[str, Any]:
    """Disconnect from camera."""
    try:
        if camera_id in _camera_registry:
            del _camera_registry[camera_id]
        return _success(message=f"Disconnected from camera {camera_id}")
    except Exception as e:
        return _error(f"Failed to disconnect: {str(e)}", str(e))


# ============================================================================
# Modbus Setup (Modbus Mode)
# ============================================================================

@_robot_required
def setup_modbus(slave_id: int = 0x07, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Setup Modbus communication on the robot flange.

    Args:
        slave_id: Modbus slave ID (default: 0x07)
        robot_id: Robot identifier

    Returns:
        Success response with modbus setup details
    """
    try:
        modbus = robot.modbus_new_flange()
        modbus.set_slave(slave_id)
        _set_modbus(robot_id, modbus)
        return _success(
            data={"slave_id": slave_id},
            message=f"Modbus setup complete with slave ID 0x{slave_id:02X}"
        )
    except Exception as e:
        return _error(f"Failed to setup modbus: {str(e)}", str(e))


# ============================================================================
# AprilTag Detection
# ============================================================================

@_robot_required
def find_tags(
    way: str = "signal",
    signal_id: int = 13,
    timeout: float = 30.0,
    robot=None,
    robot_id: str = "default",
    camera_id: str = "default"
) -> Dict[str, Any]:
    """
    Find AprilTag markers and return their positions relative to robot base.

    Supports two communication methods:
    - "signal": Uses robot signals and plugin items (requires connect_camera first)
    - "modbus": Uses flange Modbus communication (requires setup_modbus first)

    Args:
        way: Communication method - "signal" or "modbus"
        signal_id: Signal index for triggering detection (signal mode only)
        timeout: Maximum time to wait for detection in seconds
        robot_id: Robot identifier
        camera_id: Camera identifier (signal mode only)

    Returns:
        Dictionary mapping tag IDs to their poses:
        {
            "tag_id": {"x": float, "y": float, "z": float,
                       "rx": float, "ry": float, "rz": float},
            ...
        }

    Examples:
        >>> # Signal mode
        >>> connect_camera("127.0.0.1")
        >>> result = find_tags(way="signal", signal_id=13)
        >>> if result["success"]:
        ...     tags = result["data"]["tags"]
        ...     for tag_id, pose in tags.items():
        ...         print(f"Tag {tag_id}: x={pose['x']}, y={pose['y']}, z={pose['z']}")

        >>> # Modbus mode
        >>> setup_modbus(slave_id=0x07)
        >>> result = find_tags(way="modbus")
    """
    try:
        if way == "signal":
            return _find_tags_signal(robot, signal_id, timeout, camera_id)
        elif way == "modbus":
            return _find_tags_modbus(robot, timeout)
        else:
            return _error(f"Invalid way: {way}. Use 'signal' or 'modbus'")
    except Exception as e:
        return _error(f"Failed to find tags: {str(e)}", str(e))


def _find_tags_signal(robot, signal_id: int, timeout: float, camera_id: str) -> Dict[str, Any]:
    """Find tags using signal mode."""
    camera = _get_camera(camera_id)
    if not camera:
        return _error("Camera not connected. Call connect_camera first.")

    # Trigger detection
    camera.set_signal(signal_id, 1)

    # Wait for detection complete
    start_time = time.time()
    while camera.get_signal(signal_id) > 0:
        if time.time() - start_time > timeout:
            return _error("Timeout waiting for tag detection")
        time.sleep(0.1)

    # Get results from plugin
    item = camera.get_item("plugin_apriltag_tags")
    if not item or "value" not in item:
        return _success(data={"tags": {}}, message="No tags detected")

    tags = json.loads(item["value"])

    # Convert to standardized format
    formatted_tags = {}
    for tag_id, pose in tags.items():
        formatted_tags[str(tag_id)] = {
            "x": pose.get("x", 0),
            "y": pose.get("y", 0),
            "z": pose.get("z", 0),
            "rx": pose.get("rx", 0),
            "ry": pose.get("ry", 0),
            "rz": pose.get("rz", 0)
        }

    return _success(
        data={"tags": formatted_tags, "count": len(formatted_tags)},
        message=f"Detected {len(formatted_tags)} tag(s)"
    )


def _find_tags_modbus(robot, timeout: float) -> Dict[str, Any]:
    """Find tags using modbus mode."""
    modbus = _get_modbus()
    if not modbus:
        return _error("Modbus not setup. Call setup_modbus first.")

    # Get current flange pose
    kin_data = robot.get_kin_data()
    if not isinstance(kin_data, dict) or "actual_tcp_pose" not in kin_data:
        return _error("Failed to get current flange pose")

    tcp = kin_data["actual_tcp_pose"]
    flange_pose = [tcp.get("x", 0), tcp.get("y", 0), tcp.get("z", 0),
                   tcp.get("rz", 0), tcp.get("ry", 0), tcp.get("rx", 0)]

    # Write flange pose to registers (starting at 302)
    registers = pose_to_registers(flange_pose)
    modbus.write_multiple_registers(302, registers)

    # Trigger detection
    modbus.write_single_register(300, 1)

    # Wait for detection complete
    start_time = time.time()
    while modbus.read_holding_registers(300, 2)[0] != 0:
        if time.time() - start_time > timeout:
            return _error("Timeout waiting for tag detection")
        time.sleep(0.1)

    # Read number of detected tags
    num_tags = modbus.read_holding_registers(301, 2)[0]

    # Read each tag data
    tags = {}
    for i in range(1, num_tags + 1):
        tag_data = modbus.read_holding_registers(301 + 10 * i, 7)
        tag_id = str(tag_data[0])
        pose = registers_to_pose(tag_data, 1)
        tags[tag_id] = pose

    return _success(
        data={"tags": tags, "count": num_tags},
        message=f"Detected {num_tags} tag(s)"
    )


@_robot_required
def get_tag_pose(
    tag_id: Union[int, str],
    way: str = "signal",
    signal_id: int = 13,
    timeout: float = 30.0,
    robot=None,
    robot_id: str = "default",
    camera_id: str = "default"
) -> Dict[str, Any]:
    """
    Get the pose of a specific AprilTag.

    Args:
        tag_id: The ID of the tag to find
        way: Communication method - "signal" or "modbus"
        signal_id: Signal index for triggering detection
        timeout: Maximum time to wait for detection
        robot_id: Robot identifier
        camera_id: Camera identifier

    Returns:
        Pose dict {x, y, z, rx, ry, rz} if tag found

    Examples:
        >>> result = get_tag_pose(tag_id=13, way="signal")
        >>> if result["success"]:
        ...     pose = result["data"]["pose"]
        ...     print(f"Tag at: x={pose['x']:.3f}, y={pose['y']:.3f}, z={pose['z']:.3f}")
    """
    result = find_tags(way, signal_id, timeout, robot_id, camera_id)
    if not result["success"]:
        return result

    tags = result["data"]["tags"]
    tag_key = str(tag_id)

    if tag_key not in tags:
        return _error(f"Tag {tag_id} not found", f"Available tags: {list(tags.keys())}")

    return _success(
        data={"tag_id": tag_id, "pose": tags[tag_key]},
        message=f"Found tag {tag_id}"
    )


# ============================================================================
# Batch Operations
# ============================================================================

@_robot_required
def find_tags_batch(
    tag_ids: List[Union[int, str]],
    way: str = "signal",
    signal_id: int = 13,
    timeout: float = 30.0,
    robot=None,
    robot_id: str = "default",
    camera_id: str = "default"
) -> Dict[str, Any]:
    """
    Find multiple specific AprilTags in one detection cycle.

    Args:
        tag_ids: List of tag IDs to find
        way: Communication method - "signal" or "modbus"
        signal_id: Signal index for triggering detection
        timeout: Maximum time to wait for detection
        robot_id: Robot identifier
        camera_id: Camera identifier

    Returns:
        Dictionary with found tags and list of missing tags

    Examples:
        >>> result = find_tags_batch([13, 14, 15], way="signal")
        >>> if result["success"]:
        ...     found = result["data"]["found"]
        ...     missing = result["data"]["missing"]
        ...     print(f"Found: {list(found.keys())}, Missing: {missing}")
    """
    result = find_tags(way, signal_id, timeout, robot_id, camera_id)
    if not result["success"]:
        return result

    all_tags = result["data"]["tags"]
    found = {}
    missing = []

    for tag_id in tag_ids:
        tag_key = str(tag_id)
        if tag_key in all_tags:
            found[tag_key] = all_tags[tag_key]
        else:
            missing.append(tag_id)

    return _success(
        data={
            "found": found,
            "missing": missing,
            "found_count": len(found),
            "requested_count": len(tag_ids)
        },
        message=f"Found {len(found)}/{len(tag_ids)} requested tag(s)"
    )


# ============================================================================
# Main entry point for CLI execution
# ============================================================================

if __name__ == "__main__":
    import json
    print(json.dumps({
        "message": "AprilTag Detection Skill",
        "description": "Detect AprilTag markers and get their positions relative to robot base",
        "methods": ["signal", "modbus"],
        "functions": [
            "connect_camera", "disconnect_camera",
            "setup_modbus",
            "find_tags", "get_tag_pose", "find_tags_batch"
        ]
    }, indent=2))
