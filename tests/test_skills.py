#!/usr/bin/env python3
"""
Test script for Lebai Robot Skills

Run with: python3 tests/test_skills.py
All tests are synchronous - no asyncio required.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all skills can be imported."""
    print("Testing imports...")

    from skills.lebai_robot import (
        connect_robot,
        disconnect_robot,
        move_to_position,
        move_to_joint_angles,
        control_gripper,
        get_robot_status,
        get_current_position,
        get_current_joints,
        emergency_stop,
        set_payload,
    )
    from skills.lebai_batch import (
        execute_motion_sequence,
        pick_and_place,
        calibration_routine,
        monitor_status_loop,
        waypoint_navigation,
    )

    print("  ✓ All skills imported successfully")
    return True


def test_connect_disconnect():
    """Test connect and disconnect functions."""
    print("Testing connect/disconnect...")

    from skills.lebai_robot import connect_robot, disconnect_robot

    # Try to connect (will fail without real robot, but tests the function)
    result = connect_robot(host="192.168.4.63", port=3030)
    assert "success" in result
    assert "message" in result
    print(f"  Connect result: {result['message']}")

    # Disconnect
    result = disconnect_robot(robot_id="default")
    assert result.get("success") == True
    print(f"  Disconnect result: {result['message']}")

    print("  ✓ Connect/disconnect test passed")
    return True


def test_status_functions():
    """Test status functions (should handle not connected gracefully)."""
    print("Testing status functions...")

    from skills.lebai_robot import (
        get_robot_status,
        get_current_position,
        get_current_joints,
    )

    # These should return error when not connected
    status = get_robot_status()
    assert status.get("success") == False
    print(f"  Status (not connected): {status['message']}")

    position = get_current_position()
    assert position.get("success") == False
    print(f"  Position (not connected): {position['message']}")

    joints = get_current_joints()
    assert joints.get("success") == False
    print(f"  Joints (not connected): {joints['message']}")

    print("  ✓ Status functions test passed")
    return True


def test_motion_functions():
    """Test motion functions (should handle not connected gracefully)."""
    print("Testing motion functions...")

    from skills.lebai_robot import move_to_position, emergency_stop
    from skills.lebai_batch import execute_motion_sequence

    # These should return error when not connected
    move_result = move_to_position(x=100, y=0, z=200)
    assert move_result.get("success") == False
    print(f"  Move (not connected): {move_result['message']}")

    stop_result = emergency_stop()
    assert stop_result.get("success") == False
    print(f"  E-stop (not connected): {stop_result['message']}")

    sequence_result = execute_motion_sequence(positions=[])
    assert sequence_result.get("success") == False
    print(f"  Sequence (not connected): {sequence_result['message']}")

    print("  ✓ Motion functions test passed")
    return True


def test_gripper_control():
    """Test gripper control function."""
    print("Testing gripper control...")

    from skills.lebai_robot import control_gripper

    result = control_gripper(action="open")
    assert "success" in result
    print(f"  Gripper (not connected): {result['message']}")

    print("  ✓ Gripper control test passed")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Lebai Robot Skills - Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Imports", test_imports),
        ("Connect/Disconnect", test_connect_disconnect),
        ("Status Functions", test_status_functions),
        ("Motion Functions", test_motion_functions),
        ("Gripper Control", test_gripper_control),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Tests completed: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
