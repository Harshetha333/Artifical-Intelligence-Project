'''


terminator_Baroque_Chess_module_validStates.py

Given a Baroque_Chess_State board for a Baroque Chess Game, this returns all the possible
moves for the player whose turn it currently is. It assumes a few things about the rules
of the game
    
    - Leapers can only jump one piece at a time
    - Imitators can freeze Freezers (and adjacent pieces) but the two do NOT cancel out
    - King can move into check
    - Imitators can only capture as one type of piece per move
    - No "suicide" moves where frozen pieces sacrifice themselves in place of a move

This method acts as a python generator, returning valid moves one at a time.

'''
# given a current Baroque Board, returns a generator which generates all the 
# valid move for the player whose turn it currently is
WHITE = 1
BLACK = 0

# NOTE: set to a non-integer value so that EMPTY % 2 != WHITE or BLACK
EMPTY = 0.5

QUEEN_MOVES = [(1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,-1), (1, -1), (-1,1)]
ROOK_MOVES = [(1,0), (0,1), (-1,0), (0,-1)]

NUM_ROWS = 0
NUM_COLS = 0

from Baroque_Chess_state_etc import Baroque_Chess_state

# For testing!
from Baroque_Chess_state_etc import parse
import time
import traceback

def valid_moves(current_board):

    # NOTE: deals with the annoying fact that the empty squares are the same as the black squar)es % 2
    # This allow for convenient checks using PIECE % 2 == whose_move to check that a given piece matches
    # the color of the player whose turn it is (or use != to check that the color is opposite) rather than
    # breaking down into a bunch of if WHITE else if BLACK statements.
    global NUM_COLS, NUM_ROWS
    NUM_ROWS = len(current_board.board)
    NUM_COLS = len(current_board.board[0])

    board = Baroque_Chess_state(current_board.board, current_board.whose_move)
    for i, row in enumerate(board.board):
        for j, square in enumerate(row):
            if square == 0: board.board[i][j] = EMPTY

    whose_move = board.whose_move
    
    


    for i, row in enumerate(board.board):
        for j, square in enumerate(row):
            position = (i,j)
            if square != EMPTY and square % 2 == whose_move and no_freezer_near(board, position):
                # pincer
                if square in [2,3]:
                    # print("pincer moves (start, end)")
                    for move in pincer_moves(board, position): yield move

                # coordinator
                elif square in [4,5]:
                    # print("coordinator moves (start, end)")
                    for move in coordinator_moves(board, position): yield move
                
                # leaper
                elif square in [6,7]:
                    # print("leaper moves (start, end)")
                    for move in leaper_moves(board, position): yield move

                # imitator
                elif square in [8,9]:
                    # print("imitator moves (start, end)")
                    for move in imitator_moves(board, position): yield move

                # withdrawer
                elif square in [10,11]:
                    # print("withdrawer moves (start, end)")
                    for move in withdrawer_moves(board, position): yield move

                # king
                elif square in [12,13]:
                    # print("king moves (start, end)")
                    for move in king_moves(board, position): yield move

                # freezer
                else:
                    # print("freezer Moves (start, end)")
                    for move in freezer_moves(board, position): yield move

# generate a new board object by moving the piece at 'position' to 'new_position'
def make_move(board, position, new_position):

    # make a new board
    new_board = Baroque_Chess_state(board.board, board.whose_move)

    # move the piece to its new square
    new_board.board[new_position[0]][new_position[1]] = new_board.board[position[0]][position[1]] 
    new_board.board[position[0]][position[1]] = EMPTY
    return new_board

# change all the EMPTY values back to zero
# all, changes whose turn it is so the board is ready to be returned
def revert_empty(board):
    for i, row in enumerate(board.board):
        for j, square in enumerate(row):
            if square == EMPTY:
                board.board[i][j] = 0

    board.whose_move = 1 - board.whose_move



