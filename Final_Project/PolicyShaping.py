import math, random, copy

def get_action(probs):
    p = random.random()
    sum_p=0
    for i in range(len(probs)):
        sum_p+=probs[i]
        if sum_p >= p:
            return i
    return None

def softmax(values, temp=0.3):
    values_denom = sum([math.exp(value/temp) for value in values])
    if values_denom < .001:
        values_denom = .001
    probs = []
    for value in values:
        probs.append(math.exp(value/temp)/values_denom)
    return probs

def ps_probs(feedback_table, confidence):
    fdbk_probs = []
    for i, action in enumerate(feedback_table):
        # sides of the binomial probability calculation
        left_side = confidence**action
        right_side_power = 0
        for j, other_actions in enumerate(feedback_table):
            if i != j:
                right_side_power += other_actions
        right_side = (1-confidence)**right_side_power
        fdbk_probs.append(left_side*right_side)
    return fdbk_probs

def get_shaped_action(q_table, feedback_table, state, confidence=0.8):
    q_actions = q_table[state]
    fdbck_actions = feedback_table[state]
    q_probs = softmax(q_actions)
    fdbck_probs = ps_probs(fdbck_actions, confidence)
    action_probs = [(q_probs[i]*fdbck_probs[i]) for i in range(len(q_probs))]
    action_probs_denom = sum(action_probs)
    action_probs = [(action_probs[i]/action_probs_denom) for i in range(len(action_probs))]
    return get_action(action_probs)

"""The following are methods for different ways of combining the feedback table of multiple users."""

# Combine feedback tables by simple summation
def naive_combine(user1_table, user2_table):
    combined_table = []
    for state in range(len(user1_table)):
        combined_table.append([])
        for (x, y) in zip(user1_table[state], user2_table[state]):
            combined_table[state].append(x+y)
    return combined_table

# Combine feedback tables by sumation with the parent_table being wieghted heigher 
def weighted_combine(child_table, parent_table, weight):
    combined_table = []
    for state in range(len(child_table)):
        combined_table.append([])
        for (x, y) in zip(child_table[state], parent_table[state]):
            combined_table[state].append(x+(weight*y))
    return combined_table

# If signs are different for users, the user with the higher status’s number is taken, else values are summed
def sign_combine(child_table, parent_table):
    combined_table = []
    for state in range(len(child_table)):
        combined_table.append([])
        for action in range(len(child_table[state])):
            if (child_table[state][action] * parent_table[state][action]) >= 0:
                combined_table[state].append(child_table[state][action]+parent_table[state][action])
            else:
                combined_table[state].append(parent_table[state][action])
    return combined_table