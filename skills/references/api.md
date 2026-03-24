# Lebai Robot Skill - 完整 API 文档

已暴露 lebai-sdk 的所有接口，共 **130+ 个函数**。

## 官方文档

- **乐白机器人帮助文档**: [https://help.lebai.ltd](https://help.lebai.ltd)
- **Python SDK 使用指南**: [https://help.lebai.ltd/SDK/Python SDK/](https://help.lebai.ltd/SDK/Python%20SDK/)
- **Python 编程示例**: [https://help.lebai.ltd/编程示例/Python 例程.html](https://help.lebai.ltd/%E7%BC%96%E7%A8%8B%E7%A4%BA%E4%BE%8B/Python%20%E4%BE%8B%E7%A8%8B.html)
- **常见问题 FAQ**: [https://help.lebai.ltd/faq/](https://help.lebai.ltd/faq/)

## 常见问题 FAQ

| 问题 | 描述 |
|------|------|
| **机械臂运动指令有哪些** | 所有运动命令概述：MoveL, MoveC, MoveJ, SpeedL, SpeedJ, MovePT, MovePVT, MovePVAT, TowardJ |
| **为什么直线运动总是报错** | 直线运动错误排查 |
| **为什么要设置末端负载** | 为什么示教模式和碰撞检测需要负载配置 |
| **如何手动控制碰撞检测** | 如何启用/禁用碰撞检测以及监控碰撞扭矩 |
| **为什么没有示教器** | 无示教器设计的说明 |
| **新夹爪 IO 使用说明** | 新夹爪 IO 布线和配置指南 |
| **夹爪安装说明** | 夹爪安装说明 |

## 接口分类

### 1. 连接管理 (4 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `connect_robot` | 连接机器人 | host, port (bool/int, True=3030 仿真，False=3031 真机), robot_id |
| `disconnect_robot` | 断开连接 | robot_id |
| `is_connected` | 检查连接状态 | robot_id |
| `wait_disconnect` | 等待断开 | robot_id |

### 2. 基本运动控制 (6 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `towardj` | 关节插值运动 | p (关节数组 rad), a (rad/s²), v (rad/s), t, r |
| `movej` | 关节规划运动 | p (关节数组 rad), a (rad/s²), v (rad/s), t, r |
| `movel` | 直线运动 | p (笛卡尔 m, rad), a (m/s²), v (m/s), t, r |
| `movec` | 圆弧运动 | via (m, rad), p (m, rad), rad (m), a (m/s²), v (m/s), t, r |

### 3. 高级运动控制 (5 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `move_pt` | 时间点运动 | p (关节数组 rad), t |
| `move_pvt` | 位置 - 速度 - 时间运动 | p (关节数组 rad), v (rad/s), t |
| `move_pvat` | 位置 - 速度 - 加速度 - 时间运动 | p (关节数组 rad), v (rad/s), a (rad/s²), t |
| `speedj` | 关节速度控制 | a (rad/s²), v (rad/s), t |
| `speedl` | 笛卡尔速度控制 | a (m/s²), v (m/s, rad/s), t, frame |
| `move_trajectory` | 执行轨迹 | name, dir |

### 4. 运动状态 (7 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `wait_move` | 等待运动完成 | id |
| `pause_move` | 暂停运动 | - |
| `resume_move` | 恢复运动 | - |
| `stop_move` | 停止运动 | - |
| `get_running_motion` | 获取运行中运动 ID | - |
| `get_motion_state` | 获取运动状态 | id |
| `can_move` | 检查是否可运动 | robot_state |

### 5. 系统控制 (7 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `estop` | 急停 | - |
| `get_estop_reason` | 获取急停原因 | - |
| `start_sys` | 启动系统 | - |
| `stop_sys` | 停止系统 | - |
| `reboot` | 重启控制器 | - |
| `powerdown` | 关机 | - |
| `find_zero` | 回零 | - |

### 6. 示教模式 (2 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `teach_mode` | 进入示教模式 | - |
| `end_teach_mode` | 退出示教模式 | - |

### 7. 状态读取 (9 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `get_robot_state` | 机器人状态 | - |
| `get_current_position` | 当前位置 (mm, °) | - |
| `get_current_joints` | 当前关节 (°) | - |
| `get_kin_data` | 运动学数据 | - |
| `get_phy_data` | 物理数据 | - |
| `get_payload` | 负载配置 | - |
| `get_gravity` | 重心配置 | - |
| `get_tcp` | TCP 偏移量（相对于法兰末端） | - |
| `get_velocity_factor` | 速度因子 | - |

### 8. 配置设置 (9 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_payload` | 设置负载 | mass, cog |
| `set_gravity` | 设置重心 | pose |
| `set_tcp` | 设置 TCP 偏移量（相对于法兰末端） | pose |
| `set_velocity_factor` | 设置速度因子 | speed_factor |
| `enable_joint_limits` | 启用关节限位 | - |
| `disable_joint_limits` | 禁用关节限位 | - |
| `enable_collision_detector` | 启用碰撞检测 | - |
| `disable_collision_detector` | 禁用碰撞检测 | - |
| `set_collision_detector_sensitivity` | 碰撞检测灵敏度 | sensitivity |

### 9. 夹爪控制 (3 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `init_gripper` | 初始化夹爪 | force |
| `get_gripper` | 获取夹爪状态 | - |
| `control_gripper` | 控制夹爪 | force, amplitude |

### 10. 位姿操作 (11 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `save_pose` | 保存位姿 | name, pose, dir, refer<br>pose: {x,y,z,rx,ry,rz}字典或关节数组; refer: 关节数组 |
| `load_pose` | 加载位姿 | name, dir, raw_pose<br>raw_pose=False: 返回关节位置; raw_pose=True: 原样返回 |
| `load_tcp` | 加载 TCP | name, dir |
| `load_frame` | 加载坐标系 | name, dir |
| `load_led_style` | 加载 LED 样式 | name, dir |
| `load_payload` | 加载负载配置 | name, dir |
| `pose_inverse` | 位姿求逆 | p |
| `pose_add` | 位姿相加 | pose, delta, frame |
| `kinematics_forward` | 正运动学 | p |
| `kinematics_inverse` | 逆运动学 | p, refer |
| `in_pose` | 检查位姿 | p |
| `measure_manipulation` | 操作度测量 | p |

### 11. 任务管理 (8 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `start_task` | 启动任务 | scene, params, dir, is_parallel, loop_to |
| `get_task_list` | 获取任务列表 | - |
| `get_main_task_id` | 获取主任务 ID | - |
| `get_task_state` | 获取任务状态 | id |
| `pause_task` | 暂停任务 | id |
| `resume_task` | 恢复任务 | id |
| `cancel_task` | 取消任务 | id |
| `wait_task` | 等待任务完成 | id |

### 12. 数字 I/O (7 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_dio_mode` | 设置 DIO 模式 | device, pin, mode |
| `get_dio_mode` | 获取 DIO 模式 | device, pin |
| `set_do` | 设置数字输出 | device, pin, value |
| `get_do` | 获取数字输出 | device, pin |
| `get_dos` | 获取多个数字输出 | device, pin, num |
| `get_di` | 获取数字输入 | device, pin |
| `get_dis` | 获取多个数字输入 | device, pin, num |

### 13. 模拟 I/O (5 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_ao` | 设置模拟输出 | device, pin, value |
| `get_ao` | 获取模拟输出 | device, pin |
| `get_aos` | 获取多个模拟输出 | device, pin, num |
| `get_ai` | 获取模拟输入 | device, pin |
| `get_ais` | 获取多个模拟输入 | device, pin, num |

### 14. 信号 (5 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_signal` | 设置信号 | index, value |
| `add_signal` | 添加信号 | index, value |
| `get_signal` | 获取信号 | index |
| `get_signals` | 获取多个信号 | index, len |
| `set_signals` | 设置多个信号 | index, values |

### 15. 串口通信 (7 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_serial_baud_rate` | 设置波特率 | device, baud_rate |
| `set_serial_timeout` | 设置超时 | device, timeout |
| `set_serial_parity` | 设置校验 | device, parity |
| `set_flange_baud_rate` | 设置法兰波特率 | baud_rate |
| `write_serial` | 写入串口 | device, data |
| `read_serial` | 读取串口 | device, len |
| `clear_serial` | 清空串口 | device |

### 16. Modbus (12 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `read_coils` | 读线圈 | device, pin, count |
| `read_discrete_inputs` | 读离散输入 | device, pin, count |
| `read_holding_registers` | 读保持寄存器 | device, pin, count |
| `read_input_registers` | 读输入寄存器 | device, pin, count |
| `write_single_coil` | 写单线圈 | device, pin, value |
| `write_single_register` | 写单寄存器 | device, pin, value |
| `write_multiple_coils` | 写多线圈 | device, pin, values |
| `write_multiple_registers` | 写多寄存器 | device, pin, values |
| `set_modbus_timeout` | 设置超时 | device, timeout |
| `set_modbus_retry` | 设置重试 | device, retry |
| `disconnect_modbus` | 断开 Modbus | device |

### 17. LED 控制 (4 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_led` | 设置 LED | mode, speed, colors |
| `set_led_style` | 设置 LED 样式 | style |
| `set_fan` | 设置风扇 | mode |
| `set_voice` | 设置语音 | voice, volume |

### 18. 数据存储 (3 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `set_item` | 设置键值 | key, value |
| `get_item` | 获取键值 | key |
| `get_items` | 获取键值列表 | prefix |

### 19. 高级功能 (3 个)

| 函数 | 描述 | 参数 |
|------|------|------|
| `run_plugin_cmd` | 运行插件命令 | name, params |
| `call` | 调用任意方法 | method, param |
| `subscribe` | 订阅数据 | method, param |

## 使用示例

### 基本运动

```python
from skills import connect_robot, movej, movel, get_current_position, disconnect_robot

# 连接 - 仿真模式 (port=True 或 3030)
connect_robot(host="127.0.0.1", port=True)
# 连接 - 真机模式 (port=False 或 3031, 默认)
connect_robot(host="192.168.4.63", port=False)

# 移动到笛卡尔位置 (字典格式：{x, y, z, rx, ry, rz})
movel(p={"x": 0.2, "y": 0, "z": 0.2, "rx": 3.14159, "ry": 0, "rz": 0}, a=1, v=0.2)

# 获取位置
pos = get_current_position()
print(pos['position'])

# 断开
disconnect_robot()
```

### 数字输出控制

```python
from skills import set_do, get_di

# 设置 DO
set_do(device="do1", pin=0, value=1)

# 读取 DI
result = get_di(device="di1", pin=0)
print(result['value'])
```

### 保存和加载位姿

```python
from skills import save_pose, load_pose, movel

# 使用笛卡尔坐标保存位姿
save_pose(name="cartesian_pose", pose={"x": 0.3, "y": 0.2, "z": 0.4, "rx": 3.14, "ry": 0, "rz": 0})

# 使用关节角度保存位姿
save_pose(name="joint_pose", pose=[0, -1.57, 1.57, 0, 0, 0])

# 使用笛卡尔坐标保存位姿，并指定参考关节（用于奇异点情况）
save_pose(name="pose_with_refer", pose={"x": 0.3, "y": 0.2, "z": 0.4, "rx": 3.14, "ry": 0, "rz": 0}, refer=[0, -1.57, 1.57, 0, 0, 0])

# 加载位姿并移动 (默认返回关节位置)
pose = load_pose(name="cartesian_pose")
movel(p=pose['pose'], a=1, v=0.2)

# 使用 raw_pose=True 获取原始存储的位姿（可能是笛卡尔坐标或关节位置）
raw_pose = load_pose(name="cartesian_pose", raw_pose=True)
```

### Modbus 通信

```python
from skills import read_holding_registers, write_single_register

# 读取寄存器
result = read_holding_registers(device="modbus0", pin=0, count=10)
print(result['values'])

# 写入寄存器
write_single_register(device="modbus0", pin=0, value=100)
```

### 调用任意方法

```python
from skills import call

# 获取版本
result = call("get_version", None)
print(result['result'])
```

## 部署位置

技能已安装到：`/home/lebai/.openclaw/workspace/skills/lebai-robot/`

## 测试

```bash
cd /home/lebai
python3 test_full_api.py
```
