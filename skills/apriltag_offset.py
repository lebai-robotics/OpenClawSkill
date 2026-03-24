"""
AprilTag Offset Teaching Skill for Lebai Robot

Guides users to teach the grasping position relative to an AprilTag marker.

Workflow:
1. Move to tag front (20cm -> 10cm -> 7cm for optimal camera view)
2. Detect and record tag pose
3. Enter teach mode for user to manually guide to grasp position
4. Wait for shoulder button confirmation
5. Calculate and return offset from tag to grasp pose
"""

import time
from typing import Dict, Any, Optional, List
from functools import wraps

# Import from existing modules
from .lebai_robot import (
    _get_robot, _success, _error, _robot_required,
    teach_mode, end_teach_mode, get_current_position, movej, movel,
    wait_move, control_gripper, get_di
)
from .apriltag import find_tags, get_tag_pose


def _pose_to_list(pose: Dict[str, float]) -> List[float]:
    """Convert pose dict to list [x, y, z, rx, ry, rz]."""
    return [pose['x'], pose['y'], pose['z'], pose['rx'], pose['ry'], pose['rz']]


def _list_to_pose(pose_list: List[float]) -> Dict[str, float]:
    """Convert list [x, y, z, rx, ry, rz] to pose dict."""
    return {
        'x': pose_list[0], 'y': pose_list[1], 'z': pose_list[2],
        'rx': pose_list[3], 'ry': pose_list[4], 'rz': pose_list[5]
    }


def _pose_multiply(pose: Dict[str, float], delta: List[float]) -> Dict[str, float]:
    """
    Multiply pose by delta (simple translation addition).
    For more complex pose operations, use robot's pose_trans.
    """
    return {
        'x': pose['x'] + delta[0],
        'y': pose['y'] + delta[1],
        'z': pose['z'] + delta[2],
        'rx': pose['rx'] + delta[3],
        'ry': pose['ry'] + delta[4],
        'rz': pose['rz'] + delta[5]
    }


@_robot_required
def teach_grasp_offset(
    tag_id: int,
    way: str = "signal",
    signal_id: int = 13,
    open_gripper: bool = True,
    robot=None,
    robot_id: str = "default",
    camera_id: str = "default"
) -> Dict[str, Any]:
    """
    Guide user to teach grasp position relative to AprilTag.

    Complete workflow:
    1. Open gripper (optional)
    2. Move to tag front 10cm for initial approach
    3. Move to tag front 7cm for optimal camera view
    4. Detect and record tag pose
    5. Enter teach mode - user manually guides robot to grasp position
    6. Wait for shoulder button (DI SHOULDER:0) press
    7. Calculate offset from tag to grasp pose

    Args:
        tag_id: AprilTag ID to detect
        way: Communication method - "signal" or "modbus"
        signal_id: Signal index for detection
        open_gripper: Whether to open gripper before teaching
        robot_id: Robot identifier
        camera_id: Camera identifier

    Returns:
        Success response with offset data:
        {
            "tag_id": int,
            "tag_pose": {x, y, z, rx, ry, rz},
            "grasp_pose": {x, y, z, rx, ry, rz},
            "offset": {x, y, z, rx, ry, rz}
        }

    Example:
        >>> result = teach_grasp_offset(tag_id=13, way="signal")
        >>> if result["success"]:
        ...     offset = result["data"]["offset"]
        ...     print(f"Offset: {offset}")
    """
    try:
        # Step 0: Open gripper if requested
        if open_gripper:
            control_gripper(amplitude=100)
            time.sleep(0.5)

        # Step 1: Approach tag - move to 10cm in front
        result = _approach_tag(tag_id, way, signal_id, 0.1, robot, robot_id, camera_id)
        if not result["success"]:
            return result

        # Step 2: Move to optimal camera view - 7cm in front
        result = _approach_tag(tag_id, way, signal_id, 0.07, robot, robot_id, camera_id)
        if not result["success"]:
            return result

        # Step 3: Final detection and record tag pose
        result = get_tag_pose(tag_id, way, signal_id, 30.0, robot_id, camera_id)
        if not result["success"]:
            return result

        tag_pose = result["data"]["pose"]
        print(f"Tag {tag_id} detected at: {tag_pose}")

        # Step 4: Enter teach mode
        print("Entering teach mode - please guide robot to grasp position...")
        teach_result = teach_mode(robot_id)
        if not teach_result["success"]:
            return _error(f"Failed to enter teach mode: {teach_result.get('message')}")

        # Step 5: Wait for shoulder button confirmation
        print("Press SHOULDER button (DI:0) to confirm grasp position...")
        _wait_for_shoulder_button(robot)

        # Exit teach mode
        end_teach_mode(robot_id)

        # Step 6: Record grasp pose
        grasp_result = get_current_position(robot_id)
        if not grasp_result["success"]:
            return _error(f"Failed to get grasp pose: {grasp_result.get('message')}")

        grasp_pose = grasp_result["data"]["position"]
        print(f"Grasp pose recorded: {grasp_pose}")

        # Step 7: Calculate offset using robot's pose operations
        try:
            # offset = pose_trans(pose_inverse(tag_pose), grasp_pose)
            tag_inv = robot.pose_inverse(tag_pose)
            offset = robot.pose_trans(tag_inv, grasp_pose)

            # Verify
            verify = robot.pose_trans(tag_pose, offset)
            print(f"Offset: {offset}")
            print(f"Verify: pose_trans(tag_pose, offset) = {verify}")

        except Exception as e:
            # Fallback: manual calculation if robot methods fail
            print(f"Using fallback offset calculation: {e}")
            offset = {
                'x': grasp_pose['x'] - tag_pose['x'],
                'y': grasp_pose['y'] - tag_pose['y'],
                'z': grasp_pose['z'] - tag_pose['z'],
                'rx': grasp_pose['rx'] - tag_pose['rx'],
                'ry': grasp_pose['ry'] - tag_pose['ry'],
                'rz': grasp_pose['rz'] - tag_pose['rz']
            }

        return _success(
            data={
                "tag_id": tag_id,
                "tag_pose": tag_pose,
                "grasp_pose": grasp_pose,
                "offset": offset
            },
            message=f"Successfully taught grasp offset for tag {tag_id}"
        )

    except Exception as e:
        # Ensure teach mode is exited on error
        try:
            end_teach_mode(robot_id)
        except:
            pass
        return _error(f"Teach offset failed: {str(e)}", str(e))


