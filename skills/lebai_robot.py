#!/usr/bin/env python3
"""
Lebai Robot Control Skill - Complete API

Provides comprehensive control over Lebai robotic arms.
This module exposes all available lebai-sdk interfaces.

Documentation:
    - Official Docs: https://help.lebai.ltd
    - Python SDK: https://help.lebai.ltd/SDK/Python SDK/
    - Examples: https://help.lebai.ltd/编程示例/Python 例程.html
    - FAQ: https://help.lebai.ltd/faq/

Note: Uses lebai_sdk (https://github.com/lebai-robotics/lebai-sdk)
All functions are synchronous - no asyncio required.
"""

import json
import time
import inspect
from functools import wraps
from typing import Optional, Dict, Any, List, Union, Callable

# Global registry for robot connections
_robot_registry: Dict[str, Any] = {}


def _get_robot(robot_id: str = "default"):
    """Get robot instance from registry."""
    return _robot_registry.get(robot_id)


def _set_robot(robot_id: str, robot: Any):
    """Store robot instance in registry."""
    _robot_registry[robot_id] = robot


# ============================================================================
# Helper Functions and Decorators
# ============================================================================

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


def _robot_required(func: Callable) -> Callable:
    """
    Decorator to check robot connection before executing function.

    Usage:
        @_robot_required
        def my_function(robot, ...):
            robot.some_method()
            return _success(data=..., message=...)
    """
    @wraps(func)
    def wrapper(robot_id: str = "default", *args, **kwargs) -> Dict[str, Any]:
        robot = _get_robot(robot_id)
        if not robot:
            return _error("Robot not connected", "Not connected")
        try:
            return func(robot=robot, robot_id=robot_id, *args, **kwargs)
        except Exception as e:
            return _error(f"Error: {str(e)}", str(e))
    return wrapper


# ============================================================================
# Connection Management
# ============================================================================

def discover_devices(timeout: int = 3) -> Dict[str, Any]:
    """
    Discover Lebai robots on the local network.

    Args:
        timeout: Discovery timeout in seconds (default: 3)

    Returns:
        List of discovered devices with their IP addresses
    """
    try:
        from lebai_sdk import discover_devices as sdk_discover

        result = sdk_discover(timeout)
        devices = []
        if isinstance(result, list):
            for device in result:
                if isinstance(device, dict):
                    devices.append(device)
                else:
                    devices.append({"ip": str(device)})

        return _success(
            data={"devices": devices, "count": len(devices)},
            message=f"Discovered {len(devices)} device(s)"
        )
    except Exception as e:
        return _error(f"Failed to discover devices: {str(e)}", str(e))


def connect_robot(host: str = "127.0.0.1", port: Union[int, bool] = False, robot_id: str = "default") -> Dict[str, Any]:
    """
    Connect to a Lebai robot.

    Args:
        host: Robot IP address or hostname (default: "127.0.0.1")
        port: Connection port. Accepts int or bool:
              - True: Simulation mode (port 3030)
              - False: Real robot mode (port 3031, default)
              - int: Custom port number
        robot_id: Robot identifier to register in the SDK (default: "default")

    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the connection was successful
            - data (dict, optional): Connection details including host, port, robot_id
            - message (str): Status message
            - error (str, optional): Error message if connection failed

    Examples:
        >>> connect_robot("192.168.1.100", True)  # Simulation mode
        >>> connect_robot("192.168.1.100", False)  # Real robot mode (default)
        >>> connect_robot("192.168.1.100", 3030)  # Custom port
        >>> connect_robot("192.168.1.100")  # Defaults to real robot mode (port 3031)

    Raises:
        Exception: If connection to the robot fails
    """
    try:
        from lebai_sdk import connect

        # Handle bool type for port: True=simulation(3030), False=real robot(3031)
        if isinstance(port, bool):
            port = 3030 if port else 3031

        robot = connect(host, port)
        time.sleep(0.5)

        if robot.is_connected():
            _set_robot(robot_id, robot)
            return _success(
                data={
                    "host": host,
                    "port": port,
                    "connected": True,
                    "robot_id": robot_id
                },
                message=f"Connected to robot at {host}"
            )
        return _error(f"Failed to connect to robot at {host}")
    except Exception as e:
        return _error(f"Failed to connect: {str(e)}", str(e))


def disconnect_robot(robot_id: str = "default") -> Dict[str, Any]:
    """Disconnect from a Lebai robot."""
    try:
        robot = _get_robot(robot_id)
        if robot:
            del _robot_registry[robot_id]
        return _success(message=f"Disconnected from robot {robot_id}")
    except Exception as e:
        return _error(f"Failed to disconnect: {str(e)}", str(e))


