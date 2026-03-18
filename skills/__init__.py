"""
Lebai Robot Skills Package

Comprehensive control over Lebai robotic arms.
This package exposes all available lebai-sdk interfaces.
"""

from .lebai_robot import (
    # Connection Management
    connect_robot,
    disconnect_robot,
    is_connected,
    wait_disconnect,
    
    # Motion Control - Basic
    towardj,
    movej,
    movel,
    movec,
    move_to_position,
    move_to_joint_angles,
    
    # Motion Control - Advanced
    move_pt,
    move_pvt,
    move_pvat,
    speedj,
    speedl,
    move_trajectory,
    
    # Motion Control - Status
    wait_move,
    pause_move,
    resume_move,
    stop_move,
    get_running_motion,
    get_motion_state,
    can_move,
    
    # System Control
    estop,
    get_estop_reason,
    start_sys,
    stop_sys,
    reboot,
    powerdown,
    find_zero,
    
    # Teaching Mode
    teach_mode,
    end_teach_mode,
    
    # Status and Data
    get_robot_state,
    get_tcp,
    get_current_position,
    get_current_joints,
    get_kin_data,
    get_phy_data,
    get_payload,
    get_gravity,
    get_velocity_factor,
    
    # Configuration
    set_payload,
    set_gravity,
    set_tcp,
    set_velocity_factor,
    enable_joint_limits,
    disable_joint_limits,
    enable_collision_detector,
    disable_collision_detector,
    set_collision_detector_sensitivity,
    
    # Gripper Control
    init_gripper,
    get_gripper,
    control_gripper,
    
    # Pose Operations
    save_pose,
    load_pose,
    load_tcp,
    load_frame,
    load_led_style,
    load_payload,
    pose_inverse,
    pose_add,
    kinematics_forward,
    kinematics_inverse,
    in_pose,
    measure_manipulation,
    
    # Task Management
    start_task,
    get_task_list,
    get_main_task_id,
    get_task_state,
    pause_task,
    resume_task,
    cancel_task,
    wait_task,
    
    # Digital I/O
    set_dio_mode,
    get_dio_mode,
    set_do,
    get_do,
    get_dos,
    get_di,
    get_dis,
    
    # Analog I/O
    set_ao,
    get_ao,
    get_aos,
    get_ai,
    get_ais,
    
    # Signals
    set_signal,
    add_signal,
    get_signal,
    get_signals,
    set_signals,
    
    # Serial Communication
    set_serial_baud_rate,
    set_serial_timeout,
    set_serial_parity,
    set_flange_baud_rate,
    write_serial,
    read_serial,
    clear_serial,
    
    # Modbus
    read_coils,
    read_discrete_inputs,
    read_holding_registers,
    read_input_registers,
    write_single_coil,
    write_single_register,
    write_multiple_coils,
    write_multiple_registers,
    set_modbus_timeout,
    set_modbus_retry,
    disconnect_modbus,
    
    # LED Control
    set_led,
    set_led_style,
    set_fan,
    set_voice,
    
    # Items (Key-Value Storage)
    set_item,
    get_item,
    get_items,
    
    # Plugin and Advanced Features
    run_plugin_cmd,
    call,
    subscribe,
)

# Also import batch operations
from .lebai_batch import (
    execute_motion_sequence,
    pick_and_place,
    calibration_routine,
    monitor_status_loop,
    waypoint_navigation,
)

__all__ = [
    # Connection
    "connect_robot", "disconnect_robot", "is_connected", "wait_disconnect",
    
    # Motion Basic
    "towardj", "movej", "movel", "movec", "move_to_position", "move_to_joint_angles",
    
    # Motion Advanced
    "move_pt", "move_pvt", "move_pvat", "speedj", "speedl", "move_trajectory",
    
    # Motion Status
    "wait_move", "pause_move", "resume_move", "stop_move", "get_running_motion", 
    "get_motion_state", "can_move",
    
    # System
    "estop", "get_estop_reason", "start_sys", "stop_sys", "reboot", "powerdown", "find_zero",
    
    # Teaching
    "teach_mode", "end_teach_mode",
    
    # Status
    "get_robot_state", "get_tcp", "get_current_position", "get_current_joints", 
    "get_kin_data", "get_phy_data", "get_payload", "get_gravity", "get_velocity_factor",
    
    # Configuration
    "set_payload", "set_gravity", "set_tcp", "set_velocity_factor",
    "enable_joint_limits", "disable_joint_limits",
    "enable_collision_detector", "disable_collision_detector", 
    "set_collision_detector_sensitivity",
    
    # Gripper
    "init_gripper", "get_gripper", "control_gripper",
    
    # Pose
    "save_pose", "load_pose", "load_tcp", "load_frame", "load_led_style", "load_payload",
    "pose_inverse", "pose_add", "kinematics_forward", "kinematics_inverse", "in_pose", 
    "measure_manipulation",
    
    # Task
    "start_task", "get_task_list", "get_main_task_id", "get_task_state",
    "pause_task", "resume_task", "cancel_task", "wait_task",
    
    # Digital I/O
    "set_dio_mode", "get_dio_mode", "set_do", "get_do", "get_dos", "get_di", "get_dis",
    
    # Analog I/O
    "set_ao", "get_ao", "get_aos", "get_ai", "get_ais",
    
    # Signals
    "set_signal", "add_signal", "get_signal", "get_signals", "set_signals",
    
    # Serial
    "set_serial_baud_rate", "set_serial_timeout", "set_serial_parity", 
    "set_flange_baud_rate", "write_serial", "read_serial", "clear_serial",
    
    # Modbus
    "read_coils", "read_discrete_inputs", "read_holding_registers", 
    "read_input_registers", "write_single_coil", "write_single_register",
    "write_multiple_coils", "write_multiple_registers", "set_modbus_timeout",
    "set_modbus_retry", "disconnect_modbus",
    
    # LED
    "set_led", "set_led_style", "set_fan", "set_voice",
    
    # Items
    "set_item", "get_item", "get_items",
    
    # Advanced
    "run_plugin_cmd", "call", "subscribe",
    
    # Batch Operations
    "execute_motion_sequence", "pick_and_place", "calibration_routine", 
    "monitor_status_loop", "waypoint_navigation",
]
