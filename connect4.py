import mcts
import sys
import random
if sys.version_info < (3, 0):
    input = raw_input

red = True
black = False

class ConnectFour(object):

    def __init__(self, player=red, columns=None, num_rows=6, num_columns=7, is_red=True, last_move=None):
        self.player = player
        if columns is not None:
            self.columns = columns
        else:
            self.columns = [[]] * num_columns
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.is_red = is_red
        self.last_move = last_move


    def get_actions(self):
        actions = []
        if not self.is_terminal():
            for i in range(self.num_columns):
                if len(self.columns[i]) < self.num_rows:
                    actions.append(i)
            return actions

    def get_successor(self, action):
        new_columns = [column[:] if i != action else column + [self.player] for i, column, in enumerate(self.columns)]
        return ConnectFour(not self.player, new_columns, self.num_rows, self.num_columns, self.is_red, action)

    def is_terminal(self):
        # check if board is full
        for column in self.columns:
            if len(column) != self.num_rows:
                break
        else:
            return True
## TODO REFACTOR THESE HACKS###################################################
        if self.last_move is not None:
            col = self.last_move
            row = len(self.columns[self.last_move]) - 1
            # check vertical
            if contiguous(self, row, col, 4, -1, 0):
                return True
            # check all horizontals
            elif any(contiguous(self, row, col - i, 4, 0, 1) for i in range(4)):
                return True
            elif any(contiguous(self, row - i, col - i, 4, 1, 1) for i in range(4)):
                return True
            elif any(contiguous(self, row + i, col - i, 4, -1, 1) for i in range(4)):
                return True
            else:
                return False

## END OF HACKS###################################################

        # check verticals:
        for column in self.columns:
            for row in range(len(column) - 3):
                if column[row] == column[row+1] == column[row+2] == column[row+3]:
                    return True

        # check horizontals:
        for row in range(self.num_rows):
            for col in range(self.num_columns - 3):
                #print col, self.columns
                if all(len(self.columns[i]) > row for i in range(col, col+4)):
                    if self.columns[col][row] == self.columns[col+1][row] == self.columns[col+2][row] == self.columns[col+3][row]:
                        return True

        # check / diagonals:
        for row in range(self.num_rows - 3):
            for col in range(self.num_columns - 3):
                if all(len(self.columns[c]) > r for r, c in line(row, col, 4, 1, 1)):
                    if all_equal(self.columns[c][r] for r, c in line(row, col, 4, 1, 1)):
                        return True
        # check \ diagonals:
        for row in range(3, self.num_rows):
            for col in range(self.num_columns - 3):
                if all(len(self.columns[c]) > r for r, c in line(row, col, 4, -1, 1)):
                    if all_equal(self.columns[c][r] for r, c in line(row, col, 4, -1, 1)):
                        return True

    def is_won(self):
        if self.is_red:
            target = red
        else:
            target = black

        # check verticals:
        for column in self.columns:
            for row in range(len(column) - 3):
                if column[row] == column[row+1] == column[row+2] == column[row+3] == target:
                    return True

        # check horizontals:
        for row in range(self.num_rows):
            for col in range(self.num_columns - 3):
                if all(len(self.columns[i]) > row for i in range(col, col+4)):
                    if self.columns[col][row] == self.columns[col+1][row] == self.columns[col+2][row] == self.columns[col+3][row] == target:
                        return True

        # check / diagonals:
        for row in range(self.num_rows - 3):
            for col in range(self.num_columns - 3):
                if all(len(self.columns[c]) > r for r, c in line(row, col, 4, 1, 1)):
                    if all(self.columns[c][r] == target for r, c in line(row, col, 4, 1, 1)):
                        return True
        # check \ diagonals:
        for row in range(3, self.num_rows):
            for col in range(self.num_columns - 3):
                if all(len(self.columns[c]) > r for r, c in line(row, col, 4, -1, 1)):
                    if all(self.columns[c][r] == target for r, c in line(row, col, 4, -1, 1)):
                        return True

        return False

    # slightly more efficient playouts
    def playout(self):
        temp_grid = [column[:] for column in self.columns]
        temp_last = self.last_move
        player = self.player
        while not self.is_terminal():
            move = random.choice(self.get_actions())
            self.columns[move].append(player)
            self.last_move = move
            player = not player
        winner = self.is_won()
        self.columns = temp_grid
        self.last_move = temp_last
        return winner


    def __str__(self):
        result = (' ' + '%d ' * self.num_columns) % tuple(range(1, self.num_columns+1)) + '\n'
        for row in reversed(range(self.num_rows)):
            result += '|'
            for col in range(self.num_columns):
                if len(self.columns[col]) > row:
                    if self.columns[col][row] == red:
                        result += 'O '
                    else:
                        result += 'X '
                else:
                    result += '. '
            result = result[:-1]
            result += '|\n'
        result += '+' + '-'*(2*self.num_columns-1) + '+'
        return result

def contiguous(board, row, col, length, row_delta, col_delta):
    if col < 0 or row < 0 or col >= board.num_columns or len(board.columns[col]) <= row:
        return False
    val = board.columns[col][row]
    for i in range(1, length):
        c = col + i * col_delta
        r = row + i * row_delta
        if not (c >= 0 and r >= 0 and c < board.num_columns and r < len(board.columns[c]) and board.columns[c][r] == val):
            return False
    return True

# http://stackoverflow.com/a/3844948
def all_equal(iterable):
    seq = list(iterable)
    return seq.count(seq[0]) == len(seq)

def line(row, col, length, row_delta, col_delta):
    return [(row + row_delta*i, col + col_delta*i) for i in range(length)]

def test_board(): 
    simple_board = ConnectFour(red, [[]] * 3 +  [[red, black]] + [[]] * 3, 6, 7, True)
    print mcts.best_move_iterations(simple_board, 1000)

def play():
    while True:
        seconds = float(input("How many seconds do I get per move? "))
        player = input("Do you want to play as o or x? (o goes first) ")
        if player == 'o':
            board = ConnectFour(red, is_red=False)
        else:
            board = ConnectFour(red, is_red=True)
            #move, iterations = mcts.best_move_time(board, seconds)
            board = board.get_successor(3)
        print board
        while not board.is_terminal():
            board = board.get_successor(int(input('Enter a column (1 indexed) ')) - 1)
            if board.is_terminal():
                break
            print board
            print "Thinking..."
            move, iterations = mcts.best_move_time(board, seconds)
            board = board.get_successor(move)
            print board
            print "After %d iterations, I played column %d" % (iterations, move+1)
        print board
        if board.is_won():
            print 'You lost!'
        else:
            print 'You won!'

if __name__ == '__main__':
    #test_board()
    play()

