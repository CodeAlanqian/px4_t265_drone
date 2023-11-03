#!/usr/bin/env python
# coding=utf-8

import rospy

from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import *
from mavros_msgs.msg import State
import math
import sys, select, termios, tty

# 空格：降落
# 5  ：开启offboard模式
# 6  ：解锁，准备起飞
# 7  ：起飞

msg = """
Control Your Turtlebot!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
space key, k : force stop
anything else : stop smoothly
b : switch to OmniMode/CommonMode
CTRL-C to quit
"""
Omni = 0 #全向移动模式

#键值对应移动/转向方向
moveBindings = {
        'i':( 1, 0),
        'o':( 1,-1),
        'j':( 0, 1),
        'l':( 0,-1),
        'u':( 1, 1),
        ',':(-1, 0),
        '.':(-1, 1),
        'm':(-1,-1),
           }

#键值对应速度增量
speedBindings={
        'q':(1.1,1.1),
        'z':(0.9,0.9),
        'w':(1.1,1),
        'x':(0.9,1),
        'e':(1,  1.1),
        'c':(1,  0.9),
          }

#获取键值函数
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


speed = 0.2 #默认移动速度 m/s
turn  = 1   #默认转向速度 rad/s
#以字符串格式返回当前速度
def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

sita = 0.0  # 朝向
z = 0
w = 0
zf = 1
# 回调函数:订阅无人机位姿
def pose_cb(m):
    global sita
    global z
    global w
    global zf
    z = m.pose.orientation.z
    w = m.pose.orientation.w
    # 计算朝向在x轴的上方还是下方
    if z*w > 0:
        zf = 1
    else:
        zf = -1
    sita = 2*math.acos(w)*180/math.pi
    # rospy.loginfo('%.2f\r',sita)

current_state = State()
# 回调函数：订阅mavros状态
def state_cb(state):
    global current_state
    current_state = state

#主函数
if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin) #获取键值初始化，读取终端相关属性
    
    rospy.init_node('turtlebot_teleop') #创建ROS节点
    pub = rospy.Publisher('mavros/setpoint_velocity/cmd_vel_unstamped', Twist, queue_size=5) #创建速度话题发布者
    # 订阅无人机位姿
    rospy.Subscriber('mavros/local_position/pose',PoseStamped, pose_cb)

    # 订阅mavros状态
    rospy.Subscriber('mavros/state',State,state_cb)

    # 定义起飞降落服务客户端（起飞，降落）
    setModeServer = rospy.ServiceProxy('mavros/set_mode',SetMode)

    armServer = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)

    x      = 0   #前进后退方向
    y      = 0   #左右移动方向
    z      = 0   #上下移动方向
    th     = 0   #转向/横向移动方向
    count  = 0   #键值不再范围计数
    target_speed = 0 #前进后退目标速度
    target_z_speed = 0 #上下运动目标速度
    target_turn  = 0 #转向目标速度
    control_speed = 0 #前进后退实际控制速度
    control_z_speed = 0 #上下运动实际控制速度
    control_turn  = 0 #转向实际控制速度
    try:
        print(msg) #打印控制说明
        print(vels(speed,turn)) #打印当前速度
        while(1):
            key = getKey() #获取键值

            # if key:
            #     print('key = ',key)
            
            #判断键值是否在移动/转向方向键值内
            # if key in moveBindings.keys():
            #     x  = moveBindings[key][0]
            #     th = moveBindings[key][1]
            #     count = 0

            if key == 'i':   #前进
                count = 0
                x = 1
                z = 0
            elif key == ',': #后退 
                count = 0
                x = -1
                z = 0
            elif key == 'j': #往左转
                count = 0
                th = 1
                z = 0
            elif key == 'l': #往右转
                count = 0
                th = -1
                z = 0
            elif key == 'r': #上升
                count = 0
                z = 1
            elif key == 'f': #下降
                count = 0
                z = -1
            #判断键值是否在速度增量键值内
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn  = turn  * speedBindings[key][1]
                count = 0
                print(vels(speed,turn)) #速度发生变化，打印出来

            #空键值/'k',相关变量置0
            elif key == 'k' :
                x  = 0
                y  = 0
                z  = 0
                th = 0
                control_speed = 0
                control_z_speed = 0
                control_turn  = 0

            # 降落
            elif key == ' ':
                print("Vehicle Land")
                setModeServer(custom_mode='AUTO.LAND')
            # 开启offboard模式
            elif key == '5':
                if current_state.mode != "OFFBOARD" :
                    setModeServer(custom_mode='OFFBOARD')
                    print("Offboard enabled")
            # 解锁，准备起飞
            elif key == '6':
                armServer(True) 
                print("Vehicle armed")
            # 起飞
            elif key == '7':
                print("Vehicle Takeoff")
                setModeServer(custom_mode='AUTO.TAKEOFF')

            #长期识别到不明键值，相关变量置0
            else:
                count = count + 1
                if count > 4:
                    x  = 0
                    y  = 0
                    z  = 0
                    th = 0
                if (key == '\x03'):
                    break

            #根据速度与方向计算目标速度
            target_speed = speed * x
            target_z_speed = speed * z
            target_turn  = turn * th

            #x方向平滑控制，计算前进后退实际控制速度
            if target_speed > control_speed:
                control_speed = min( target_speed, control_speed + 0.1 )
            elif target_speed < control_speed:
                control_speed = max( target_speed, control_speed - 0.1 )
            else:
                control_speed = target_speed
            
            #z方向平滑控制，实际控制速度
            if target_z_speed > control_z_speed:
                control_z_speed = min( target_z_speed, control_z_speed + 0.1 )
            elif target_z_speed < control_z_speed:
                control_z_speed = max( target_z_speed, control_z_speed - 0.1 )
            else:
                control_z_speed = target_z_speed

            #平滑控制，计算转向实际控制速度
            if target_turn > control_turn:
                control_turn = min( target_turn, control_turn + 0.5 )
            elif target_turn < control_turn:
                control_turn = max( target_turn, control_turn - 0.5 )
            else:
                control_turn = target_turn
         
            # 计算出y方向的sin值
            y_sita = math.sin(sita/180*math.pi)
            # 如果小于0，则改为正数
            if y_sita < 0:
                y_sita = -y_sita
            # 乘以y分量的正负（通过四元数z*w获得，z*w>0,y分量在x轴上方）
            y_sita = y_sita * zf

            twist = Twist()  #创建ROS速度话题变量
            twist.linear.x = control_speed * math.cos(sita/180*math.pi)
            twist.linear.y = control_speed * y_sita  # 朝向速度乘以y轴sin值
            twist.linear.z = control_z_speed
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = control_turn

            pub.publish(twist) #ROS发布速度话题

    #运行出现问题则程序终止并打印相关错误信息
    except Exception as e:
        print(e)

    #程序结束前发布速度为0的速度话题
    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = control_turn
        pub.publish(twist)

    #程序结束前设置终端相关属性
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