def _approach_tag(
    tag_id: int,
    way: str,
    signal_id: int,
    front_distance: float,
    robot,
    robot_id: str,
    camera_id: str
) -> Dict[str, Any]:
    """
    Move robot to a position in front of the tag.

    Args:
        tag_id: AprilTag ID
        way: Communication method
        signal_id: Signal index
        front_distance: Distance in front of tag (meters, negative = towards tag)
        robot: Robot instance
        robot_id: Robot identifier
        camera_id: Camera identifier
    """
    # Get tag position
    result = get_tag_pose(tag_id, way, signal_id, 30.0, robot_id, camera_id)
    if not result["success"]:
        return result

    tag_pose = result["data"]["pose"]

    # Calculate approach position (in front of tag)
    # In tag frame, Z points outward, so negative Z moves towards tag
    approach_pose = {
        'x': tag_pose['x'],
        'y': tag_pose['y'],
        'z': tag_pose['z'] - front_distance,  # front_distance meters in front
        'rx': tag_pose['rx'],
        'ry': tag_pose['ry'],
        'rz': tag_pose['rz']
    }

    # Move to approach position using movej
    print(f"Moving to {front_distance*100:.0f}cm in front of tag...")
    try:
        robot.movej(approach_pose, 0.1, 0.1, None, None)
        robot.wait_move()
        return _success(message=f"Reached position {front_distance}m in front of tag")
    except Exception as e:
        return _error(f"Failed to approach tag: {str(e)}", str(e))


def _wait_for_shoulder_button(robot, check_interval: float = 0.02):
    """
    Wait for SHOULDER digital input button press.

    Args:
        robot: Robot instance
        check_interval: Check interval in seconds (default: 20ms)
    """
    while True:
        try:
            # Check SHOULDER DI:0
            value = robot.get_di("SHOULDER", 0)
            if value != 0:
                print("Shoulder button pressed - confirming position")
                break
        except:
            pass
        time.sleep(check_interval)


