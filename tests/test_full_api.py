#!/usr/bin/env python3
"""
Lebai Robot Skill - 完整 API 测试

测试所有可用的接口类别。
"""

from skills.lebai_robot_full import (
    connect_robot, disconnect_robot, get_robot_state, get_current_position,
    get_current_joints, estop, get_kin_data, get_phy_data,
    towardj, wait_move,
    set_do, get_di, set_ao, get_ai,
    control_gripper, init_gripper,
    save_pose, load_pose,
    start_task, get_task_list,
    call,
)

def main():
    print("=" * 60)
    print("Lebai Robot Skill - 完整 API 测试")
    print("=" * 60)
    
    # 1. 连接
    print("\n1. 连接测试...")
    result = connect_robot(host="127.0.0.1", port=3030)
    print(f"   连接：{result['message']}")
    if not result.get('success'):
        print("   无法连接，测试终止")
        return
    
    # 2. 基本状态
    print("\n2. 基本状态读取...")
    state = get_robot_state()
    print(f"   机器人状态：{state.get('status', 'unknown')}")
    
    pos = get_current_position()
    if pos.get('success'):
        p = pos['position']
        print(f"   TCP: X={p['x']:.1f}mm, Y={p['y']:.1f}mm, Z={p['z']:.1f}mm")
    
    joints = get_current_joints()
    if joints.get('success'):
        j = joints['joints']
        print(f"   关节：J1={j[0]:.1f}, J2={j[1]:.1f}, J3={j[2]:.1f}...")
    
    # 3. 运动学数据
    print("\n3. 运动学数据...")
    kin = get_kin_data()
    if kin.get('success'):
        kd = kin['kin_data']
        print(f"   实际关节：{len(kd.get('actual_joint_pose', []))} 轴")
        print(f"   实际 TCP: {kd.get('actual_tcp_pose', {})}")
    
    # 4. 物理数据
    print("\n4. 物理数据...")
    phy = get_phy_data()
    if phy.get('success'):
        pd = phy['phy_data']
        print(f"   关节温度：{pd.get('joint_temp', 'N/A')}")
        print(f"   关节电压：{pd.get('joint_voltage', 'N/A')}")
    
    # 5. 任务
    print("\n5. 任务管理...")
    tasks = get_task_list()
    print(f"   任务列表：{tasks.get('tasks', [])}")
    
    # 6. 调用任意方法
    print("\n6. call 方法测试...")
    result = call("get_version", None)
    print(f"   版本：{result.get('result', 'N/A')}")
    
    # 7. 断开
    print("\n7. 断开连接...")
    disconnect_robot()
    print("   已断开")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    print("\n可用的接口类别:")
    print("""
    - 连接管理：connect_robot, disconnect_robot, is_connected, wait_disconnect
    - 基本运动：towardj, movej, movel, movec
    - 高级运动：move_pt, move_pvt, move_pvat, speedj, speedl, move_trajectory
    - 运动状态：wait_move, pause_move, resume_move, stop_move, get_running_motion
    - 系统控制：estop, get_estop_reason, start_sys, stop_sys, reboot, powerdown, find_zero
    - 示教模式：teach_mode, end_teach_mode
    - 状态读取：get_robot_state, get_tcp, get_current_position, get_current_joints
    - 数据读取：get_kin_data, get_phy_data, get_payload, get_gravity
    - 配置设置：set_payload, set_gravity, set_tcp, set_velocity_factor
    - 安全功能：enable_joint_limits, disable_joint_limits, enable_collision_detector
    - 夹爪控制：init_gripper, get_gripper, control_gripper
    - 位姿操作：save_pose, load_pose, load_tcp, load_frame, kinematics_forward/inverse
    - 任务管理：start_task, get_task_list, get_task_state, pause_task, cancel_task
    - 数字 IO：set_do, get_do, set_dio_mode, get_di, get_dis
    - 模拟 IO：set_ao, get_ao, get_ai, get_ais
    - 信号：set_signal, get_signal, get_signals
    - 串口：write_serial, read_serial, set_serial_baud_rate
    - Modbus：read_coils, write_single_coil, read_holding_registers
    - LED：set_led, set_led_style, set_fan, set_voice
    - 存储：set_item, get_item, get_items
    - 高级：call, subscribe, run_plugin_cmd
    """)


if __name__ == "__main__":
    main()