@_robot_required
def is_connected(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Check if robot is connected."""
    return _success(data={"connected": robot.is_connected()})


@_robot_required
def wait_disconnect(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Wait for robot disconnection."""
    result = robot.wait_disconnect()
    return _success(data={"result": result}, message="Wait disconnect completed")


# ============================================================================
# Motion Control - Basic
# ============================================================================

@_robot_required
def towardj(p: List[float], a: float, v: float, t: float = None, r: float = None,
            robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move to joint position (joint interpolation).

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        a: Joint acceleration in rad/s²
        v: Joint velocity in rad/s
        t: Timeout (optional)
        r: Blend radius (optional)
        robot_id: Robot identifier
    """
    result = robot.towardj(p, a, v, t, r)
    return _success(data={"id": result}, message="Move command sent")


@_robot_required
def movej(p: List[float], a: float, v: float, t: float = None, r: float = None,
          robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move to joint position with planning.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        a: Joint acceleration in rad/s²
        v: Joint velocity in rad/s
        t: Timeout (optional)
        r: Blend radius (optional)
        robot_id: Robot identifier
    """
    result = robot.movej(p, a, v, t, r)
    return _success(data={"id": result}, message="Move command sent")


@_robot_required
def movel(p: Dict[str, float], a: float, v: float, t: float = None, r: float = None,
          robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move to Cartesian position (linear motion).

    Args:
        p: Target position - {x, y, z, rx, ry, rz} dict (m, rad)
        a: Cartesian acceleration in m/s²
        v: Cartesian velocity in m/s
        t: Timeout (optional)
        r: Blend radius (optional)
        robot_id: Robot identifier
    """
    result = robot.movel(p, a, v, t, r)
    return _success(data={"id": result}, message="Move command sent")


@_robot_required
def movec(via: Dict[str, float], p: Dict[str, float], rad: float, a: float, v: float,
          t: float = None, r: float = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Circular motion.

    Args:
        via: Via point - {x, y, z, rx, ry, rz} dict (m, rad)
        p: Target position - {x, y, z, rx, ry, rz} dict (m, rad)
        rad: Radius in meters
        a: Cartesian acceleration in m/s²
        v: Cartesian velocity in m/s
        t: Timeout (optional)
        r: Blend radius (optional)
        robot_id: Robot identifier
    """
    result = robot.movec(via, p, rad, a, v, t, r)
    return _success(data={"id": result}, message="Move command sent")


# ============================================================================
# Motion Control - Advanced
# ============================================================================

@_robot_required
def move_pt(p: List[float], t: float, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move through points with time.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        t: Time
        robot_id: Robot identifier
    """
    robot.move_pt(p, t)
    return _success(message="Move pt command sent")


@_robot_required
def move_pvt(p: List[float], v: List[float], t: float, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move with position, velocity, time.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        v: Joint velocity - [j1, j2, j3, j4, j5, j6] array in rad/s
        t: Time
        robot_id: Robot identifier
    """
    robot.move_pvt(p, v, t)
    return _success(message="Move pvt command sent")


@_robot_required
def move_pvat(p: List[float], v: List[float], a: List[float], t: float,
              robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move with position, velocity, acceleration, time.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        v: Joint velocity - [j1, j2, j3, j4, j5, j6] array in rad/s
        a: Joint acceleration - [j1, j2, j3, j4, j5, j6] array in rad/s²
        t: Time
        robot_id: Robot identifier
    """
    robot.move_pvat(p, v, a, t)
    return _success(message="Move pvat command sent")


@_robot_required
def speedj(a: float, v: List[float], t: float = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Joint velocity control.

    Args:
        a: Joint acceleration in rad/s²
        v: Joint velocity - [j1, j2, j3, j4, j5, j6] array in rad/s
        t: Timeout (optional)
        robot_id: Robot identifier
    """
    result = robot.speedj(a, v, t)
    return _success(data={"id": result}, message="Speedj command sent")


@_robot_required
def speedl(a: float, v: Dict[str, float], t: float = None, frame: Dict[str, float] = None,
           robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Cartesian velocity control.

    Args:
        a: Cartesian acceleration in m/s²
        v: Cartesian velocity - {x, y, z, rx, ry, rz} dict (m/s, rad/s)
        t: Timeout (optional)
        frame: Reference frame (optional)
        robot_id: Robot identifier
    """
    result = robot.speedl(a, v, t, frame)
    return _success(data={"id": result}, message="Speedl command sent")


@_robot_required
def move_trajectory(name: str, dir: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Execute a saved trajectory."""
    result = robot.move_trajectory(name, dir)
    return _success(data={"id": result}, message="Trajectory command sent")


# ============================================================================
# Motion Control - Status
# ============================================================================

@_robot_required
def wait_move(id: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Wait for motion to complete."""
    robot.wait_move(id)
    return _success(message="Motion completed")


@_robot_required
def pause_move(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Pause current motion."""
    robot.pause_move()
    return _success(message="Motion paused")


@_robot_required
def resume_move(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Resume paused motion."""
    robot.resume_move()
    return _success(message="Motion resumed")


@_robot_required
def stop_move(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Stop current motion."""
    robot.stop_move()
    return _success(message="Motion stopped")


@_robot_required
def get_running_motion(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get running motion ID."""
    return _success(data={"id": robot.get_running_motion()})


@_robot_required
def get_motion_state(id: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get motion state by ID."""
    return _success(data={"state": robot.get_motion_state(id)})


@_robot_required
def can_move(robot_state: Any, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Check if robot can move."""
    return _success(data={"can_move": robot.can_move(robot_state)})


# ============================================================================
# System Control
# ============================================================================

@_robot_required
def estop(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Emergency stop."""
    robot.estop()
    return _success(message="Emergency stop executed")


@_robot_required
def get_estop_reason(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get emergency stop reason."""
    return _success(data={"reason": robot.get_estop_reason()})


@_robot_required
def start_sys(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Start system."""
    robot.start_sys()
    return _success(message="System started")


@_robot_required
def stop_sys(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Stop system."""
    robot.stop_sys()
    return _success(message="System stopped")


@_robot_required
def reboot(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Reboot robot controller."""
    robot.reboot()
    return _success(message="Reboot command sent")


@_robot_required
def powerdown(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Power down robot."""
    robot.powerdown()
    return _success(message="Powerdown command sent")


@_robot_required
def find_zero(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Find zero position (homing)."""
    robot.find_zero()
    return _success(message="Homing started")


# ============================================================================
# Teaching Mode
# ============================================================================

@_robot_required
def teach_mode(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Enter teaching mode."""
    robot.teach_mode()
    return _success(message="Teaching mode enabled")


@_robot_required
def end_teach_mode(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Exit teaching mode."""
    robot.end_teach_mode()
    return _success(message="Teaching mode disabled")


# ============================================================================
# Status and Data
# ============================================================================

@_robot_required
def get_robot_state(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get robot state (IDLE, RUNNING, ESTOP, etc.)."""
    return _success(data={"status": robot.get_robot_state()})


@_robot_required
def get_tcp(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Get TCP offset relative to the flange end.

    Returns the configured TCP tool center point offset from the flange.
    This is NOT the TCP position in base frame.
    For TCP position relative to base frame, use get_current_position().
    """
    return _success(data={"tcp": robot.get_tcp()})


def get_current_position(robot_id: str = "default") -> Dict[str, Any]:
    """
    Get current TCP position in base frame (meters and radians).

    Returns the TCP position relative to the robot base frame.
    For TCP offset relative to flange, use get_tcp().

    Returns:
        position: {x, y, z, rx, ry, rz} dict in meters and radians
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return _error("Robot not connected")

        kin_data = robot.get_kin_data()
        if isinstance(kin_data, dict) and 'actual_tcp_pose' in kin_data:
            tcp = kin_data['actual_tcp_pose']
            return _success(data={"position": {
                "x": tcp.get('x', 0),
                "y": tcp.get('y', 0),
                "z": tcp.get('z', 0),
                "rx": tcp.get('rx', 0),
                "ry": tcp.get('ry', 0),
                "rz": tcp.get('rz', 0)
            }})
        return _error("Unable to parse TCP data")
    except Exception as e:
        return _error(f"Error: {str(e)}", str(e))


def get_current_joints(robot_id: str = "default") -> Dict[str, Any]:
    """
    Get current joint angles in radians.

    Returns:
        joints: [j1, j2, j3, j4, j5, j6] array in radians
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return _error("Robot not connected")

        kin_data = robot.get_kin_data()
        if isinstance(kin_data, dict) and 'actual_joint_pose' in kin_data:
            joints = kin_data['actual_joint_pose']
            return _success(data={"joints": list(joints)})
        return _error("Unable to parse joint data")
    except Exception as e:
        return _error(f"Error: {str(e)}", str(e))


@_robot_required
def get_kin_data(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get kinematic data."""
    return _success(data={"kin_data": robot.get_kin_data()})


@_robot_required
def get_phy_data(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get physical data (joint temp, voltage, etc.)."""
    return _success(data={"phy_data": robot.get_phy_data()})


@_robot_required
def get_payload(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get payload configuration."""
    return _success(data={"payload": robot.get_payload()})


@_robot_required
def get_gravity(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get gravity center configuration."""
    return _success(data={"gravity": robot.get_gravity()})


@_robot_required
def get_velocity_factor(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get velocity factor."""
    return _success(data={"velocity_factor": robot.get_velocity_factor()})


# ============================================================================
# Configuration
# ============================================================================

@_robot_required
def set_payload(mass: float = None, cog: List[float] = None,
                robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set payload configuration."""
    robot.set_payload(mass=mass, cog=cog)
    return _success(message="Payload configured")


@_robot_required
def set_gravity(pose: Dict[str, float], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Set gravity center.

    Args:
        pose: Gravity center - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    robot.set_gravity(pose)
    return _success(message="Gravity center configured")


@_robot_required
def set_tcp(pose: Dict[str, float], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Set TCP offset.

    Args:
        pose: TCP offset - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    robot.set_tcp(pose)
    return _success(message="TCP configured")


@_robot_required
def set_velocity_factor(speed_factor: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set global velocity factor."""
    robot.set_velocity_factor(speed_factor)
    return _success(message="Velocity factor set")


@_robot_required
def enable_joint_limits(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Enable joint limits."""
    robot.enable_joint_limits()
    return _success(message="Joint limits enabled")


@_robot_required
def disable_joint_limits(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Disable joint limits."""
    robot.disable_joint_limits()
    return _success(message="Joint limits disabled")


@_robot_required
def enable_collision_detector(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Enable collision detector."""
    robot.enable_collision_detector()
    return _success(message="Collision detector enabled")


@_robot_required
def disable_collision_detector(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Disable collision detector."""
    robot.disable_collision_detector()
    return _success(message="Collision detector disabled")


@_robot_required
def set_collision_detector_sensitivity(sensitivity: float,
                                       robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set collision detector sensitivity."""
    robot.set_collision_detector_sensitivity(sensitivity)
    return _success(message="Sensitivity configured")


# ============================================================================
# Gripper Control
# ============================================================================

@_robot_required
def init_gripper(force: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Initialize gripper."""
    robot.init_claw(force=force)
    return _success(message="Gripper initialized")


@_robot_required
def get_gripper(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get gripper status."""
    return _success(data={"gripper": robot.get_claw()})


@_robot_required
def control_gripper(force: int = None, amplitude: int = None,
                    robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Control gripper.

    Args:
        force: Gripper force (0-100)
        amplitude: Gripper amplitude (0-100, 0=closed, 100=open)
        robot_id: Robot identifier
    """
    robot.set_claw(force=force, amplitude=amplitude)
    return _success(message="Gripper controlled")


# ============================================================================
# Pose Operations
# ============================================================================

@_robot_required
def save_pose(name: str, pose: Union[Dict[str, float], List[float]] = None,
              dir: str = None, refer: List[float] = None,
              robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Save pose to file.

    Args:
        name: Pose name
        pose: TCP pose, can be either:
              - {x, y, z, rx, ry, rz} dict in meters and radians
              - Joint angles list [j1, j2, j3, j4, j5, j6] in radians
        dir: Directory (optional)
        refer: Reference joint angles [j1, j2, j3, j4, j5, j6] in radians (optional)
        robot_id: Robot identifier
    """
    robot.save_pose(name, pose, dir, refer)
    return _success(message=f"Pose '{name}' saved")


@_robot_required
def load_pose(name: str, dir: str = None, raw_pose: bool = None,
              robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Load pose from file.

    Args:
        name: Pose name
        dir: Directory (optional)
        raw_pose: If True, return pose as stored (cartesian or joint).
                  If False/None, convert to joint angles (default).
        robot_id: Robot identifier

    Returns:
        Dict with 'pose' key containing the pose data
    """
    return _success(data={"pose": robot.load_pose(name, dir, raw_pose)})


@_robot_required
def load_tcp(name: str, dir: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Load TCP configuration from file."""
    return _success(data={"tcp": robot.load_tcp(name, dir)})


@_robot_required
def load_frame(name: str, dir: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Load frame from file."""
    return _success(data={"frame": robot.load_frame(name, dir)})


@_robot_required
def load_led_style(name: str, dir: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Load LED style from file."""
    return _success(data={"led_style": robot.load_led_style(name, dir)})


@_robot_required
def load_payload(name: str, dir: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Load payload configuration from file."""
    return _success(data={"payload": robot.load_payload(name, dir)})


@_robot_required
def pose_inverse(p: Dict[str, float], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Calculate inverse pose.

    Args:
        p: Pose - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    return _success(data={"inverse_pose": robot.pose_inverse(p)})


@_robot_required
def pose_add(pose: Dict[str, float], delta: Dict[str, float], frame: Dict[str, float] = None,
             robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Add delta to pose.

    Args:
        pose: Base pose - {x, y, z, rx, ry, rz} dict in meters and radians
        delta: Delta pose - {x, y, z, rx, ry, rz} dict in meters and radians
        frame: Reference frame (optional)
        robot_id: Robot identifier
    """
    return _success(data={"result_pose": robot.pose_add(pose, delta, frame)})


@_robot_required
def kinematics_forward(p: List[float], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Forward kinematics.

    Args:
        p: Joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        robot_id: Robot identifier

    Returns:
        TCP pose as {x, y, z, rx, ry, rz} dict
    """
    return _success(data={"tcp_pose": robot.kinematics_forward(p)})


@_robot_required
def kinematics_inverse(p: Dict[str, float], refer: List[float] = None,
                       robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Inverse kinematics.

    Args:
        p: TCP pose - {x, y, z, rx, ry, rz} dict in meters and radians
        refer: Reference joint angles (optional)
        robot_id: Robot identifier

    Returns:
        Joint angles as [j1, j2, j3, j4, j5, j6] array
    """
    return _success(data={"joint_angles": robot.kinematics_inverse(p, refer)})


@_robot_required
def in_pose(p: Dict[str, float], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Check if current pose is close to target.

    Args:
        p: Target pose - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    return _success(data={"in_pose": robot.in_pose(p)})


@_robot_required
def measure_manipulation(p: Dict[str, float], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Measure manipulation.

    Args:
        p: TCP pose - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    return _success(data={"measurement": robot.measure_manipulation(p)})


# ============================================================================
# Task Management
# ============================================================================

@_robot_required
def start_task(scene: str, params: Dict = None, dir: str = None,
               is_parallel: bool = None, loop_to: str = None,
               robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Start a task."""
    return _success(data={"task_id": robot.start_task(scene, params, dir, is_parallel, loop_to)})


@_robot_required
def get_task_list(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get task list."""
    return _success(data={"tasks": robot.get_task_list()})


@_robot_required
def get_main_task_id(robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get main task ID."""
    return _success(data={"main_task_id": robot.get_main_task_id()})


@_robot_required
def get_task_state(id: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get task state."""
    return _success(data={"state": robot.get_task_state(id)})


@_robot_required
def pause_task(id: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Pause task."""
    robot.pause_task(id)
    return _success(message="Task paused")


@_robot_required
def resume_task(id: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Resume task."""
    robot.resume_task(id)
    return _success(message="Task resumed")


@_robot_required
def cancel_task(id: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Cancel task."""
    robot.cancel_task(id)
    return _success(message="Task cancelled")


@_robot_required
def wait_task(id: int = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Wait for task completion."""
    robot.wait_task(id)
    return _success(message="Task completed")


# ============================================================================
# Digital I/O
# ============================================================================

@_robot_required
def set_dio_mode(device: str, pin: int, mode: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set digital I/O mode."""
    robot.set_dio_mode(device, pin, mode)
    return _success(message="DIO mode configured")


@_robot_required
def get_dio_mode(device: str, pin: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get digital I/O mode."""
    return _success(data={"mode": robot.get_dio_mode(device, pin)})


@_robot_required
def set_do(device: str, pin: int, value: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set digital output."""
    robot.set_do(device, pin, value)
    return _success(message=f"DO {device}:{pin} = {value}")


@_robot_required
def get_do(device: str, pin: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get digital output."""
    return _success(data={"value": robot.get_do(device, pin)})


@_robot_required
def get_dos(device: str, pin: int, num: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple digital outputs."""
    return _success(data={"values": robot.get_dos(device, pin, num)})


@_robot_required
def get_di(device: str, pin: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get digital input."""
    return _success(data={"value": robot.get_di(device, pin)})


@_robot_required
def get_dis(device: str, pin: int, num: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple digital inputs."""
    return _success(data={"values": robot.get_dis(device, pin, num)})


# ============================================================================
# Analog I/O
# ============================================================================

@_robot_required
def set_ao(device: str, pin: int, value: float, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set analog output."""
    robot.set_ao(device, pin, value)
    return _success(message=f"AO {device}:{pin} = {value}")


@_robot_required
def get_ao(device: str, pin: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get analog output."""
    return _success(data={"value": robot.get_ao(device, pin)})


@_robot_required
def get_aos(device: str, pin: int, num: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple analog outputs."""
    return _success(data={"values": robot.get_aos(device, pin, num)})


@_robot_required
def get_ai(device: str, pin: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get analog input."""
    return _success(data={"value": robot.get_ai(device, pin)})


@_robot_required
def get_ais(device: str, pin: int, num: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple analog inputs."""
    return _success(data={"values": robot.get_ais(device, pin, num)})


# ============================================================================
# Signals
# ============================================================================

@_robot_required
def set_signal(index: int, value: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set signal."""
    robot.set_signal(index, value)
    return _success(message=f"Signal {index} = {value}")


@_robot_required
def add_signal(index: int, value: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Add signal."""
    robot.add_signal(index, value)
    return _success(message=f"Signal {index} added")


@_robot_required
def get_signal(index: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get signal."""
    return _success(data={"value": robot.get_signal(index)})


@_robot_required
def get_signals(index: int, length: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple signals."""
    return _success(data={"values": robot.get_signals(index, length)})


@_robot_required
def set_signals(index: int, values: List[int], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set multiple signals."""
    robot.set_signals(index, values)
    return _success(message=f"Signals set from index {index}")


# ============================================================================
# Serial Communication
# ============================================================================

@_robot_required
def set_serial_baud_rate(device: str, baud_rate: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set serial baud rate."""
    robot.set_serial_baud_rate(device, baud_rate)
    return _success(message=f"Serial {device} baud rate set to {baud_rate}")


@_robot_required
def set_serial_timeout(device: str, timeout: float, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set serial timeout."""
    robot.set_serial_timeout(device, timeout)
    return _success(message=f"Serial {device} timeout set to {timeout}")


@_robot_required
def set_serial_parity(device: str, parity: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set serial parity."""
    robot.set_serial_parity(device, parity)
    return _success(message=f"Serial {device} parity set to {parity}")


@_robot_required
def set_flange_baud_rate(baud_rate: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set flange baud rate."""
    robot.set_flange_baud_rate(baud_rate)
    return _success(message=f"Flange baud rate set to {baud_rate}")


@_robot_required
def write_serial(device: str, data: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Write to serial port."""
    robot.write_serial(device, data)
    return _success(message=f"Data written to {device}")


@_robot_required
def read_serial(device: str, length: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Read from serial port."""
    return _success(data={"data": robot.read_serial(device, length)})


@_robot_required
def clear_serial(device: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Clear serial buffer."""
    robot.clear_serial(device)
    return _success(message=f"Serial {device} buffer cleared")


# ============================================================================
# Modbus
# ============================================================================

@_robot_required
def read_coils(device: str, pin: int, count: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus coils."""
    return _success(data={"values": robot.read_coils(device, pin, count)})


@_robot_required
def read_discrete_inputs(device: str, pin: int, count: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus discrete inputs."""
    return _success(data={"values": robot.read_discrete_inputs(device, pin, count)})


@_robot_required
def read_holding_registers(device: str, pin: int, count: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus holding registers."""
    return _success(data={"values": robot.read_holding_registers(device, pin, count)})


@_robot_required
def read_input_registers(device: str, pin: int, count: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus input registers."""
    return _success(data={"values": robot.read_input_registers(device, pin, count)})


@_robot_required
def write_single_coil(device: str, pin: int, value: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Write single Modbus coil."""
    robot.write_single_coil(device, pin, value)
    return _success(message=f"Coil {device}:{pin} = {value}")


@_robot_required
def write_single_register(device: str, pin: int, value: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Write single Modbus register."""
    robot.write_single_register(device, pin, value)
    return _success(message=f"Register {device}:{pin} = {value}")


@_robot_required
def write_multiple_coils(device: str, pin: int, values: List[int], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Write multiple Modbus coils."""
    robot.write_multiple_coils(device, pin, values)
    return _success(message=f"Multiple coils written to {device}")


@_robot_required
def write_multiple_registers(device: str, pin: int, values: List[int], robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Write multiple Modbus registers."""
    robot.write_multiple_registers(device, pin, values)
    return _success(message=f"Multiple registers written to {device}")


@_robot_required
def set_modbus_timeout(device: str, timeout: float, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set Modbus timeout."""
    robot.set_modbus_timeout(device, timeout)
    return _success(message=f"Modbus {device} timeout set to {timeout}")


@_robot_required
def set_modbus_retry(device: str, retry: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set Modbus retry count."""
    robot.set_modbus_retry(device, retry)
    return _success(message=f"Modbus {device} retry set to {retry}")


@_robot_required
def disconnect_modbus(device: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Disconnect Modbus."""
    robot.disconnect_modbus(device)
    return _success(message=f"Modbus {device} disconnected")


# ============================================================================
# LED Control
# ============================================================================

@_robot_required
def set_led(mode: str, speed: int, colors: List, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set LED."""
    robot.set_led(mode, speed, colors)
    return _success(message="LED configured")


@_robot_required
def set_led_style(style: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set LED style."""
    robot.set_led_style(style)
    return _success(message=f"LED style set to {style}")


@_robot_required
def set_fan(mode: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set fan mode."""
    robot.set_fan(mode)
    return _success(message=f"Fan mode set to {mode}")


@_robot_required
def set_voice(voice: str, volume: int, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set voice."""
    robot.set_voice(voice, volume)
    return _success(message="Voice configured")


# ============================================================================
# Items (Key-Value Storage)
# ============================================================================

@_robot_required
def set_item(key: str, value: Any, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Set item."""
    robot.set_item(key, value)
    return _success(message=f"Item '{key}' set")


@_robot_required
def get_item(key: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get item."""
    return _success(data={"item": robot.get_item(key)})


@_robot_required
def get_items(prefix: str, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Get items by prefix."""
    return _success(data={"items": robot.get_items(prefix)})


# ============================================================================
# Plugin and Advanced Features
# ============================================================================

@_robot_required
def run_plugin_cmd(name: str, params: Dict = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """Run plugin command."""
    return _success(data={"result": robot.run_plugin_cmd(name, params)})


@_robot_required
def call(method: str, param: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Call arbitrary robot method via lebai-proto protocol.
    
    Args:
        method: Method name in snake_case format (e.g., "get_kin_data", "set_tcp")
        param: JSON-formatted parameter string matching the proto definition
        robot_id: Robot identifier
    
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the call was successful
            - data (dict): Result from the method call
                - result: The response data from the robot
    
    Available Methods (snake_case naming):
        # AutoService
        - "set_auto": {"name": int, "value": bool}
        - "get_auto": {"name": int}
        
        # KinematicService
        - "get_kin_data": null
        - "set_tcp": {"x": float, "y": float, "z": float, "rx": float, "ry": float, "rz": float}
        - "get_tcp": null
        - "set_kin_factor": {"speed_factor": int}
        - "get_kin_factor": null
        
        # MotionService
        - "pause_move": null
        - "resume_move": null
        - "stop_move": null
        - "wait_move": {"id": int}
        - "get_running_motion": null
        - "get_motion_state": {"id": int}
        - "start_teach_mode": null
        - "end_teach_mode": null
        
        # ClawService
        - "init_claw": {"force": bool}
        - "set_claw": {"force": float, "amplitude": float}
        - "get_claw": null
        
        # IoService
        - "set_do": {"device": int, "pin": int, "value": int}
        - "get_do": {"device": int, "pin": int}
        - "get_di": {"device": int, "pin": int}
        - "set_ao": {"device": int, "pin": int, "value": float}
        - "get_ao": {"device": int, "pin": int}
        - "get_ai": {"device": int, "pin": int}
        
        # SafetyService
        - "enable_collision_detector": null
        - "disable_collision_detector": null
        - "set_collision_detector": {"action": int, "pause_time": int, "sensitivity": int}
        - "enable_limit": null
        - "disable_limit": null
        
        # DynamicService
        - "set_payload": {"mass": float, "cog": {"x": float, "y": float, "z": float}}
        - "get_payload": null
        - "set_gravity": {"x": float, "y": float, "z": float}
        - "get_gravity": null
        
        # PostureService
        - "get_forward_kin": {"pose": {"kind": int, "joint": [...]}}
        - "get_inverse_kin": {"pose": {...}, "refer": [...]}
        - "get_pose_inverse": {"pose": {...}}
        - "get_pose_add": {"pose": {...}, "delta": {...}}
        
        # LedService
        - "set_led": {"mode": int, "speed": int, "colors": [...]}
        - "set_voice": {"voice": int, "volume": int}
        - "set_fan": {"mode": int}
        
        # SignalService
        - "set_signal": {"key": int, "value": int}
        - "get_signal": {"key": int}
        - "add_signal": {"key": int, "value": int}
        
        # SerialService
        - "set_serial_baud_rate": {"device": str, "baud_rate": int}
        - "write_serial": {"device": str, "data": [...]}
        - "read_serial": {"device": str, "len": int}
        
        # ModbusService
        - "read_coils": {"device": str, "pin": str, "count": int}
        - "write_single_coil": {"device": str, "pin": str, "value": bool}
        - "read_holding_registers": {"device": str, "pin": str, "count": int}
        - "write_single_register": {"device": str, "pin": str, "value": int}
        
        # System
        - "get_version": null
        - "get_robot_state": null
        - "estop": null
        - "start_sys": null
        - "stop_sys": null
        - "reboot": null
    
    Usage:
        # Get kinematic data
        result = call("get_kin_data", None)
        
        # Set TCP
        result = call("set_tcp", '{"x": 0.1, "y": 0.0, "z": 0.05, "rx": 0, "ry": 0, "rz": 0}')
        
        # Set digital output
        result = call("set_do", '{"device": 0, "pin": 0, "value": 1}')
        
        # Get robot state
        result = call("get_robot_state", None)
    
    Note:
        Method names use snake_case convention as defined in lebai-proto.
        Parameters must be valid JSON strings matching the proto message format.
        See https://lebai-robotics.github.io/lebai-proto/ for complete protocol reference.
    """
    return _success(data={"result": robot.call(method, param)})


@_robot_required
def subscribe(method: str, param: str = None, robot=None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Subscribe to robot data stream.
    
    Args:
        method: Subscription method name (e.g., "robot_state", "kin_data", "phy_data", "buttons_status", "task_stdout", "message")
        param: Optional parameter for the subscription method
        robot_id: Robot identifier
    
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the subscription was successful
            - data (dict): Subscription object with next() method
                - subscription: The subscription object from lebai-sdk
        
    Usage:
        # Subscribe to kinematic data
        result = subscribe("get_kin_data")
        if result.get("success"):
            subscription = result["data"]["subscription"]
            # Call next() to wait for and receive new data
            data1 = subscription.next()  # First update
            data2 = subscription.next()  # Second update (blocks until new data arrives)
            # Can call next() repeatedly to receive latest data
        
    Note:
        The subscription object's next() method is blocking - it waits for new data.
        Call next() repeatedly to receive continuous updates.
    """
    return _success(data={"subscription": robot.subscribe(method, param)})


# ============================================================================
# Main entry point for CLI execution
# ============================================================================

if __name__ == "__main__":
    print(json.dumps({
        "message": "Lebai Robot Control Skill - Complete API",
        "description": "Comprehensive control over Lebai robotic arms",
        "categories": {
            "connection": ["discover_devices", "connect_robot", "disconnect_robot", "is_connected", "wait_disconnect"],
            "motion_basic": ["towardj", "movej", "movel", "movec"],
            "motion_advanced": ["move_pt", "move_pvt", "move_pvat", "speedj", "speedl", "move_trajectory"],
            "motion_status": ["wait_move", "pause_move", "resume_move", "stop_move", "get_running_motion", "get_motion_state", "can_move"],
            "system": ["estop", "get_estop_reason", "start_sys", "stop_sys", "reboot", "powerdown", "find_zero"],
            "teaching": ["teach_mode", "end_teach_mode"],
            "status": ["get_robot_state", "get_tcp", "get_current_position", "get_current_joints", "get_kin_data", "get_phy_data", "get_payload", "get_gravity", "get_velocity_factor"],
            "configuration": ["set_payload", "set_gravity", "set_tcp", "set_velocity_factor", "enable_joint_limits", "disable_joint_limits", "enable_collision_detector", "disable_collision_detector", "set_collision_detector_sensitivity"],
            "gripper": ["init_gripper", "get_gripper", "control_gripper"],
            "pose": ["save_pose", "load_pose", "load_tcp", "load_frame", "load_led_style", "load_payload", "pose_inverse", "pose_add", "kinematics_forward", "kinematics_inverse", "in_pose", "measure_manipulation"],
            "task": ["start_task", "get_task_list", "get_main_task_id", "get_task_state", "pause_task", "resume_task", "cancel_task", "wait_task"],
            "digital_io": ["set_dio_mode", "get_dio_mode", "set_do", "get_do", "get_dos", "get_di", "get_dis"],
            "analog_io": ["set_ao", "get_ao", "get_aos", "get_ai", "get_ais"],
            "signals": ["set_signal", "add_signal", "get_signal", "get_signals", "set_signals"],
            "serial": ["set_serial_baud_rate", "set_serial_timeout", "set_serial_parity", "set_flange_baud_rate", "write_serial", "read_serial", "clear_serial"],
            "modbus": ["read_coils", "read_discrete_inputs", "read_holding_registers", "read_input_registers", "write_single_coil", "write_single_register", "write_multiple_coils", "write_multiple_registers", "set_modbus_timeout", "set_modbus_retry", "disconnect_modbus"],
            "led": ["set_led", "set_led_style", "set_fan", "set_voice"],
            "items": ["set_item", "get_item", "get_items"],
            "advanced": ["run_plugin_cmd", "call", "subscribe"]
        }
    }, indent=2))