@_robot_required
def grasp_with_offset(
    tag_id: int,
    offset: Dict[str, float],
    way: str = "signal",
    signal_id: int = 13,
    approach_height: float = 0.1,
    grasp_height: float = 0.0,
    robot=None,
    robot_id: str = "default",
    camera_id: str = "default"
) -> Dict[str, Any]:
    """
    Move to grasp position using previously taught offset.

    Args:
        tag_id: AprilTag ID to detect
        offset: Offset from tag to grasp pose {x, y, z, rx, ry, rz}
        way: Communication method - "signal" or "modbus"
        signal_id: Signal index for detection
        approach_height: Height above grasp position for approach (meters)
        grasp_height: Final grasp height relative to tag (meters)
        robot_id: Robot identifier
        camera_id: Camera identifier

    Returns:
        Success response with executed motion details

    Example:
        >>> # First teach the offset
        >>> result = teach_grasp_offset(tag_id=13)
        >>> offset = result["data"]["offset"]
        >>>
        >>> # Later use it to grasp
        >>> grasp_with_offset(tag_id=13, offset=offset, approach_height=0.1)
    """
    try:
        # Detect tag
        result = get_tag_pose(tag_id, way, signal_id, 30.0, robot_id, camera_id)
        if not result["success"]:
            return result

        tag_pose = result["data"]["pose"]

        # Calculate grasp pose: pose_trans(tag_pose, offset)
        try:
            grasp_pose = robot.pose_trans(tag_pose, offset)
        except:
            # Fallback
            grasp_pose = {
                'x': tag_pose['x'] + offset['x'],
                'y': tag_pose['y'] + offset['y'],
                'z': tag_pose['z'] + offset['z'],
                'rx': tag_pose['rx'] + offset['rx'],
                'ry': tag_pose['ry'] + offset['ry'],
                'rz': tag_pose['rz'] + offset['rz']
            }

        # Adjust for grasp height
        grasp_pose['z'] += grasp_height

        # Approach position
        approach_pose = grasp_pose.copy()
        approach_pose['z'] += approach_height

        # Open gripper
        control_gripper(amplitude=100)
        time.sleep(0.5)

        # Move to approach position
        print(f"Moving to approach position: {approach_pose}")
        robot.movel(approach_pose, 1.0, 0.2, None, None)
        robot.wait_move()

        # Move to grasp position
        print(f"Moving to grasp position: {grasp_pose}")
        robot.movel(grasp_pose, 1.0, 0.1, None, None)
        robot.wait_move()

        # Close gripper
        control_gripper(amplitude=0)
        time.sleep(0.5)

        # Lift up
        print("Lifting object...")
        robot.movel(approach_pose, 1.0, 0.2, None, None)
        robot.wait_move()

        return _success(
            data={
                "tag_id": tag_id,
                "tag_pose": tag_pose,
                "grasp_pose": grasp_pose,
                "offset_applied": offset
            },
            message=f"Successfully grasped object at tag {tag_id}"
        )

    except Exception as e:
        return _error(f"Grasp with offset failed: {str(e)}", str(e))


@_robot_required
def save_offset_config(
    name: str,
    tag_id: int,
    offset: Dict[str, float],
    robot=None,
    robot_id: str = "default"
) -> Dict[str, Any]:
    """
    Save offset configuration to robot.

    Args:
        name: Configuration name
        tag_id: AprilTag ID
        offset: Offset data {x, y, z, rx, ry, rz}
        robot_id: Robot identifier

    Returns:
        Success response
    """
    try:
        config = {
            "tag_id": tag_id,
            "offset": offset
        }
        robot.save_pose(f"apriltag_offset_{name}", config)
        return _success(message=f"Offset config '{name}' saved")
    except Exception as e:
        return _error(f"Failed to save config: {str(e)}", str(e))


@_robot_required
def load_offset_config(
    name: str,
    robot=None,
    robot_id: str = "default"
) -> Dict[str, Any]:
    """
    Load offset configuration from robot.

    Args:
        name: Configuration name
        robot_id: Robot identifier

    Returns:
        Success response with offset data
    """
    try:
        config = robot.load_pose(f"apriltag_offset_{name}")
        return _success(
            data=config,
            message=f"Offset config '{name}' loaded"
        )
    except Exception as e:
        return _error(f"Failed to load config: {str(e)}", str(e))


# ============================================================================
# Main entry point for CLI execution
# ============================================================================

if __name__ == "__main__":
    import json
    print(json.dumps({
        "message": "AprilTag Offset Teaching Skill",
        "description": "Guide users to teach grasp positions relative to AprilTag markers",
        "functions": [
            "teach_grasp_offset",
            "grasp_with_offset",
            "save_offset_config",
            "load_offset_config"
        ],
        "workflow": [
            "1. Move to tag front for optimal camera view",
            "2. Detect and record tag pose",
            "3. Enter teach mode for user guidance",
            "4. Wait for shoulder button confirmation",
            "5. Calculate offset from tag to grasp pose"
        ]
    }, indent=2))
