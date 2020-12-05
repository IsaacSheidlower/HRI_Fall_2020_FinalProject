#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import Image, SoundFile, ImageFile
from pybricks.ev3devices import Motor, TouchSensor
from pybricks.parameters import Port
import time 
from threading import Thread

class Q_agent(EV3Brick):
    def __init__(self, ev3, drive, obstacle_sensor, color_sensor, touch_left, touch_right, state_size,
                action_size, env, goal_states = [[3,3]]):
        super(Q_agent, self).__init__()

        self.ev3 = ev3
        self.drive = drive
        self.obstacle_sensor = obstacle_sensor
        self.color_sensor = color_sensor
        self.touch_left = touch_left
        self.touch_right = touch_right
        self.state_size = state_size
        self.action_size = action_size
        # self.q_table = q_table
        self.goal_states = goal_states
        self.env = env 
        self.agent_pos = [0,0]
        self.agent_state = 0
        self.orientation = "f"
        self.env_state = {} # states will be represented as digits, while positions as list coordinates.
        # This is so the q-table/feedback table is 2D. Here is a dictionary to switch between them
        counter = 0
        for i in range(len(env)):
            for j in range(len(env[i])):
                self.env_state[(i,j)] = counter
                counter += 1

    def get_feedback(self):
        stopwatch = StopWatch()
        stopwatch.reset()
        self.ev3.light.on(Color.ORANGE)
        while True:
            if self.touch_left.pressed():
                self.ev3.light.off()
                return -1
            elif self.touch_right.pressed():
                self.ev3.light.off()
                return 1
            if stopwatch.time() > 10000:
                self.ev3.light.off()
                return 0

    def get_double_press(self): # used to indicate a user has finished their time with CHORE bot
        stopwatch = StopWatch()
        stopwatch.reset()
        self.ev3.light.on(Color.ORANGE)
        while True:
            if self.touch_left.pressed() and self.touch_right.pressed():
                return True
            if stopwatch.time() > 3000:
                self.ev3.light.off()
                return False
    
    def say(self, words, color=Color.RED):
        self.ev3.light.on(color)
        self.ev3.speaker.say(str(words))
        self.ev3.light.off()
    
    def beep(self):
        self.ev3.speaker.beep()

    def get_color(self, time=1000):
        stopwatch = StopWatch()
        stopwatch.reset()
        self.ev3.light.on(Color.ORANGE)
        while True:
            if self.color_sensor.color() == Color.BLUE:
                self.ev3.light.off()
                return Color.BLUE
            if self.color_sensor.color() == Color.GREEN:
                self.ev3.light.off()
                return  Color.GREEN
            if self.color_sensor.color() == Color.YELLOW:
                self.ev3.light.off()
                return Color.YELLOW
            if self.color_sensor.color() == Color.RED:
                self.ev3.light.off()
                return Color.RED
            if stopwatch.time() > time:
                self.ev3.light.off()
                return None

    def drive_time(self, dist=100, time=1, ang=0):
        stopwatch = StopWatch()
        stopwatch.reset()
        while True:
            self.drive.drive(dist, ang)
            if stopwatch.time() > time:
                self.drive.drive.stop()
                break

    def drive_straight(self):
        self.drive.straight(222)
    
    def drive_backward(self):
        self.drive.straight(-222)

    def spin(self, angle):
        self.drive.turn(angle)

    def unload(self): # unload payload
        self.drive.stop()
        turn_rate = self.drive.settings()[2]
        turn_acceleration = self.drive.settings()[3]
        self.drive.settings(turn_rate=300, turn_acceleration=2000)
        self.drive.turn(25)
        self.drive.turn(-25)
        self.drive.stop()
        self.drive.settings(turn_rate=turn_rate, turn_acceleration=turn_acceleration)

    def driveTillObst(self, speed):
        while True:
            self.drive.drive(speed)
            if self.obstacle_sensor.distance() <= 45:
                self.drive.stop()

    """
    The following are for navigating the enviornment. 
    Orientations are with respect to 0,0 with agent facing 3,0
    Orienation code:
    f = forward facing
    b = backward facing
    l = left facing
    r = right facing

    Action_code:
    0 = forward
    1 = backward
    2 = left
    3 = right
    """
    def go_foward(self):
        if (self.agent_pos[0]+1) >= (len(self.env)): return
        else:
            if self.orientation == "f":  
                self.agent_pos[0] += 1
                self.drive_straight()
                return 
            elif self.orientation == "b":
                #self.spin(175)
                self.agent_pos[0] += 1
                self.drive_straight()
                self.orientation = 'f'
                return
            elif self.orientation == 'l':
                self.spin(-87)
                self.agent_pos[0] += 1
                self.drive_straight()
                self.orientation = 'f'
                return
            elif self.orientation == 'r':
                self.spin(87)
                self.agent_pos[0] += 1
                self.drive_straight()
                self.orientation = 'f'
                return
    
    def go_backward(self):
        if (self.agent_pos[0]-1) < 0: return
        else:
            if self.orientation == "b":  
                self.agent_pos[0] -= 1
                self.drive_backward()
                return 
            elif self.orientation == "f":
                #self.spin(180)
                self.agent_pos[0] -= 1
                self.drive_backward()
                self.orientation = 'b'
                return
            elif self.orientation == 'l':
                self.spin(-87)
                self.agent_pos[0] -= 1
                self.drive_backward()
                self.orientation = 'b'
                return
            elif self.orientation == 'r':
                self.spin(87)
                self.agent_pos[0] -= 1
                self.drive_backward()
                self.orientation = 'b'
                return
    
    def go_left(self):
        if (self.agent_pos[1]+1) >= len(self.env[0]): return
        else:
            if self.orientation == "l":  
                self.agent_pos[1] += 1
                self.drive_straight()
                return 
            elif self.orientation == "f":
                self.spin(87)
                self.agent_pos[1] += 1
                self.drive_straight()
                self.orientation = 'l'
                return
            elif self.orientation == 'b':
                self.spin(87)
                self.agent_pos[1] += 1
                self.drive_straight()
                self.orientation = 'l'
                return
            elif self.orientation == 'r':
                self.spin(172)
                self.agent_pos[1] += 1
                self.drive_straight()
                self.orientation = 'l'
                return

    def go_right(self):
        if (self.agent_pos[1]-1) < 0: return
        else:
            if self.orientation == "r":  
                self.agent_pos[1] -= 1
                self.drive_straight()
                return 
            elif self.orientation == "f":
                self.spin(-87)
                self.agent_pos[1] -= 1
                self.drive_straight()
                self.orientation = 'r'
                return
            elif self.orientation == 'b':
                self.spin(-87)
                self.agent_pos[1] -= 1
                self.drive_straight()
                self.orientation = 'r'
                return
            elif self.orientation == 'l':
                self.spin(172)
                self.agent_pos[1] -= 1
                self.drive_straight()
                self.orientation = 'r'
                return
        
    # Method to reset CHORE bot at start position
    def reset(self):
        self.agent_pos = [0,0]
        self.orientation = 'f'
        return 0 

    def alt_reset(self):
        self.agent_pos = [0,3]
        self.orientation = 'f'
        return 3 

    def get_state_from_pos(self):
        pos = (self.agent_pos[0], self.agent_pos[1])
        return self.env_state[pos]

    # Step function for agent. Moves agent and returns the new state of the agent; the reward from the env; and if done or not 
    def step(self, action):
        if action == 0:
            self.go_foward()
        elif action == 1:
            self.go_backward()
        elif action == 2:
            self.go_left()
        elif action == 3:
            self.go_right()
        
        reward = self.env[self.agent_pos[0]][self.agent_pos[1]]
        is_done = False
        for goal in self.goal_states:
            if self.agent_pos == goal:
                is_done = True
        
        next_state = self.get_state_from_pos()

        return next_state, reward, is_done