#! /usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

rospy.init_node('cv_node')
pub = rospy.Publisher('/cmd_vel', Twist, 
  queue_size=10)
last_linx=0
last_angz=0
br = CvBridge()

def callback(data):
    global last_angz
    global last_linx
    try:
        cv_image = br.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
        print(e)
    im_cut = cv_image[750:800,0:800]
    #cv2.imshow("Image window", im_cut)
    im_grey = img_gray = cv2.cvtColor(im_cut, cv2.COLOR_BGR2GRAY)
    threshold = 100
    _, binary = cv2.threshold(im_grey,threshold,255,cv2.THRESH_BINARY)
    numpy_vertical = np.vstack((im_grey,binary))
    cv2.imshow("Image window", numpy_vertical)
    mass_x, mass_y = np.where(binary <= 0)
    if mass_x.size > 0 or mass_y.size > 0:
        cent_y = np.average(mass_x)
        cent_x = np.average(mass_y)
        last_linx = 2
        last_angz = (400-cent_x)/100
        move = Twist()
        move.linear.x = last_linx
        move.angular.z = last_angz
    else:
        cent_x = 0
        cent_y = 0
        move = Twist()
        move.linear.x = last_linx
        move.angular.z = last_angz

    
    
    rospy.loginfo("center x: %d, center y %d",cent_x, cent_y)

    pub.publish(move)

    # cv2.imshow("Image window", binary)
    cv2.waitKey(3)

def cv_control():
    rospy.Subscriber('/rrbot/camera1/image_raw',Image,callback)

while not rospy.is_shutdown():
    cv_control()
    rospy.spin()
