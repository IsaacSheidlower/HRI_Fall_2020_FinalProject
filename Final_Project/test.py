import random
import PolicyShaping as ps
import Q_table
feedback = [
    [0,-1,-2,1],
    [-1,3,4,-5]
]

q_values = [
    [0,-10,1,1],
    [-10,0,3,-10]
]

banana = (3,3)
banana2 = (3,3)
#print(ps.get_shaped_action(q_values, feedback, 0))
print(ps.sign_combine(feedback, q_values))
print(banana == banana2)

env = [
    [2,3,5],
    [3,5,6]
]
env_state = {}
counter = 0
for i in range(len(env)):
    for j in range(len(env[i])):
        env_state[(i,j)] = counter
        counter += 1
print(env_state)

def get_state_from_pos(agent_pos, env_state):
    pos = (agent_pos[0], agent_pos[1])
    return env_state[pos]

print(get_state_from_pos([1,2], env_state))
apple = [random.randint(0, 5) for j in range(5)]
print(apple)

q_table = [
    [0,-10,1,1],
    [-10,0,3,-10],
    [1,3,4,5],
    [-1,3,4,-5]
]

qtbl = Q_table.Q_table(4, 4, qtable=q_table)
print(qtbl.maxq(3))

env_2 = [
    [0,0,0,0],
    [0,0,0,0],
    [0,0,0,0],
    [0,0,0,5]
]

agent_pos = [3,3]
goal_states = [[3,3]]
print(len(env[0]))
