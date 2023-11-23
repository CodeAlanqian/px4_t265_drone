#! /usr/bin/env python
# coding=utf-8
import rospy
from geometry_msgs.msg import PoseStamped,Twist
from std_msgs.msg import Bool
from mavros_msgs.msg import State,AttitudeTarget,PositionTarget
from mavros_msgs.srv import CommandBool, CommandBoolRequest, SetMode, SetModeRequest
import tf
from tf import transformations
import math

class PX4():
    def __init__(self) :
        self.current_state = State()
        #self.id = Bool(False)
        self.takeoff_state = Bool(False)
        self.current_local_pos = PoseStamped()
        self.state_sub = rospy.Subscriber("mavros/state", State, callback = self.state_cb)
        self.local_pos_sub = rospy.Subscriber("mavros/local_position/pose",PoseStamped,callback = self.local_pos_sub_callback)
        self.local_pub = rospy.Publisher("mavros/setpoint_position/local", PoseStamped, queue_size=10)
        self.local_vel_pub = rospy.Publisher("/mavros/setpoint_velocity/cmd_vel_unstamped", Twist, queue_size=10)

        self.takeoff_sub = rospy.Subscriber("/is_takeoff", Bool, callback = self.takeoff_cb)

        #self.identify_pub = rospy.Publisher("/identify", Bool,queue_size=10)

        rospy.wait_for_service("/mavros/cmd/arming")
        self.arming_client = rospy.ServiceProxy("mavros/cmd/arming", CommandBool)
        rospy.wait_for_service("/mavros/set_mode")
        self.set_mode_client = rospy.ServiceProxy("mavros/set_mode", SetMode)

        self.pose = PoseStamped()
        self.vel = Twist()

        self.offb_set_mode = SetModeRequest()
        self.arm_cmd = CommandBoolRequest()
    
    def takeoff_cb(self, msg):
        self.takeoff_state = msg
        print(msg)


    def state_cb(self,msg):
        self.current_state = msg
        
        print(msg.mode,msg.armed)

    def local_pos_sub_callback(self,msg):
        self.current_local_pos = msg

    def distance_jugdge(self,x,y,z=0.5):
        if math.sqrt(math.pow((self.current_local_pos.pose.position.x - x),2) + 
                                    math.pow((self.current_local_pos.pose.position.y - y),2) + 
                                    math.pow((self.current_local_pos.pose.position.z - z),2)) < 0.15:
            return True
        
    def set_velocity(self,x,y,z,yawrate):
        self.vel.linear.x = x
        self.vel.linear.y = y
        self.vel.linear.z = z
        self.vel.angular.z = yawrate

    def set_point(self,x,y,z,angle):
        self.pose.pose.position.x = x
        self.pose.pose.position.y = y
        self.pose.pose.position.z = z
        q = transformations.quaternion_from_euler(0,0,angle)
        self.pose.pose.orientation.x = q[0]
        self.pose.pose.orientation.y = q[1]
        self.pose.pose.orientation.z = q[2]
        self.pose.pose.orientation.w = q[3]
    
    def sett_PID_velocity(self,target_x,target_y,target_z,target_yaw):
        self.vel.linear.x = 0.75*(target_x-self.current_local_pos.pose.position.x)
        self.vel.linear.y = 0.75*(target_y-self.current_local_pos.pose.position.y)
        self.vel.linear.z = 3*(target_z-self.current_local_pos.pose.position.z)
        euler = transformations.euler_from_quaternion([self.current_local_pos.pose.orientation.x,
            self.current_local_pos.pose.orientation.y,
            self.current_local_pos.pose.orientation.z,
            self.current_local_pos.pose.orientation.w])
        self.vel.angular.z = (target_yaw - euler[2])