from __future__ import division
import math
import random
import time

def best_move_iterations(state, iterations):
    """returns the best move and time spent computing"""
    root = MonteCarloTreeNode(None, state)
    start = time.time()
    for _ in range(iterations):
        child = root.select()
        child.propogate(child.simulate())
    return root.play(), time.time() - start

def best_move_time(state, seconds):
    """returns the best move and number of mcts iterations computed"""
    start = time.time()
    root = MonteCarloTreeNode(None, state)
    iterations = 0
    while time.time() - start < seconds:
        child = root.select()
        child.propogate(child.simulate())
        iterations += 1
    return root.play(), iterations

def uct(parent_wins, parent_playouts, child_wins, child_playouts, exploration_parameter = math.sqrt(2)):
    return child_wins/child_playouts + exploration_parameter * math.sqrt(math.log(parent_playouts)/child_playouts)

class MonteCarloTreeNode(object):

    def __init__(self, parent, state, max=True):
        self.parent = parent
        self.state = state
        self.max = max
        self.wins = 0
        self.playouts = 0
        self.children = {}

    def select(self, selection_function=uct):
        if self.state.is_terminal():
            return self
        elif len(self.children) < len(self.state.get_actions()):
            actions = list(self.state.get_actions())
            random.shuffle(actions)
            for action in actions:
                if action not in self.children:
                    self.children[action] = MonteCarloTreeNode(self, self.state.get_successor(action), max=not self.max)
                    return self.children[action]
        else:
            return max(self.children.values(), key=lambda child: selection_function(self.wins, self.playouts, child.wins, child.playouts)).select(selection_function)

    def simulate(self):
        return self.state.playout()
        curr = self.state
        while not curr.is_terminal():
            curr = curr.get_successor(random.choice(curr.get_actions()))
        return curr.is_won()

    def propogate(self, won):
        self.playouts += 1
        if (won and not self.max) or (not won and self.max):
            self.wins += 1
        if self.parent is not None:
            self.parent.propogate(won)

    def play(self):
        for move in self.children:
            print '%d:    %5.2f%%    %4d/%d' % (move+1, 100*self.children[move].playouts / self.playouts, self.children[move].wins, self.children[move].playouts)
        print "        %4d/%d total" % (self.wins, self.playouts)
        return sorted(
            sorted(self.children.items(), key=lambda (action, child): child.wins), 
            key=lambda (action, child): child.playouts)[-1][0]

    def str_depth(self, depth, action=None):
        result = '-' * depth
        if action is not None:
            result += '%d: ' % action
        result +=  "(%d/%d)\n" % (self.wins, self.playouts)
        for action, child in self.children.items():
            result += child.str_depth(depth+1, action=action)
        return result

    def __str__(self):
        return self.str_depth(0)


