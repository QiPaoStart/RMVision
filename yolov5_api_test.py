# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 12:32:34 2023

@author: wangjiayu
"""

from robomaster import robot
from yolov5_api import yolov5_api
import cv2
import rule

r = rule.rule()

api = yolov5_api()
api.load()

ep_robot = robot.Robot()
ep_robot.initialize(conn_type='ap')

version = ep_robot.get_version()
print("Robot version: {0}".format(version))

ep_robot.set_robot_mode(mode="free")

rule.robo_led.setLED(ep_robot, color=rule.robo_led.blue)

ep_camera = ep_robot.camera
ep_camera.start_video_stream(display=False, resolution="360p")
ep_gimbal = ep_robot.gimbal
ep_gimbal.recenter().wait_for_completed()
ep_blaster = ep_robot.blaster
ep_chassis = ep_robot.chassis

target_x, target_y = 320, 180

def pidself(set_value, feedback_value,kp):
    k=kp
    error = set_value - feedback_value
    output = k * error
    return output

def getClosest(l):
    i = 0
    ri = 1e9
    for oi, obj in enumerate(l):
        radius = pow((target_x - obj[0]), 2) + pow((target_y - obj[1]), 2)
        if radius < ri:
            i = oi
            ri = radius
    return l[i]

r.sub_attack(ep_robot)

auto = True
cnt = 0

while True:

    r.heartbeat()
    frame = ep_camera.read_cv2_image(strategy="newest")
    res, im = api.detect_with_image(frame)
    robo, red, blue = api.convert_center(res)

    cnt += 1

    if len(blue) <= 0 and auto:
        #print("z reset." + str(cnt))
        ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)
        ep_chassis.drive_speed(z=0)
        
    if len(blue) > 0 and auto:
        
        selected = getClosest(blue)
        x = selected[0]
        y = selected[1]
        
        center = (int(x),int(y))

        if abs(target_x - x) < 11 and abs(target_y - y) < 10:
            speed_pitch=0
            speed_yaw=0
            r.fire(blaster=ep_blaster, fire_type="ir", times=1)
        else:
            speed_pitch = pidself(target_y, y,0.3)
            speed_yaw = - pidself(target_x, x,0.3)

        ep_gimbal.drive_speed(pitch_speed=speed_pitch , yaw_speed=speed_yaw)
        ep_chassis.drive_speed(z=speed_yaw)
        print(speed_yaw)
        
    cv2.imshow("Robot",im)
    
    c = cv2.waitKey(10)
    
    if not ((c >= ord("a") and c <= ord("z")) or (c >= ord("A") and c <= ord("Z"))):
        ep_chassis.drive_speed(x=0,y=0)
    
    if c == ord("w") or c == ord("W"): ep_chassis.drive_speed(x=0.3)
    if c == ord("q") or c == ord("Q"): ep_chassis.drive_speed(x=0.3, y=-0.3)
    if c == ord("e") or c == ord("E"): ep_chassis.drive_speed(x=0.3, y=0.3)
    if c == ord("a") or c == ord("A"): ep_chassis.drive_speed(y=-0.3)
    if c == ord("s") or c == ord("S"): ep_chassis.drive_speed(x=-0.3)
    if c == ord("d") or c == ord("D"): ep_chassis.drive_speed(y=0.3)
    if c == ord("z") or c == ord("Z"): ep_chassis.drive_speed(x=-0.3, y=-0.3)
    if c == ord("x") or c == ord("X"): ep_chassis.drive_speed(x=-0.3, y=0.3)
    if (c == ord("j") or c == ord("J")
            or c == ord("l") or c == ord("L") 
            or c == ord("i") or c == ord("I")
            or c == ord("k") or c == ord("K")):
        auto = False
        if c == ord("j") or c == ord("J"):
            ep_chassis.drive_speed(z=-50)
            ep_gimbal.drive_speed(yaw_speed=-50, pitch_speed=0)
        if c == ord("l") or c == ord("L"):
            ep_chassis.drive_speed(z=50)
            ep_gimbal.drive_speed(yaw_speed=50, pitch_speed=0)
        if c == ord("i") or c == ord("I"):
            ep_gimbal.drive_speed(pitch_speed=30, yaw_speed=0)
        if c == ord("k") or c == ord("K"):
            ep_gimbal.drive_speed(pitch_speed=-30, yaw_speed=0)
    else:
        auto = True
    if c == ord("f") or c == ord("F"):
        r.fire(blaster=ep_blaster, fire_type="ir", times=1)
    if c == ord("r") or c == ord("R"):
        ep_gimbal.recenter(pitch_speed=360, yaw_speed=360)
    if c & 0xFF == 27:
        ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)
        ep_chassis.drive_speed(x=0,y=0,z=0)
        break        

ep_gimbal.recenter().wait_for_completed()
ep_camera.stop_video_stream()
ep_robot.close()
cv2.destroyAllWindows() 