def pincer_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in ROOK_MOVES:
        k = 1
        new_row = row + k*dr
        new_col = col + k*dc
        # had to add this condition because python allows negative indexing (i.e. list[-1])
        while new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
            # if the square is empty (and all squares leading up to it by the else clause)
            # then it is a valid move
            if board.board[new_row][new_col] == EMPTY:
                
                new_position = (new_row, new_col)
                # print(new_position)
                
                yield pincer_captures(board, position, new_position)

                k+=1
                new_row = row + k*dr
                new_col = col + k*dc
            else:
                # found an enemy or friendly piece that it cannot jump over/move past
                break


def pincer_captures(board, position, new_position, make_move_and_revert=True):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    if make_move_and_revert:
        new_board = make_move(board, position, new_position)
    else:
        new_board = board

    nrow = new_position[0]
    ncol = new_position[1]
    
    for (dr, dc) in ROOK_MOVES:
        # dr is change in row
        # dc is change in column
            # if theres a matching colored piece 2 steps away and an enemy one step away in this direction
        if nrow + 2*dr >= 0 and nrow + 2*dr < NUM_ROWS and ncol + 2*dc >= 0 and ncol + 2*dc < NUM_COLS and new_board.board[nrow][ncol] % 2 == new_board.board[nrow + 2*dr][ncol + 2*dc] % 2 and new_board.board[nrow][ncol] % 2 != new_board.board[nrow + dr][ncol + dc] % 2:
            new_board.board[nrow + dr][ncol + dc] = EMPTY


    if make_move_and_revert: revert_empty(new_board)
    return new_board



def coordinator_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        new_row = row + k*dr
        new_col = col + k*dc
        while new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
            # if the square is empty (and all squares leading up to it by the else clause)
            # then it is a valid move
            if board.board[row + k*dr][col + k*dc] == EMPTY:
                new_position = (row + k*dr, col + k*dc)
                yield coordinator_captures(board, position, new_position)
                k += 1
                new_row = row + k*dr
                new_col = col + k*dc
            else:
                # square has an enemy or friendly piece. Cannot jumpy over these
                break

def coordinator_captures(board, position, new_position, make_move_and_revert=True):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    if make_move_and_revert:
        new_board = make_move(board, position, new_position)
    else:
        new_board = board

    nrow = new_position[0]
    ncol = new_position[1]

    # find the kings location
    for i, row in enumerate(new_board.board):
        for j, piece in enumerate(row):
            if piece in [12, 13] and piece % 2 == new_board.whose_move:
                king_row = i
                king_col = j

                # if there is an enemy piece at the intersection of coordinator row and king column, capture it
                if new_board.board[nrow][king_col] % 2 != new_board.whose_move:
                    new_board.board[nrow][king_col] = EMPTY

                # if there is an enemy piece at the intersection of coordinator row and king column, capture it
                if new_board.board[king_row][ncol] % 2 != new_board.whose_move:
                    new_board.board[king_row][ncol] = EMPTY

                break
                
    if make_move_and_revert: revert_empty(new_board)
    return new_board

def leaper_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]
    whose_move = board.whose_move

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        enemy_count = 0
        new_row = row + k*dr
        new_col = col + k*dc
        while new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
            # can hop over at most one enemy
            if enemy_count > 1:
                break

            # empty square; possible move
            elif board.board[new_row][new_col] == EMPTY:
                new_position = (new_row, new_col)
                yield leaper_captures(board, position, new_position, (dr, dc), k)

            # cannot jump over pieces on the same team
            elif board.board[row + k*dr][col + k*dc] % 2 == whose_move:
                break

            # square contains an enemy piece
            else:
                enemy_count += 1

            k += 1
            new_row = row + k*dr
            new_col = col + k*dc


