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
        control_gripper,
        get_robot_state,
        get_current_position,
        get_current_joints,
        estop,
        set_payload,
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
    print(f"  Connect result: {result.get('message', 'Unknown')}")

    # Disconnect
    result = disconnect_robot(robot_id="default")
    assert result.get("success") == True
    print(f"  Disconnect result: {result.get('message', 'Unknown')}")

    print("  ✓ Connect/disconnect test passed")
    return True


def test_status_functions():
    """Test status functions (should handle not connected gracefully)."""
    print("Testing status functions...")

    from skills.lebai_robot import (
        get_robot_state,
        get_current_position,
        get_current_joints,
    )

    # These should return error when not connected
    status = get_robot_state()
    assert status.get("success") == False
    print(f"  Status (not connected): {status.get('message', 'Unknown')}")

    position = get_current_position()
    assert position.get("success") == False
    print(f"  Position (not connected): {position.get('message', 'Unknown')}")

    joints = get_current_joints()
    assert joints.get("success") == False
    print(f"  Joints (not connected): {joints.get('message', 'Unknown')}")

    print("  ✓ Status functions test passed")
    return True


def test_motion_functions():
    """Test motion functions (should handle not connected gracefully)."""
    print("Testing motion functions...")

    from skills.lebai_robot import movel, estop

    # These should return error when not connected
    move_result = movel(p={"x": 0.1, "y": 0, "z": 0.2, "rx": 0, "ry": 0, "rz": 0}, a=1, v=0.2)
    assert move_result.get("success") == False
    print(f"  Move (not connected): {move_result.get('message', 'Unknown')}")

    stop_result = estop()
    assert stop_result.get("success") == False
    print(f"  E-stop (not connected): {stop_result.get('message', 'Unknown')}")

    print("  ✓ Motion functions test passed")
    return True


def test_gripper_control():
    """Test gripper control function."""
    print("Testing gripper control...")

    from skills.lebai_robot import control_gripper

    result = control_gripper(action="open")
    assert "success" in result
    print(f"  Gripper (not connected): {result.get('message', 'Unknown')}")

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
