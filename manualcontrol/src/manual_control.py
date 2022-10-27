#! /usr/bin/env python3

import rospy
from motion_msgs.msg import ManualControl
import sys, select, os
if os.name == 'nt':
  import msvcrt
else:
  import tty, termios

MAX_THROTTLE = 1
MIN_THROTTLE = 0

MAX_STEERING = 1
MIN_STEERING = -1

MAX_BRAKE = 1
MIN_BRAKE = 0

MAX_GEAR = 7
MIN_GEAR = 0

MAX_HANDBRAKE = 1
MIN_HANDBRAKE = 0

THROTTLE_STEP_SIZE = 0.01
STEERING_STEP_SIZE = 0.05
BRAKE_STEP_SIZE = 0.1
GEAR_STEP_SIZE = 1
HANDBRAKE_STEP_SIZE = 1

msg = """
Control Your Vehicle!
---------------------------
Moving around:
   q    w    e
   a    s    d
        x

w : increase throttle (minimum:0, maximum:1, step_size=0.01)
a/d : increase/decrease steering (minimum:-1, maximum:1, step_size=0.05)
q/e : increase/decrease gear (minimum:0, maximum:1, step_size=0.01)
x : Brake
s/space_key : Hand Brake (force stop)


CTRL-C to quit
"""

e = """
Communications Failed
"""

def getKey():
    if os.name == 'nt':
      if sys.version_info[0] >= 3:
        return msvcrt.getch().decode()
      else:
        return msvcrt.getch()

    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def postn(target_throttle, target_steering, target_gear, target_brake, target_handbrake):
    return "currently:\tthrottle %s\t steering %s\t gear %s\t brake %s\t handbrake%s " % (target_throttle,target_steering,target_gear,target_brake,target_handbrake)


def constrain(input, low, high):
    if input < low:
      input = low
    elif input > high:
      input = high
    else:
      input = input

    return input

def checkThrottleLimit(pos):
    pos = constrain(pos, MIN_THROTTLE, MAX_THROTTLE)
    return pos

def checkSteeringLimit(pos):
    pos = constrain(pos, MIN_STEERING, MAX_STEERING)
    return pos

def checkGearLimit(pos):
    pos = constrain(pos, MIN_GEAR, MAX_GEAR)
    return pos

def checkBrakeLimit(pos):
    pos = constrain(pos, MIN_BRAKE, MAX_BRAKE)
    return pos

def checkHandbrakeLimit(pos):
    pos = constrain(pos, MIN_HANDBRAKE, MAX_HANDBRAKE)
    return pos

if __name__=="__main__":
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('manualcontrol')
    pub = rospy.Publisher('/pedal_pos', ManualControl, queue_size=10)

 
    status = 0
    target_throttle  = 0.0
    target_steering  = 0.0
    target_gear = 0.0
    target_brake = 0.0
    target_handbrake = 0.0



    print(msg)
    while(1):
        key = getKey()
        if key == 'w' :
            target_throttle = checkThrottleLimit(target_throttle + THROTTLE_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
        elif key == 'a' :
            target_steering = checkSteeringLimit(target_steering + STEERING_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
        elif key == 'd' :
            target_steering = checkSteeringLimit(target_steering - STEERING_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
        elif key == 'x' :
            target_brake = checkBrakeLimit(target_brake + BRAKE_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
        elif key == 'q' :
            target_gear = checkGearLimit(target_gear + GEAR_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
        elif key == 'e' :
            target_gear = checkGearLimit(target_gear - GEAR_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
        elif key == ' ' or key == 's' :
            target_handbrake = checkHandbrakeLimit(target_handbrake + HANDBRAKE_STEP_SIZE)
            status = status + 1
            print(postn(target_throttle, target_steering,target_gear,target_brake,target_handbrake))
        elif (key == '\x03'):
                break
        else :
            while (target_throttle>0) or (target_steering>0) or (target_brake>0) or (target_handbrake>0):
                target_steering = 0
                target_throttle = 0
                target_brake = 0
                target_handbrake = 0 
                print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))
            while (target_steering<0) :
                target_steering = 0
                print(postn(target_throttle,target_steering,target_gear,target_brake,target_handbrake))


        motion = ManualControl()
        motion.Throttle = target_throttle
        motion.Steering = target_steering
        motion.Gear = target_gear
        motion.Brake = target_brake
        motion.Handbrake = target_handbrake
        pub.publish(motion)
    

    
    motion = ManualControl()
    motion.Throttle = 0.0
    motion.Steering = 0.0
    motion.Gear = 0.0
    motion.Brake = 0.0
    motion.Handbrake = 0.0
    pub.publish(motion)

if os.name != 'nt':
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