def leaper_captures(board, position, new_position, direction, steps, make_move_and_revert=True):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    if make_move_and_revert:
        new_board = make_move(board, position, new_position)
    else:
        new_board = board

    row = position[0]
    col = position[1]
    dr = direction[0] 
    dc = direction[1]
        
    for k in range(1, steps):
        # dont have to worry about capturing a piece of the same color because
        # it would not be a valid move to jumpy over a teammate
        new_board.board[row + k*dr][col + k*dc] = EMPTY


    if make_move_and_revert: revert_empty(new_board)
    return new_board

def imitator_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''    
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        new_row = row + k*dr
        new_col = col + k*dc
        already_jumped = False
        capture_as = 'other'

        while new_col >= 0 and new_row >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
            new_square = board.board[new_row][new_col]
            new_position = (new_row, new_col)

            # if the square is empty (and all squares leading up to it by the else clause)
            # then it is a valid move
            # NOTE: this could be capturing as either a leaper OR an 'other' depending on capture_as
            if new_square == EMPTY:
                for move in imitator_captures(board, position, new_position, (dr, dc), k, capture_as):
                    yield move
                k += 1

            # if its the opposite teams king, ONLY a step away, acts as a king and captures it.
            elif k == 1 and new_square in [12, 13] and new_square % 2 != board.whose_move: 
                for move in imitator_captures(board, position, new_position, (dr, dc), k, capture_as='king'):
                    yield move
                break

            elif not already_jumped and new_square in [6,7] and new_square % 2 != board.whose_move:
                # can jump over it        
                k += 1
                capture_as = 'leaper'
                already_jumped = True
            else:
                # square has an enemy or friendly piece. Cannot jumpy over these
                break

            new_row = row + k*dr
            new_col = col + k*dc



