import random
class Q_table:
    def __init__(self, state_size, action_size, zeros=True, minqval=None, maxqval=None, qtable=None):
        """
        If zeros is set to False, then the q-table will be initiated with random values between 0 and 1. If min and
        max values are set, the table is filled with uniform distributed values between the min and max.
        """
        self.state_size = state_size
        self.action_size = action_size
        self.minqval = minqval
        self.maxqval = maxqval
        self.qtable = []
        if qtable is not None:
            self.qtable = qtable
        else:
            if zeros is True:
                for state in range(state_size):
                    self.qtable.append([0 for j in range(action_size)])

            elif minqval is None and maxqval is None and zeros is False:
                for state in range(state_size):
                    self.qtable.append([random.random() for j in range(action_size)])

            else:
                for state in range(state_size):
                    self.qtable.append([random.randint(minqval, maxqval) for j in range(action_size)])

    def get_qtable(self):
        return self.qtable

    def set_qtable(self, qtable):
        self.qtable = qtable

    def get_qval(self, state, action):
        """
        Returns the q-vlaue given a state acion pair.
        """
        try:
            return self.qtable[state, action]
        except IndexError:
            if action >= self.action_size:
                print("Index error: No such action.")

            elif state >= self.state_size:
                print("Index error: No such state.")

            elif state >= self.state_size and action >= self.action_size:
                print("Index error: No such state nor such action.")

    def set_qval(self, state, action, qval):
        """
        Assign a q-value to a state action pair.
        """
        try:
            self.qtable[state, action] = qval
        except IndexError:
            if action >= self.action_size:
                print("Index error: No such action.")
            elif state >= self.state_size:
                print("Index error: No such state.")
            elif state >= self.state_size and action >= self.action_size:
                print("Index error: No such state nor such action.")

    def optaction(self, state):
        """
        Returns the action associated with the highest q-value given a state
        """
        try:
            max_qval = max(self.qtable[state])
            return self.qtable.index(max_qval)
        except IndexError:
            print("Index error: No such state.")

    def maxq(self, state):
        """
        Returns the maximum q-value for a given state.
        """
        try:
            return self.qtable[state].index((max(self.qtable[state])))
        except IndexError:
            print("Index error: No such state.")