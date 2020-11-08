#!/usr/bin/env pybricks-micropython
import copy
import itertools
import math, random
import time
from _thread import allocate_lock, start_new_thread
from threading import Thread

from pybricks.ev3devices import (ColorSensor, GyroSensor, InfraredSensor,
                                 Motor, TouchSensor, UltrasonicSensor)
from pybricks.hubs import EV3Brick
from pybricks.media.ev3dev import ImageFile, SoundFile
from pybricks.parameters import Button, Color, Direction, Port, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import DataLog, StopWatch, wait

import Q_agent, Q_table, User, PolicyShaping

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

def argmax(interable):
    return max(enumerate(interable), key=lambda x:x[1])[0]
    """
    argmax function taken from user wall-e on stack overflow at link:
    https://stackoverflow.com/questions/5098580/implementing-argmax-in-python
    """

# Create your objects here.
ev3 = EV3Brick()

right_motor = Motor(Port.B)
left_motor = Motor(Port.C)
wheel_diameter = 56
axle_track = 114

drive = DriveBase(left_motor, right_motor, wheel_diameter, axle_track)

obstacle_sensor = UltrasonicSensor(Port.S4)
color_sensor = ColorSensor(Port.S2)
touch_left =  TouchSensor(Port.S3)
touch_right = TouchSensor(Port.S1)

ev3.speaker.set_speech_options(voice='m5', speed=None, pitch=None)

# Initialize enviornment:
env = [
    [0,0,0,0],
    [0,0,0,0],
    [0,0,0,0],
    [0,0,0,5]
]

# Initialize CHORE bot
fam = Q_agent.Q_agent(ev3, drive, obstacle_sensor, color_sensor, touch_left, touch_right, 4, 4, env)

state_size = len(env) * len(env[0])
action_size = 4
qtable = Q_table.Q_table(state_size, action_size)

# Initialize user:
child = User.User(Color.RED, state_size, action_size, 0) 

episodes = 20
max_moves = 30 # Max agent moves per episode

# Q-learning parameters
learning = 0.1
discount = .9
exploration_rate = 1
min_exploration = .001
exploration_decay = .1

# policy shaping parameters:
confidence = .9  # confidence that feedback is optimal
likelihood = .5  # likelihood feedback is provided
const = 0.3  # constant used in probability of action equation

rewards = []
num_moves = []


data = DataLog('Episode #', 'Reward', "Time", "Num_feedbacks", "agent_pos", "is_done", name="ep_log", timestamp=True, extension='csv', append=False)

episode_stopwatch = StopWatch()
episode_stopwatch.reset()

for episode in range(episodes):
    wait(10000)
    episode_stopwatch.reset
    fam.beep()
    state = fam.reset()
    is_done = False
    curr_reward = 0
    num_moves.append(0)
    num_feedbacks = 0 # Number of times the us gave feedback during the episode

    for move in range(max_moves):
        if random.random() > exploration_rate:
            action = PolicyShaping.get_shaped_action(qtable.qtable, child.get_feedback_table(), state, confidence)
        else:
            action = random.randint(0, action_size-1)

        num_moves[episode] += 1
        next_state, reward, is_done = fam.step(action)
        if state != next_state:
            feedback = fam.get_feedback()
            print(feedback)
            if feedback != 0:
                num_feedbacks += 1
            wait(3000)
            child.update_feedback_table(state, action, feedback)
            if reward == 0 and done is False:
                reward = -1 # penalty for each move
        else: 
            if reward == 0 and done is False:
                reward = -3 # penalty for trying to move out of bounds
        
        ep_time = episode_stopwatch.time()
        data.log(episode, curr_reward, ep_time, num_feedbacks, fam.agent_pos, is_done)
        print(state, action)
        qtable.qtable[state][action] = (1 - learning) * qtable.qtable[state][action] + learning * \
                                        (reward + discount * qtable.maxq(next_state))
        
        state = next_state
        curr_reward += reward

        if is_done:
            fam.say("Hooray!")
            break
    if not is_done:
        fam.say("Let's try again.")
    ep_time = episode_stopwatch.time()
    data.log(episode, curr_reward, ep_time, num_feedbacks, fam.agent_pos, is_done)
    episode_stopwatch.reset()
    rewards.append(curr_reward)
    # Exponential decay of exploration rate:
    exploration_rate = min_exploration + (1 - min_exploration) * math.exp(-exploration_decay * episode)


"""

#fam.go_backward()
fam.agent_pos = [2,3]
fam.go_foward()
print(fam.orientation, fam.agent_pos)
fam.go_left()
print(fam.orientation, fam.agent_pos)
fam.go_right()
print(fam.orientation, fam.agent_pos)

fam.go_backward()
print(fam.orientation, fam.agent_pos)

#fam.go_left()

global_reward = 0
next_state, reward, is_done = fam.step(0)
global_reward+=reward
print(next_state, reward, is_done, fam.agent_pos, global_reward)
next_state, reward, is_done = fam.step(1)
global_reward+=reward
print(next_state, reward, is_done, fam.agent_pos, global_reward)
next_state, reward, is_done = fam.step(2)
global_reward += reward
print(next_state, reward, is_done, fam.agent_pos, global_reward)
next_state, reward, is_done = fam.step(3)
global_reward+=reward
print(next_state, reward, is_done, fam.agent_pos, global_reward)"""