def imitator_captures(board, position, new_position, direction, steps, capture_as):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    
    '''
    row = position[0]
    col = position[1]
    nrow = new_position[0]
    ncol = new_position[1]
    dr = direction[0]
    dc = direction[1]
    any_captures_made = False # in the case no captures are made, we still want to return a board.

    # simply making the move will take care of the king capture if necessary
    if capture_as == 'king':
        new_board = make_move(board, position, new_position)
        revert_empty(new_board)
        yield new_board
        return # exit the generator; already capturing as a king cannot capture as another piece

    # take care of leaper captures
    # in this case, since the only way to jump over a piece is if we noticed it was a leaper,
    # we dont have to check any further conditions
    elif capture_as == 'leaper':
        new_board = make_move(board, position, new_position)
        leaper_captures(new_board, position, new_position, direction, steps, make_move_and_revert=False)
        revert_empty(new_board)
        yield new_board
        return # exit the generator and stop iterating

    # take care of withdrawer captures: only captures withdrawer
    elif capture_as == 'other':
        capture_made = False
        new_board = make_move(board, position, new_position)
        if row - dr >= 0 and row - dr < NUM_ROWS and col - dc  >= 0 and col - dc < NUM_COLS and new_board.board[row - dr][col - dc] in [10, 11] and new_board.board[row - dr][col - dc] % 2 != board.whose_move:
            new_board.board[row - dr][col - dc] = EMPTY
            capture_made = True

        # NOTE: ONLY return if captures are made in order to prevent unnecessarily expanding state tree. i.e. dont want
        # to have a state for capturing as a withdrawer, a state for capturing as a coordinator, etc when all of them dont
        # capture anything and generate identical states.
        if capture_made:
            revert_empty(new_board)
            yield new_board
            # reset board for next possible capture type
            new_board = make_move(board, position, new_position)
            any_captures_made = True


        # take care of pincher captures
        capture_made = False
        for (dr, dc) in ROOK_MOVES:
            # dr is change in row
            # dc is change in column

            # if theres a matching colored piece 2 steps away and an enemy one step away in this direction
            # also, the piece being captured must be a pincher
            if nrow + 2*dr >= 0 and nrow + 2*dr < NUM_ROWS and ncol + 2*dc >= 0 and ncol + 2*dc  < NUM_COLS and \
                    new_board.board[nrow][ncol] % 2 == new_board.board[nrow + 2*dr][ncol + 2*dc] % 2 and new_board.board[nrow][ncol] % 2 != new_board.board[nrow + dr][ncol + dc] % 2 and new_board.board[nrow + dr][ncol + dc] in [2,3]:

                new_board.board[nrow + dr][ncol + dc] = EMPTY
                capture_made = True

        if capture_made:
            revert_empty(new_board)
            yield new_board
            # reset board for next move type
            new_board = make_move(board, position, new_position)
            any_captures_made = True


        # take care of coordinator captures
        capture_made = False
        for i, row in enumerate(new_board.board):
            for j, piece in enumerate(row):
                if piece in [12, 13] and piece % 2 == new_board.whose_move:
                    # find kings location
                    king_row = i
                    king_col = j

                    # if there is an enemy piece at the intersection of coordinator row and king column, capture it
                    if new_board.board[nrow][king_col] in [4,5] and new_board.board[nrow][king_col] % 2 != new_board.whose_move:
                        new_board.board[nrow][king_col] = EMPTY
                        capture_made = True

                    # if there is an enemy piece at the intersection of coordinator row and king column, capture it
                    if new_board.board[king_row][ncol] in [4,5] and new_board.board[king_row][ncol] % 2 != new_board.whose_move:
                        new_board.board[king_row][ncol] = EMPTY
                        capture_made = True

                    break

        if capture_made:
            revert_empty(new_board)
            yield new_board
            any_captures_made = True

        # if no moves result in a capture (regardless of which piece we are imitating) we still want to return
        # at least one move: the move that just changes the square of the imitator.
        if not any_captures_made:
            revert_empty(new_board)
            yield new_board


def withdrawer_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        new_row = row + k*dr
        new_col = col + k*dc
        while new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
                # if the square is empty (and all squares leading up to it by the else clause)
                # then it is a valid move
                if board.board[new_row][new_col] == EMPTY:
                    new_position = (new_row, new_col)
                    yield withdrawer_captures(board, position, new_position, (dr, dc))
                    k += 1
                    new_row = row + k*dr
                    new_col = col + k*dc
                else:
                    # square has an enemy or friendly piece. Cannot jumpy over these
                    break

def withdrawer_captures(board, position, new_position, direction, make_move_and_revert=True):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)
    direction = the direction the piece is moving in (dr, dc)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''

    if make_move_and_revert:
        new_board = make_move(board, position, new_position)
    else:
        new_board = board

    row = position[0]
    col = position[1]
    dr = direction[0]
    dc = direction[1]

    if row - dr >= 0 and row - dr < NUM_ROWS and col - dc >= 0 and col - dc < NUM_COLS and new_board.board[row - dr][col - dc] % 2 != new_board.whose_move:
        new_board.board[row - dr][col - dc] = EMPTY

    if make_move_and_revert: revert_empty(new_board)
    return new_board

    
def king_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    whose_move = board.whose_move
    row = position[0]
    col = position[1]
    
    for (dr, dc) in QUEEN_MOVES:
        # whose move = 1 for white and % 2 == 1 for white pieces
        # whose move = 0 for black and % 2 == EMPTY for black pieces
        # i.e. king can move as long as there isnt a friendly piece there
        if row + dr >= 0 and col + dc >= 0 and row + dr < NUM_ROWS and col + dc < NUM_COLS and board.board[row + dr][col + dc] % 2 != whose_move:
            yield king_captures(board, position, (row + dr, col + dc))

def king_captures(board, position, new_position, make_move_and_revert=True):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    # since the king captures by occupying the square, all we have to do is move the king
    # to his new square.

    if make_move_and_revert:
        new_board = make_move(board, position, new_position)
    else:
        new_board = board

    if make_move_and_revert: revert_empty(new_board) 
    return new_board
    
def freezer_moves(board, position):
    '''
    board = current board before move has been made
    position = position of the piece to be moved on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    row = position[0]
    col = position[1]

    for (dr, dc) in QUEEN_MOVES:
        k = 1
        new_row = row + k*dr
        new_col = col + k*dc
        while new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
                # if the square is empty (and all squares leading up to it by the else clause)
                # then it is a valid move
                if board.board[row + k*dr][col + k*dc] == EMPTY:
                    new_position = (row + k*dr, col + k*dc)
                    yield freezer_captures(board, position, new_position)
                    k += 1
                    new_row = row + k*dr
                    new_col = col + k*dc
                else:
                    # square has an enemy or friendly piece. Cannot jump over these
                    break

