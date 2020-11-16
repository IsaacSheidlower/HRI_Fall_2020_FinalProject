import random, math 

"""
User class to represent the human interacting with a CHORE bot.
user_ID is a color id and status is a number represnting their heirharchical authority. 
state_size and action_size define the enviornment.
"""
class User:
    def __init__(self, user_ID, state_size, action_size, status=0, username = "None"):
        self.user_ID = user_ID
        self.username = username
        self.state_size = state_size
        self.action_size = action_size
        self.status = status
        self.fdbck_table = [([0]*action_size) for state in range(state_size)]

    def get_feedback_table(self):
        return self.fdbck_table

    def set_feedback_table(self, feedback_table):
        self.fdbck_table = feedback_table
    
    def update_feedback_table(self, state, action, feedback):
        try: 
            self.fdbck_table[state][action] += feedback
        except:
            return IndexError