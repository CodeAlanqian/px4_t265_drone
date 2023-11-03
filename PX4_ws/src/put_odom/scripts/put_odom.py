#! /usr/bin/env python
# coding=utf-8
import rospy
import tf
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf import transformations
import math

odom = Odometry()
odom
def callback_cameraodom(msg):
    global odom
    odom = msg


if __name__ == "__main__":
    rospy.init_node("put_odom",anonymous=True)
    rate = rospy.Rate(50)
    camera_odom_sub = rospy.Subscriber("camera/odom/sample",Odometry,callback = callback_cameraodom)
    odom_pub = rospy.Publisher("odom",Odometry,queue_size=50)
    odom_broadcaster = tf.TransformBroadcaster()
    odom_trans = TransformStamped()
    current_time = rospy.Time.now()
    last_time = rospy.Time.now()
    x = 0.0
    y = 0.0
    while not rospy.is_shutdown():
        current_time = rospy.Time.now()
        dt = (current_time-last_time).to_sec() 

        euler = transformations.euler_from_quaternion([odom.pose.pose.orientation.x,odom.pose.pose.orientation.y,odom.pose.pose.orientation.z,odom.pose.pose.orientation.w])
        yaw = euler[2]*math.pi/180

        delta_x = (odom.twist.twist.linear.x*math.cos(yaw) - odom.twist.twist.linear.y*math.sin(yaw)) * dt
        delta_y = (odom.twist.twist.linear.x*math.sin(yaw) + odom.twist.twist.linear.y*math.cos(yaw)) * dt

        x += delta_x
        y += delta_y
    
        odom_trans.header.stamp = current_time
        odom_trans.header.frame_id = "odom"
        odom_trans.child_frame_id = "base_link"

        odom_trans.transform.translation.x = x
        odom_trans.transform.translation.y = y
        odom_trans.transform.translation.z = 0
        odom_trans.transform.rotation = odom.pose.pose.orientation

        odom_broadcaster.sendTransformMessage(odom_trans)

        odom.header.stamp = current_time
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        odom.pose.pose.position.z = 0
        odom.twist.twist.linear.z = 0

        odom_pub.publish(odom)

        last_time = current_time
        rate.sleep()
