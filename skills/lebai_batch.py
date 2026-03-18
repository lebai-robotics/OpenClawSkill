#!/usr/bin/env python3
"""
Lebai Robot Batch Operations Skill

Provides batch operations for Lebai robotic arms including:
- Multi-point motion sequences
- Calibration routines
- Automated pick and place
- Status monitoring loops

Note: Uses lebai_sdk (https://github.com/lebai-robotics/lebai-sdk)
All functions are synchronous - no asyncio required.
"""

import json
import time
from typing import List, Dict, Any, Optional


def execute_motion_sequence(
    robot_id: str = "default",
    positions: List[Dict[str, float]] = None,
    speed: int = 50,
    wait_between: float = 0.5
) -> Dict[str, Any]:
    """
    Execute a sequence of motion positions.

    Args:
        robot_id: Robot identifier
        positions: List of position dictionaries with keys:
                   x, y, z, rx, ry, rz
        speed: Movement speed (0-100)
        wait_between: Wait time between motions in seconds

    Returns:
        Sequence execution status with results for each position
    """
    if positions is None:
        positions = []

    results = []

    try:
        from skills.lebai_robot import _get_robot

        robot = _get_robot(robot_id)
        if not robot:
            return {
                "success": False,
                "message": "Robot not connected. Call connect_robot first.",
                "error": "Not connected"
            }

        a = speed * 0.5
        v = speed * 0.5

        for i, pos in enumerate(positions):
            try:
                pose = [
                    pos.get('x', 0),
                    pos.get('y', 0),
                    pos.get('z', 0),
                    pos.get('rx', 0),
                    pos.get('ry', 0),
                    pos.get('rz', 0)
                ]

                robot.towardj(pose, a, v)
                robot.wait_move()

                results.append({
                    "step": i + 1,
                    "success": True,
                    "position": pos
                })

                if wait_between > 0 and i < len(positions) - 1:
                    time.sleep(wait_between)

            except Exception as e:
                results.append({
                    "step": i + 1,
                    "success": False,
                    "error": str(e),
                    "position": pos
                })
                break

        return {
            "success": all(r.get("success", False) for r in results),
            "completed_steps": len([r for r in results if r.get("success")]),
            "total_steps": len(positions),
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to execute sequence: {str(e)}",
            "error": str(e),
            "results": results
        }


def pick_and_place(
    robot_id: str = "default",
    pick_position: Dict[str, float] = None,
    place_position: Dict[str, float] = None,
    approach_height: float = 50.0,
    speed: int = 50
) -> Dict[str, Any]:
    """
    Execute a pick and place operation.

    Args:
        robot_id: Robot identifier
        pick_position: Position to pick from (x, y, z, rx, ry, rz) in meters
        place_position: Position to place to (x, y, z, rx, ry, rz) in meters
        approach_height: Height to approach before picking/placing in meters
        speed: Movement speed (0-100)

    Returns:
        Operation status
    """
    import math

    if pick_position is None:
        pick_position = {"x": 0.2, "y": 0, "z": 0.1, "rx": math.pi, "ry": 0, "rz": 0}
    if place_position is None:
        place_position = {"x": 0.2, "y": 0.1, "z": 0.1, "rx": math.pi, "ry": 0, "rz": 0}

    try:
        from skills.lebai_robot import _get_robot

        robot = _get_robot(robot_id)
        if not robot:
            return {
                "success": False,
                "message": "Robot not connected. Call connect_robot first.",
                "error": "Not connected"
            }

        a = speed * 0.5
        v = speed * 0.5

        def move_to(pose_list):
            robot.towardj(pose_list, a, v)
            robot.wait_move()

        # Step 1: Move to approach position above pick
        pick_approach = [
            pick_position['x'],
            pick_position['y'],
            pick_position['z'] + approach_height,
            pick_position['rx'],
            pick_position['ry'],
            pick_position['rz']
        ]
        move_to(pick_approach)

        # Step 2: Move to pick position
        pick_pose = [
            pick_position['x'],
            pick_position['y'],
            pick_position['z'],
            pick_position['rx'],
            pick_position['ry'],
            pick_position['rz']
        ]
        move_to(pick_pose)

        # Step 3: Close gripper
        robot.set_claw(100)
        time.sleep(0.5)

        # Step 4: Move to approach position
        move_to(pick_approach)

        # Step 5: Move to place approach position
        place_approach = [
            place_position['x'],
            place_position['y'],
            place_position['z'] + approach_height,
            place_position['rx'],
            place_position['ry'],
            place_position['rz']
        ]
        move_to(place_approach)

        # Step 6: Move to place position
        place_pose = [
            place_position['x'],
            place_position['y'],
            place_position['z'],
            place_position['rx'],
            place_position['ry'],
            place_position['rz']
        ]
        move_to(place_pose)

        # Step 7: Open gripper
        robot.set_claw(0)
        time.sleep(0.5)

        # Step 8: Move to approach position
        move_to(place_approach)

        return {
            "success": True,
            "message": "Pick and place completed successfully",
            "pick_position": pick_position,
            "place_position": place_position
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Pick and place failed: {str(e)}",
            "error": str(e)
        }


