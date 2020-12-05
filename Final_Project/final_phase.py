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

import csv

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
    [5,0,0,5]
]

# Initialize CHORE bot
fam = Q_agent.Q_agent(ev3, drive, obstacle_sensor, color_sensor, touch_left, touch_right, 4, 4, env, goal_states=[[3,0], [3,3]])

state_size = len(env) * len(env[0])
action_size = 4
qtable = Q_table.Q_table(state_size, action_size)
qtable.set_qtable([[0.128259, -2.49579, -0.9717524750999997, -1.834937099999999], [0.7984907999999998, -2.49579, -0.9596463929999997, -0.3], [-0.2406299999999999, -2.117789999999999, 0.153, -0.657], [0.4281000000000001, -2.49579, -0.9, -0.3], [-0.5106299999999999, -0.3923999999999999, 0.03, -0.9], [-0.198, -0.657, 0.5153099999999999, 0.01530000000000001], [-0.657, -0.132, 1.169379, 0.03], [-0.83193, -0.51, -0.3293999999999999, 0.07200000000000001], [2.55, 0.24, -0.02999999999999999, 0], [-0.3, 0.5255999999999999, 0, 0], [0, -0.05099999999999999, -0.51, 0], [4.411754999999999, 0, -0.9, -0.3], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])

# Initialize users:
child = User.User(Color.RED, state_size, action_size, 1, "child") 
#parent = User.User(Color.GREEN, state_size, action_size, 2, "parent") 
parent = User.User(Color.GREEN, state_size, action_size, 1.5, "parent") 
no_user = User.User(Color.BLUE, state_size, action_size, 1)

child.set_feedback_table([[-3, 0, 5, 0], [-1, 0, 8, -1], [5, 0, 2, -3], [2, 0, 0, -1], [0, 2, 1, 0], [-3, 2, 0, 0], [2, -2, 2, -1], [1, -1, 0, -2], [0, 0, 0, 0], [-1, 2, 0, 0], [0, 1, 2, 0], [2, 0, 0, -1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
parent.set_feedback_table([[3, 0, -1, 0], [2, 0, 0, 0], [0, 0, 0, 0], [-1, 0, 0, 0], [5, -1, -1, 0], [0, -1, -1, 3], [0, 0, -1, 1], [0, -1, 0, 1], [2, -1, -1, 0], [0, -1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])

"""Type of PS feedback table combine:
Version 0 = naive
Version 1 = weighted combine
Version 2 = sign combine
"""
ps_version = 2


if ps_version == 0:
    no_user.set_feedback_table(PolicyShaping.naive_combine(child.get_feedback_table(), parent.get_feedback_table()))
    combined_fdbktable_data_0 = DataLog(name = "naive_combine", extension='csv', append=False)
    combined_fdbktable_data_0.log(no_user.get_feedback_table())
elif ps_version == 1:
    no_user.set_feedback_table(PolicyShaping.weighted_combine(child_table=child.get_feedback_table(), parent_table=parent.get_feedback_table(), weight=parent.status))
    combined_fdbktable_data_1 = DataLog(name = "weight_combine", extension='csv', append=False)
    combined_fdbktable_data_1.log(no_user.get_feedback_table())
elif ps_version == 2:
    no_user.set_feedback_table(PolicyShaping.sign_combine(child_table=child.get_feedback_table(), parent_table=parent.get_feedback_table()))
    combined_fdbktable_data_2 = DataLog(name = "sign_combine", extension='csv', append=False)
    combined_fdbktable_data_2.log(no_user.get_feedback_table())

episodes = 20
max_moves = 23 # Max agent moves per episode

# Q-learning parameters
learning = 0.3
discount = .9
exploration_rate = .00001
min_exploration = .0001
exploration_decay = .4

# policy shaping parameters:
confidence = .99  # confidence that feedback is optimal
likelihood = .5  # likelihood feedback is provided
const = 0.3  # constant used in probability of action equation

rewards = []
num_moves = []


data = DataLog('Episode #', 'Reward', "Time", "Num_feedbacks", "agent_pos", "is_done", \
                "username", name="ep_log", timestamp=True, extension='csv', append=False)

q_table_data = DataLog(name = "q_table", extension='csv', append=False)


episode_stopwatch = StopWatch()
episode_stopwatch.reset()

user = no_user


for episode in range(episodes):
    wait(8000)
    episode_stopwatch.reset
    fam.beep()
    #state = fam.reset()
    state = fam.alt_reset()
    is_done = False
    curr_reward = 0
    num_moves.append(0)
    num_feedbacks = 0 # Number of times the us gave feedback during the episode
    for move in range(max_moves):
        action = PolicyShaping.get_shaped_action(qtable.qtable, user.get_feedback_table(), state, confidence)
        next_state, reward, is_done = fam.step(action)
        if state != next_state:
            num_moves[episode] += 1
            if user is not no_user:
                feedback = fam.get_feedback()
                print(feedback)
                if feedback != 0:
                    num_feedbacks += 1
                wait(3000)
                user.update_feedback_table(state, action, feedback)
            if reward == 0 and is_done is False:
                reward = -1 # penalty for each move
        else: 
            print(move)
            move -= 1 # does not count as a move
            print(move)
            if reward == 0 and is_done is False:
                reward = -3 # penalty for trying to move out of bounds
        
        ep_time = episode_stopwatch.time()
        data.log(episode, curr_reward, ep_time, num_feedbacks, fam.agent_pos, is_done, user.username)
        print(state, action)
        qtable.qtable[state][action] = (1 - learning) * qtable.qtable[state][action] + learning * \
                                        (reward + discount * qtable.maxq(next_state))
        
        state = next_state
        curr_reward += reward
        print(qtable.qtable)
        if is_done:
            fam.unload()
            fam.say("Hooray!", color=Color.GREEN)
            break
    if not is_done:
        fam.say("Let's try again.")
    ep_time = episode_stopwatch.time()
    data.log(episode, curr_reward, ep_time, num_feedbacks, fam.agent_pos, is_done)
    episode_stopwatch.reset()
    rewards.append(curr_reward)
    user_session_is_done = fam.get_double_press() # Check if user is finished
    if not user_session_is_done:
        continue
    else:
        q_table_data.log(qtable.qtable)
        fam.say("Goodbye")