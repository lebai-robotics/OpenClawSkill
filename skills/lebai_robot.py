#!/usr/bin/env python3
"""
Lebai Robot Control Skill - Complete API

Provides comprehensive control over Lebai robotic arms.
This module exposes all available lebai-sdk interfaces.

Note: Uses lebai_sdk (https://github.com/lebai-robotics/lebai-sdk)
All functions are synchronous - no asyncio required.
"""

import json
import time
import inspect
from typing import Optional, Dict, Any, List, Union

# Global registry for robot connections
_robot_registry: Dict[str, Any] = {}


def _get_robot(robot_id: str = "default"):
    """Get robot instance from registry."""
    return _robot_registry.get(robot_id)


def _set_robot(robot_id: str, robot: Any):
    """Store robot instance in registry."""
    _robot_registry[robot_id] = robot


# ============================================================================
# Connection Management
# ============================================================================

def connect_robot(host: str = "127.0.0.1", port: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Connect to a Lebai robot.

    Args:
        host: Robot IP address or hostname
        port: Port number (optional, defaults to 3030)
        robot_id: Robot identifier (default: "default")

    Returns:
        Connection status and robot information
    """
    try:
        from lebai_sdk import connect

        if port is not None:
            robot = connect(host, port)
        else:
            robot = connect(host)
        time.sleep(0.5)

        if robot.is_connected():
            _set_robot(robot_id, robot)
            return {
                "success": True,
                "message": f"Connected to robot at {host}",
                "robot_info": {
                    "host": host,
                    "port": port,
                    "connected": True,
                    "robot_id": robot_id
                }
            }
        return {
            "success": False,
            "message": f"Failed to connect to robot at {host}",
            "robot_info": {"host": host, "port": port, "connected": False}
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to connect: {str(e)}", "error": str(e)}


def disconnect_robot(robot_id: str = "default") -> Dict[str, Any]:
    """Disconnect from a Lebai robot."""
    try:
        robot = _get_robot(robot_id)
        if robot:
            del _robot_registry[robot_id]
        return {"success": True, "message": f"Disconnected from robot {robot_id}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to disconnect: {str(e)}", "error": str(e)}


def is_connected(robot_id: str = "default") -> Dict[str, Any]:
    """Check if robot is connected."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "connected": False, "message": "Robot not connected"}
        return {"success": True, "connected": robot.is_connected()}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def wait_disconnect(robot_id: str = "default") -> Dict[str, Any]:
    """Wait for robot disconnection."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.wait_disconnect()
        return {"success": True, "message": "Wait disconnect completed", "result": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Motion Control - Basic
# ============================================================================

def towardj(p: List[float], a: float, v: float,
            t: float = None, r: float = None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move to joint position (joint interpolation).

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        a: Joint acceleration in rad/s²
        v: Joint velocity in rad/s
        t: Timeout (optional)
        r: Blend radius (optional)
        robot_id: Robot identifier

    Returns:
        Motion execution status
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected", "error": "Not connected"}

        result = robot.towardj(p, a, v, t, r)
        return {"success": True, "message": "Move command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def movej(p: List[float], a: float, v: float,
          t: float = None, r: float = None, robot_id: str = "default") -> Dict[str, Any]:
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
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected", "error": "Not connected"}

        result = robot.movej(p, a, v, t, r)
        return {"success": True, "message": "Move command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def movel(p: Dict[str, float], a: float, v: float,
          t: float = None, r: float = None, robot_id: str = "default") -> Dict[str, Any]:
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
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected", "error": "Not connected"}

        result = robot.movel(p, a, v, t, r)
        return {"success": True, "message": "Move command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def movec(via: Dict[str, float], p: Dict[str, float],
          rad: float, a: float, v: float, t: float = None, r: float = None,
          robot_id: str = "default") -> Dict[str, Any]:
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
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected", "error": "Not connected"}

        result = robot.movec(via, p, rad, a, v, t, r)
        return {"success": True, "message": "Move command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Motion Control - Advanced
# ============================================================================

def move_pt(p: List[float], t: float, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move through points with time.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        t: Time
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.move_pt(p, t)
        return {"success": True, "message": "Move pt command sent"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def move_pvt(p: List[float], v: List[float], t: float, robot_id: str = "default") -> Dict[str, Any]:
    """
    Move with position, velocity, time.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        v: Joint velocity - [j1, j2, j3, j4, j5, j6] array in rad/s
        t: Time
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.move_pvt(p, v, t)
        return {"success": True, "message": "Move pvt command sent"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def move_pvat(p: List[float], v: List[float], a: List[float], t: float,
              robot_id: str = "default") -> Dict[str, Any]:
    """
    Move with position, velocity, acceleration, time.

    Args:
        p: Target joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        v: Joint velocity - [j1, j2, j3, j4, j5, j6] array in rad/s
        a: Joint acceleration - [j1, j2, j3, j4, j5, j6] array in rad/s²
        t: Time
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.move_pvat(p, v, a, t)
        return {"success": True, "message": "Move pvat command sent"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def speedj(a: float, v: List[float], t: float = None, robot_id: str = "default") -> Dict[str, Any]:
    """
    Joint velocity control.

    Args:
        a: Joint acceleration in rad/s²
        v: Joint velocity - [j1, j2, j3, j4, j5, j6] array in rad/s
        t: Timeout (optional)
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.speedj(a, v, t)
        return {"success": True, "message": "Speedj command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def speedl(a: float, v: Dict[str, float], t: float = None, frame: Dict[str, float] = None,
           robot_id: str = "default") -> Dict[str, Any]:
    """
    Cartesian velocity control.

    Args:
        a: Cartesian acceleration in m/s²
        v: Cartesian velocity - {x, y, z, rx, ry, rz} dict (m/s, rad/s)
        t: Timeout (optional)
        frame: Reference frame (optional)
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.speedl(a, v, t, frame)
        return {"success": True, "message": "Speedl command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def move_trajectory(name: str, dir: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Execute a saved trajectory."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.move_trajectory(name, dir)
        return {"success": True, "message": "Trajectory command sent", "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Motion Control - Status
# ============================================================================

def wait_move(id: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Wait for motion to complete."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.wait_move(id)
        return {"success": True, "message": "Motion completed"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def pause_move(robot_id: str = "default") -> Dict[str, Any]:
    """Pause current motion."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.pause_move()
        return {"success": True, "message": "Motion paused"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def resume_move(robot_id: str = "default") -> Dict[str, Any]:
    """Resume paused motion."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.resume_move()
        return {"success": True, "message": "Motion resumed"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def stop_move(robot_id: str = "default") -> Dict[str, Any]:
    """Stop current motion."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.stop_move()
        return {"success": True, "message": "Motion stopped"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_running_motion(robot_id: str = "default") -> Dict[str, Any]:
    """Get running motion ID."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_running_motion()
        return {"success": True, "id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_motion_state(id: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get motion state by ID."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_motion_state(id)
        return {"success": True, "state": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def can_move(robot_state, robot_id: str = "default") -> Dict[str, Any]:
    """Check if robot can move."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.can_move(robot_state)
        return {"success": True, "can_move": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# System Control
# ============================================================================

def estop(robot_id: str = "default") -> Dict[str, Any]:
    """Emergency stop."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.estop()
        return {"success": True, "message": "Emergency stop executed"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_estop_reason(robot_id: str = "default") -> Dict[str, Any]:
    """Get emergency stop reason."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_estop_reason()
        return {"success": True, "reason": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def start_sys(robot_id: str = "default") -> Dict[str, Any]:
    """Start system."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.start_sys()
        return {"success": True, "message": "System started"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def stop_sys(robot_id: str = "default") -> Dict[str, Any]:
    """Stop system."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.stop_sys()
        return {"success": True, "message": "System stopped"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def reboot(robot_id: str = "default") -> Dict[str, Any]:
    """Reboot robot controller."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.reboot()
        return {"success": True, "message": "Reboot command sent"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def powerdown(robot_id: str = "default") -> Dict[str, Any]:
    """Power down robot."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.powerdown()
        return {"success": True, "message": "Powerdown command sent"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def find_zero(robot_id: str = "default") -> Dict[str, Any]:
    """Find zero position (homing)."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.find_zero()
        return {"success": True, "message": "Homing started"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Teaching Mode
# ============================================================================

def teach_mode(robot_id: str = "default") -> Dict[str, Any]:
    """Enter teaching mode."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.teach_mode()
        return {"success": True, "message": "Teaching mode enabled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def end_teach_mode(robot_id: str = "default") -> Dict[str, Any]:
    """Exit teaching mode."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.end_teach_mode()
        return {"success": True, "message": "Teaching mode disabled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Status and Data
# ============================================================================

def get_robot_state(robot_id: str = "default") -> Dict[str, Any]:
    """Get robot state (IDLE, RUNNING, ESTOP, etc.)."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_robot_state()
        return {"success": True, "status": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_tcp(robot_id: str = "default") -> Dict[str, Any]:
    """
    Get TCP offset relative to the flange end.
    
    Returns the configured TCP tool center point offset from the flange.
    This is NOT the TCP position in base frame.
    For TCP position relative to base frame, use get_current_position().
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_tcp()
        return {"success": True, "tcp": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


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
            return {"success": False, "message": "Robot not connected"}

        kin_data = robot.get_kin_data()
        if isinstance(kin_data, dict) and 'actual_tcp_pose' in kin_data:
            tcp = kin_data['actual_tcp_pose']
            return {
                "success": True,
                "position": {
                    "x": tcp.get('x', 0),
                    "y": tcp.get('y', 0),
                    "z": tcp.get('z', 0),
                    "rx": tcp.get('rx', 0),
                    "ry": tcp.get('ry', 0),
                    "rz": tcp.get('rz', 0)
                }
            }
        return {"success": False, "message": "Unable to parse TCP data"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_current_joints(robot_id: str = "default") -> Dict[str, Any]:
    """
    Get current joint angles in radians.
    
    Returns:
        joints: [j1, j2, j3, j4, j5, j6] array in radians
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}

        kin_data = robot.get_kin_data()
        if isinstance(kin_data, dict) and 'actual_joint_pose' in kin_data:
            joints = kin_data['actual_joint_pose']
            return {
                "success": True,
                "joints": list(joints)
            }
        return {"success": False, "message": "Unable to parse joint data"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_kin_data(robot_id: str = "default") -> Dict[str, Any]:
    """Get kinematic data."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_kin_data()
        return {"success": True, "kin_data": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_phy_data(robot_id: str = "default") -> Dict[str, Any]:
    """Get physical data (joint temp, voltage, etc.)."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_phy_data()
        return {"success": True, "phy_data": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_payload(robot_id: str = "default") -> Dict[str, Any]:
    """Get payload configuration."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_payload()
        return {"success": True, "payload": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_gravity(robot_id: str = "default") -> Dict[str, Any]:
    """Get gravity center configuration."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_gravity()
        return {"success": True, "gravity": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_velocity_factor(robot_id: str = "default") -> Dict[str, Any]:
    """Get velocity factor."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_velocity_factor()
        return {"success": True, "velocity_factor": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Configuration
# ============================================================================

def set_payload(mass: float = None, cog: List[float] = None, 
                robot_id: str = "default") -> Dict[str, Any]:
    """Set payload configuration."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_payload(mass=mass, cog=cog)
        return {"success": True, "message": "Payload configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_gravity(pose: Dict[str, float],
                robot_id: str = "default") -> Dict[str, Any]:
    """
    Set gravity center.
    
    Args:
        pose: Gravity center - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_gravity(pose)
        return {"success": True, "message": "Gravity center configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_tcp(pose: Dict[str, float],
            robot_id: str = "default") -> Dict[str, Any]:
    """
    Set TCP offset.
    
    Args:
        pose: TCP offset - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_tcp(pose)
        return {"success": True, "message": "TCP configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_velocity_factor(speed_factor: int, robot_id: str = "default") -> Dict[str, Any]:
    """Set global velocity factor."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_velocity_factor(speed_factor)
        return {"success": True, "message": "Velocity factor set"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def enable_joint_limits(robot_id: str = "default") -> Dict[str, Any]:
    """Enable joint limits."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.enable_joint_limits()
        return {"success": True, "message": "Joint limits enabled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def disable_joint_limits(robot_id: str = "default") -> Dict[str, Any]:
    """Disable joint limits."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.disable_joint_limits()
        return {"success": True, "message": "Joint limits disabled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def enable_collision_detector(robot_id: str = "default") -> Dict[str, Any]:
    """Enable collision detector."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.enable_collision_detector()
        return {"success": True, "message": "Collision detector enabled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def disable_collision_detector(robot_id: str = "default") -> Dict[str, Any]:
    """Disable collision detector."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.disable_collision_detector()
        return {"success": True, "message": "Collision detector disabled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_collision_detector_sensitivity(sensitivity: float, 
                                       robot_id: str = "default") -> Dict[str, Any]:
    """Set collision detector sensitivity."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_collision_detector_sensitivity(sensitivity)
        return {"success": True, "message": "Sensitivity configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Gripper Control
# ============================================================================

def init_gripper(force: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Initialize gripper."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.init_claw(force=force)
        return {"success": True, "message": "Gripper initialized"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_gripper(robot_id: str = "default") -> Dict[str, Any]:
    """Get gripper status."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_claw()
        return {"success": True, "gripper": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def control_gripper(action: str = "open", force: int = None, amplitude: int = None,
                    robot_id: str = "default") -> Dict[str, Any]:
    """
    Control gripper.

    Args:
        action: "open", "close", or "set"
        force: Gripper force (0-100)
        amplitude: Gripper amplitude
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        
        if action == "open":
            robot.set_claw(0)
        elif action == "close":
            robot.set_claw(100)
        elif action == "set":
            robot.set_claw(force=force, amplitude=amplitude)
        else:
            return {"success": False, "message": "Invalid action. Use 'open', 'close', or 'set'"}
        
        return {"success": True, "message": f"Gripper action '{action}' executed"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Pose Operations
# ============================================================================

def save_pose(name: str, pose: Dict[str, float] = None,
              dir: str = None, refer: List[float] = None,
              robot_id: str = "default") -> Dict[str, Any]:
    """
    Save pose to file.
    
    Args:
        name: Pose name
        pose: TCP pose - {x, y, z, rx, ry, rz} dict in meters and radians
        dir: Directory (optional)
        refer: Reference joint angles (optional)
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.save_pose(name, pose, dir, refer)
        return {"success": True, "message": f"Pose '{name}' saved"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def load_pose(name: str, dir: str = None, raw_pose: bool = None,
              robot_id: str = "default") -> Dict[str, Any]:
    """Load pose from file."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.load_pose(name, dir, raw_pose)
        return {"success": True, "pose": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def load_tcp(name: str, dir: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Load TCP configuration from file."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.load_tcp(name, dir)
        return {"success": True, "tcp": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def load_frame(name: str, dir: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Load frame from file."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.load_frame(name, dir)
        return {"success": True, "frame": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def load_led_style(name: str, dir: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Load LED style from file."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.load_led_style(name, dir)
        return {"success": True, "led_style": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def load_payload(name: str, dir: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Load payload configuration from file."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.load_payload(name, dir)
        return {"success": True, "payload": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def pose_inverse(p: Dict[str, float],
                 robot_id: str = "default") -> Dict[str, Any]:
    """
    Calculate inverse pose.
    
    Args:
        p: Pose - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.pose_inverse(p)
        return {"success": True, "inverse_pose": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def pose_add(pose: Dict[str, float],
             delta: Dict[str, float], frame: Dict[str, float] = None,
             robot_id: str = "default") -> Dict[str, Any]:
    """
    Add delta to pose.
    
    Args:
        pose: Base pose - {x, y, z, rx, ry, rz} dict in meters and radians
        delta: Delta pose - {x, y, z, rx, ry, rz} dict in meters and radians
        frame: Reference frame (optional)
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.pose_add(pose, delta, frame)
        return {"success": True, "result_pose": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def kinematics_forward(p: List[float],
                       robot_id: str = "default") -> Dict[str, Any]:
    """
    Forward kinematics.
    
    Args:
        p: Joint angles - [j1, j2, j3, j4, j5, j6] array in radians
        robot_id: Robot identifier
    
    Returns:
        TCP pose as {x, y, z, rx, ry, rz} dict
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.kinematics_forward(p)
        return {"success": True, "tcp_pose": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def kinematics_inverse(p: Dict[str, float],
                       refer: List[float] = None,
                       robot_id: str = "default") -> Dict[str, Any]:
    """
    Inverse kinematics.
    
    Args:
        p: TCP pose - {x, y, z, rx, ry, rz} dict in meters and radians
        refer: Reference joint angles (optional)
        robot_id: Robot identifier
    
    Returns:
        Joint angles as [j1, j2, j3, j4, j5, j6] array
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.kinematics_inverse(p, refer)
        return {"success": True, "joint_angles": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def in_pose(p: Dict[str, float],
            robot_id: str = "default") -> Dict[str, Any]:
    """
    Check if current pose is close to target.
    
    Args:
        p: Target pose - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.in_pose(p)
        return {"success": True, "in_pose": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def measure_manipulation(p: Dict[str, float], robot_id: str = "default") -> Dict[str, Any]:
    """
    Measure manipulation.
    
    Args:
        p: TCP pose - {x, y, z, rx, ry, rz} dict in meters and radians
        robot_id: Robot identifier
    """
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.measure_manipulation(p)
        return {"success": True, "measurement": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Task Management
# ============================================================================

def start_task(scene: str, params: Dict = None, dir: str = None,
               is_parallel: bool = None, loop_to: str = None,
               robot_id: str = "default") -> Dict[str, Any]:
    """Start a task."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.start_task(scene, params, dir, is_parallel, loop_to)
        return {"success": True, "task_id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_task_list(robot_id: str = "default") -> Dict[str, Any]:
    """Get task list."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_task_list()
        return {"success": True, "tasks": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_main_task_id(robot_id: str = "default") -> Dict[str, Any]:
    """Get main task ID."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_main_task_id()
        return {"success": True, "main_task_id": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_task_state(id: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Get task state."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_task_state(id)
        return {"success": True, "state": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def pause_task(id: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Pause task."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.pause_task(id)
        return {"success": True, "message": "Task paused"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def resume_task(id: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Resume task."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.resume_task(id)
        return {"success": True, "message": "Task resumed"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def cancel_task(id: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Cancel task."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.cancel_task(id)
        return {"success": True, "message": "Task cancelled"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def wait_task(id: int = None, robot_id: str = "default") -> Dict[str, Any]:
    """Wait for task completion."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.wait_task(id)
        return {"success": True, "message": "Task completed"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Digital I/O
# ============================================================================

def set_dio_mode(device: str, pin: int, mode: str, 
                 robot_id: str = "default") -> Dict[str, Any]:
    """Set digital I/O mode."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_dio_mode(device, pin, mode)
        return {"success": True, "message": "DIO mode configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_dio_mode(device: str, pin: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get digital I/O mode."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_dio_mode(device, pin)
        return {"success": True, "mode": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_do(device: str, pin: int, value: int, robot_id: str = "default") -> Dict[str, Any]:
    """Set digital output."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_do(device, pin, value)
        return {"success": True, "message": f"DO {device}:{pin} = {value}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_do(device: str, pin: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get digital output."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_do(device, pin)
        return {"success": True, "value": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_dos(device: str, pin: int, num: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple digital outputs."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_dos(device, pin, num)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_di(device: str, pin: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get digital input."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_di(device, pin)
        return {"success": True, "value": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_dis(device: str, pin: int, num: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple digital inputs."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_dis(device, pin, num)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Analog I/O
# ============================================================================

def set_ao(device: str, pin: int, value: float, robot_id: str = "default") -> Dict[str, Any]:
    """Set analog output."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_ao(device, pin, value)
        return {"success": True, "message": f"AO {device}:{pin} = {value}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_ao(device: str, pin: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get analog output."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_ao(device, pin)
        return {"success": True, "value": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_aos(device: str, pin: int, num: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple analog outputs."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_aos(device, pin, num)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_ai(device: str, pin: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get analog input."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_ai(device, pin)
        return {"success": True, "value": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_ais(device: str, pin: int, num: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple analog inputs."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_ais(device, pin, num)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Signals
# ============================================================================

def set_signal(index: int, value: int, robot_id: str = "default") -> Dict[str, Any]:
    """Set signal."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_signal(index, value)
        return {"success": True, "message": f"Signal {index} = {value}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def add_signal(index: int, value: int, robot_id: str = "default") -> Dict[str, Any]:
    """Add signal."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.add_signal(index, value)
        return {"success": True, "message": f"Signal {index} added"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_signal(index: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get signal."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_signal(index)
        return {"success": True, "value": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_signals(index: int, length: int, robot_id: str = "default") -> Dict[str, Any]:
    """Get multiple signals."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_signals(index, length)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_signals(index: int, values: List[int], robot_id: str = "default") -> Dict[str, Any]:
    """Set multiple signals."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_signals(index, values)
        return {"success": True, "message": f"Signals set from index {index}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Serial Communication
# ============================================================================

def set_serial_baud_rate(device: str, baud_rate: int, 
                         robot_id: str = "default") -> Dict[str, Any]:
    """Set serial baud rate."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_serial_baud_rate(device, baud_rate)
        return {"success": True, "message": f"Serial {device} baud rate set to {baud_rate}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_serial_timeout(device: str, timeout: float, 
                       robot_id: str = "default") -> Dict[str, Any]:
    """Set serial timeout."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_serial_timeout(device, timeout)
        return {"success": True, "message": f"Serial {device} timeout set to {timeout}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_serial_parity(device: str, parity: str, robot_id: str = "default") -> Dict[str, Any]:
    """Set serial parity."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_serial_parity(device, parity)
        return {"success": True, "message": f"Serial {device} parity set to {parity}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_flange_baud_rate(baud_rate: int, robot_id: str = "default") -> Dict[str, Any]:
    """Set flange baud rate."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_flange_baud_rate(baud_rate)
        return {"success": True, "message": f"Flange baud rate set to {baud_rate}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def write_serial(device: str, data: str, robot_id: str = "default") -> Dict[str, Any]:
    """Write to serial port."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.write_serial(device, data)
        return {"success": True, "message": f"Data written to {device}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def read_serial(device: str, length: int, robot_id: str = "default") -> Dict[str, Any]:
    """Read from serial port."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.read_serial(device, length)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def clear_serial(device: str, robot_id: str = "default") -> Dict[str, Any]:
    """Clear serial buffer."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.clear_serial(device)
        return {"success": True, "message": f"Serial {device} buffer cleared"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Modbus
# ============================================================================

def read_coils(device: str, pin: int, count: int, robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus coils."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.read_coils(device, pin, count)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def read_discrete_inputs(device: str, pin: int, count: int, 
                         robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus discrete inputs."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.read_discrete_inputs(device, pin, count)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def read_holding_registers(device: str, pin: int, count: int, 
                           robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus holding registers."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.read_holding_registers(device, pin, count)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def read_input_registers(device: str, pin: int, count: int, 
                         robot_id: str = "default") -> Dict[str, Any]:
    """Read Modbus input registers."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.read_input_registers(device, pin, count)
        return {"success": True, "values": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def write_single_coil(device: str, pin: int, value: int, 
                      robot_id: str = "default") -> Dict[str, Any]:
    """Write single Modbus coil."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.write_single_coil(device, pin, value)
        return {"success": True, "message": f"Coil {device}:{pin} = {value}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def write_single_register(device: str, pin: int, value: int, 
                          robot_id: str = "default") -> Dict[str, Any]:
    """Write single Modbus register."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.write_single_register(device, pin, value)
        return {"success": True, "message": f"Register {device}:{pin} = {value}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def write_multiple_coils(device: str, pin: int, values: List[int], 
                         robot_id: str = "default") -> Dict[str, Any]:
    """Write multiple Modbus coils."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.write_multiple_coils(device, pin, values)
        return {"success": True, "message": f"Multiple coils written to {device}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def write_multiple_registers(device: str, pin: int, values: List[int], 
                             robot_id: str = "default") -> Dict[str, Any]:
    """Write multiple Modbus registers."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.write_multiple_registers(device, pin, values)
        return {"success": True, "message": f"Multiple registers written to {device}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_modbus_timeout(device: str, timeout: float, 
                       robot_id: str = "default") -> Dict[str, Any]:
    """Set Modbus timeout."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_modbus_timeout(device, timeout)
        return {"success": True, "message": f"Modbus {device} timeout set to {timeout}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_modbus_retry(device: str, retry: int, robot_id: str = "default") -> Dict[str, Any]:
    """Set Modbus retry count."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_modbus_retry(device, retry)
        return {"success": True, "message": f"Modbus {device} retry set to {retry}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def disconnect_modbus(device: str, robot_id: str = "default") -> Dict[str, Any]:
    """Disconnect Modbus."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.disconnect_modbus(device)
        return {"success": True, "message": f"Modbus {device} disconnected"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# LED Control
# ============================================================================

def set_led(mode: str, speed: int, colors: List, robot_id: str = "default") -> Dict[str, Any]:
    """Set LED."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_led(mode, speed, colors)
        return {"success": True, "message": "LED configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_led_style(style: str, robot_id: str = "default") -> Dict[str, Any]:
    """Set LED style."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_led_style(style)
        return {"success": True, "message": f"LED style set to {style}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_fan(mode: str, robot_id: str = "default") -> Dict[str, Any]:
    """Set fan mode."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_fan(mode)
        return {"success": True, "message": f"Fan mode set to {mode}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def set_voice(voice: str, volume: int, robot_id: str = "default") -> Dict[str, Any]:
    """Set voice."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_voice(voice, volume)
        return {"success": True, "message": "Voice configured"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Items (Key-Value Storage)
# ============================================================================

def set_item(key: str, value: Any, robot_id: str = "default") -> Dict[str, Any]:
    """Set item."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        robot.set_item(key, value)
        return {"success": True, "message": f"Item '{key}' set"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_item(key: str, robot_id: str = "default") -> Dict[str, Any]:
    """Get item."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_item(key)
        return {"success": True, "item": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def get_items(prefix: str, robot_id: str = "default") -> Dict[str, Any]:
    """Get items by prefix."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.get_items(prefix)
        return {"success": True, "items": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Plugin and Advanced Features
# ============================================================================

def run_plugin_cmd(name: str, params: Dict = None, robot_id: str = "default") -> Dict[str, Any]:
    """Run plugin command."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.run_plugin_cmd(name, params)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def call(method: str, param: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Call arbitrary robot method."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.call(method, param)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


def subscribe(method: str, param: str = None, robot_id: str = "default") -> Dict[str, Any]:
    """Subscribe to robot data."""
    try:
        robot = _get_robot(robot_id)
        if not robot:
            return {"success": False, "message": "Robot not connected"}
        result = robot.subscribe(method, param)
        return {"success": True, "subscription": result}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}


# ============================================================================
# Main entry point for CLI execution
# ============================================================================

if __name__ == "__main__":
    print(json.dumps({
        "message": "Lebai Robot Control Skill - Complete API",
        "description": "Comprehensive control over Lebai robotic arms",
        "categories": {
            "connection": ["connect_robot", "disconnect_robot", "is_connected", "wait_disconnect"],
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