def calibration_routine(
    robot_id: str = "default",
    home_position: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Execute a calibration/home routine.

    Args:
        robot_id: Robot identifier
        home_position: Home position for calibration (default: straight up) in meters

    Returns:
        Calibration status
    """
    import math

    if home_position is None:
        home_position = {"x": 0, "y": 0, "z": 0.3, "rx": math.pi, "ry": 0, "rz": 0}

    try:
        from skills.lebai_robot import _get_robot

        robot = _get_robot(robot_id)
        if not robot:
            return {
                "success": False,
                "message": "Robot not connected. Call connect_robot first.",
                "error": "Not connected"
            }

        home_pose = [
            home_position['x'],
            home_position['y'],
            home_position['z'],
            home_position['rx'],
            home_position['ry'],
            home_position['rz']
        ]

        robot.towardj(home_pose, 30, 30)
        robot.wait_move()

        # Get current position to verify
        current_pose = robot.get_tcp()

        return {
            "success": True,
            "message": "Calibration routine completed",
            "home_position": home_position,
            "actual_position": {
                "x": current_pose[0], "y": current_pose[1], "z": current_pose[2],
                "rx": current_pose[3], "ry": current_pose[4], "rz": current_pose[5]
            } if isinstance(current_pose, (list, tuple)) else current_pose
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Calibration failed: {str(e)}",
            "error": str(e)
        }


def monitor_status_loop(
    robot_id: str = "default",
    interval: float = 1.0,
    duration: float = 10.0
) -> Dict[str, Any]:
    """
    Monitor robot status for a specified duration.

    Args:
        robot_id: Robot identifier
        interval: Status check interval in seconds
        duration: Total monitoring duration in seconds

    Returns:
        Monitoring results with status history
    """
    try:
        from skills.lebai_robot import _get_robot

        robot = _get_robot(robot_id)
        if not robot:
            return {
                "success": False,
                "message": "Robot not connected. Call connect_robot first.",
                "error": "Not connected"
            }

        status_history = []
        start_time = time.time()

        while (time.time() - start_time) < duration:
            try:
                status = robot.get_robot_state()
                status_history.append({
                    "timestamp": time.time() - start_time,
                    "status": status
                })
            except Exception as e:
                status_history.append({
                    "timestamp": time.time() - start_time,
                    "error": str(e)
                })

            time.sleep(interval)

        return {
            "success": True,
            "message": f"Monitoring completed for {duration} seconds",
            "samples": len(status_history),
            "history": status_history
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Monitoring failed: {str(e)}",
            "error": str(e)
        }


def waypoint_navigation(
    robot_id: str = "default",
    waypoints: List[Dict[str, float]] = None,
    speeds: List[int] = None
) -> Dict[str, Any]:
    """
    Navigate through multiple waypoints with different speeds.

    Args:
        robot_id: Robot identifier
        waypoints: List of waypoint positions
        speeds: List of speeds for each waypoint (default: all 50)

    Returns:
        Navigation status
    """
    if waypoints is None:
        waypoints = []
    if speeds is None:
        speeds = [50] * len(waypoints)

    results = []

    try:
        from skills.lebai_robot import _get_robot

        robot = _get_robot(robot_id)
        if not robot:
            return {
                "success": False,
                "message": "Robot not connected. Call connect_robot first.",
                "error": "Not connected"
            }

        for i, (waypoint, speed) in enumerate(zip(waypoints, speeds)):
            try:
                pose = [
                    waypoint.get('x', 0),
                    waypoint.get('y', 0),
                    waypoint.get('z', 0),
                    waypoint.get('rx', 0),
                    waypoint.get('ry', 0),
                    waypoint.get('rz', 0)
                ]

                a = min(speed, 100) * 0.5
                v = min(speed, 100) * 0.5

                robot.towardj(pose, a, v)
                robot.wait_move()

                results.append({
                    "waypoint": i + 1,
                    "success": True,
                    "position": waypoint
                })
            except Exception as e:
                results.append({
                    "waypoint": i + 1,
                    "success": False,
                    "error": str(e),
                    "position": waypoint
                })
                break

        return {
            "success": all(r.get("success", False) for r in results),
            "completed_waypoints": len([r for r in results if r.get("success")]),
            "total_waypoints": len(waypoints),
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Waypoint navigation failed: {str(e)}",
            "error": str(e),
            "results": results
        }


# Main entry point for CLI execution
if __name__ == "__main__":
    import sys

    print(json.dumps({
        "message": "Lebai Robot Batch Operations Skill",
        "available_operations": [
            "execute_motion_sequence",
            "pick_and_place",
            "calibration_routine",
            "monitor_status_loop",
            "waypoint_navigation"
        ],
        "usage": "Import and call functions directly"
    }, indent=2))