def freezer_captures(board, position, new_position):
    '''
    board = current board before move has been made
    position = old position of the piece on the board (row, col)
    new_position = new location of piece on the board (row, col)

    returns: 
        new_board = new board object where given piece has been moved and all captures have been made
    '''
    # since the freezer does not capture, we just move it to its new square.
    new_board = make_move(board, position, new_position)
    revert_empty(new_board) 
    return new_board




# returns True if there is no adjacent freezer.
# Flag is to help in the case of a nearby imitator to prevent further rounds of recursion
# i.e. if there is in imitator nearby, it could be acting as a freezer so I have to check if a freezer
# is nearby that imitator. I wouldn't want a chain of imitators to cause this to recurse more than one 
# level as imitators CANNOT imitate themselves, so I stop that from happening with one flag
# NOTE: assumes immitators and freezers do NOT cancel out
def no_freezer_near(board, position, flag=False):
    whose_move = board.whose_move

    if flag: whose_move = 1-whose_move

    adj_squares = [(i,j) for i in range(max(0, position[0]-1), min(NUM_ROWS, position[0] + 2)) for j in range(max(0, position[1] - 1), min(NUM_COLS, position[1] + 2))]
    adj_squares.remove(position)

    for square in adj_squares:
        piece = board.board[square[0]][square[1]]
        if whose_move == WHITE:
            if piece == 14: return False

            # NOTE: checks if there is an imitator acting as a freezer nearby
            elif piece == 8 and not flag and not no_freezer_near(board,square, flag=True): return False 
        else:
            if piece == 15: return False

            # NOTE: checks if there is an imitator acting as a freezer nearby
            elif piece == 9 and not flag and not no_freezer_near(board,square, flag=True): return False 

    return True

# ===================================== TESTING CODE
# INITIAL = parse('''
# c l i w k i l f
# p p p p p p p p
# - - - - - - - -
# - - - - - - - -
# - - - - - - - -
# - - - - - - - -
# P P P P P P P P
# F L I W K I L C
# ''')


# test imitator
# INITIAL = parse('''
#- - - - - - - -
#- - - - C - - -
#- - k - p f - -
#- w I - - p P -
#- - - - p f - -
#- - l - P - - -
#- - - - - - - -
#- - - - - - - -
#''')

#INITIAL = parse('''
#- - - - - - - -
#- - - - - k - -
#- - - - F - - -
#- - - - - - - -
#- - - - - - - -
#- - - - - - - -
#- - - - - - - -
#- - - - - - - -
#''')


# NOTE: Testing notes
# Pincer
#   Pincer can capture single piece in direction of motion
#   Pincer can capture multiple pieces
#   Pincer cannot move through other pieces
#   Pincer does not capture teamates
#  Pincer does not capture without a teammate on the opposite side of piece

#initial_board = Baroque_Chess_state(INITIAL)
#initial_board.whose_move = BLACK
#print("INTIAL BOARD \n\n")
#print(initial_board)
# # print(initial_board.board)

# # start = time.time()

#for i in range(1):
#    for move in valid_moves(initial_board): 
#        print(move) 

# print("done!")
# print("runtime: ", time.time() - start)
