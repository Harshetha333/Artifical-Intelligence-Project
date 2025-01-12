'''


terminator_Baroque_Chess_module_staticEval.StopAsyncIteration

This file contains the static evaluation function used by our agent
to evaluate the state of a given board. It uses several heuristics
to score each board including:
    - which pieces remain
    - how many pieces are frozen
    - how "structured" are the pawns/pincers
    - how well-defended is the king

'''


from Baroque_Chess_state_etc import Baroque_Chess_state
import time

# given a barque state object evaluate the position of the board.
# WHITE is assumed to be the maximizing player and BLACK the minimizing

# Like in chess how we associate a given point value to each piece.
# the most basic form of understanding the position of the game
# Uses the piece number / 2 as the key and the piece value as the value
# 1 = Pincer, 2 = Coordinator, 3 = Leaperm 4 = imitator, 5 = withdrawer, 6 = King, 7 = Freezer
# 0 = EMPTY square
PIECE_VALUES = {0:0, 1:1, 2:5, 3:5, 4:5, 5:2, 6:100, 7:8}
weights = {'piece':5, 'freezing':3, 'withdraw':0, 'pinch':1, 'king_Def':1 }

DIAGONAL_MOVES = [(1,-1), (1,1), (-1,1), (-1,-1)]
ROOK_MOVES = [(0,1), (1,0), (-1,0), (0,-1)]
QUEEN_MOVES = ROOK_MOVES + DIAGONAL_MOVES

NUM_ROWS = 0
NUM_COLS = 0

def static_eval(board):
    global NUM_COLS, NUM_ROWS
    NUM_ROWS = len(board.board)
    NUM_COLS = len(board.board[0])

    white_score = 0
    black_score = 0
    black_king_alive = False
    white_king_alive = False

    for i, row in enumerate(board.board):
        for j, piece in enumerate(row):

            # do not need to do any calculations for empty square
            if piece == 0:
                continue

            ortho_neighbors = get_neighbors(board, i, j, ROOK_MOVES)
            diag_neighbors = get_neighbors(board, i, j, DIAGONAL_MOVES)
            all_neighbors = ortho_neighbors + diag_neighbors

            # find piece score: you get a better score if you have more pieces
            if piece % 2 == 0:
                black_score += weights['piece'] * PIECE_VALUES[piece // 2]
            else:
                white_score += weights['piece'] * PIECE_VALUES[piece // 2]

            # find freezing score: you get a better score if you have more enemy pieces frozen
            #                    your score is higher if you freeze higher valued pieces
            if piece == 14 or (piece == 8 and 15 in all_neighbors): # black freezer or black imitator acting as freezer
                black_score += weights['freezing'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 1 ])

            elif piece == 15 or (piece == 9 and 14 in all_neighbors):
                white_score += weights['freezing'] * sum([PIECE_VALUES[x // 2] for x in all_neighbors if x % 2 == 0 ])


            # find withdrawer score: higher score if withdrawer has a chance of capturing a good piece
            # i.e. counts the neighbors of a withdrawer where there is an empty square in opposite direction
#            elif piece == 10:
#                takeable_neighbors = check_withdrawer(board, i, j)
#                black_score += weights['withdraw'] * sum([PIECE_VALUES[x // 2] for x in takeable_neighbors if x % 2 == 1 ])
#
#            elif piece == 11:
#                takeable_neighbors = check_withdrawer(board, i, j)
#                white_score += weights['withdraw'] * sum([PIECE_VALUES[x // 2] for x in takeable_neighbors if x % 2 == 0 ])

            # Pawn/pincer structure: Give points if the pawns have lots of self pinching power: i.e. they lie in an open
            # line with another piece of theres, with at most one black piece between them
            elif piece == 2: # Black pincer
                black_score += weights['pinch'] * check_pincer(board, i, j)

            elif piece == 3: # white pincer
                white_score += weights['pinch'] * check_pincer(board, i, j)

        
            # check if king is well-defended. In this game, as most pieces capture by needing a line of site to the king
            # it will be beneficial if we have a few friendly pieces nearby and less enemy pieces
            elif piece == 12: # black king
                black_king_alive = True
                black_score += weights['king_Def'] * sum([1 for x in all_neighbors if x % 2 == 0]) # friendly pieces
                black_score -= weights['king_Def'] * sum([1 for x in all_neighbors if x % 2 == 1]) # enemy pieces

            elif piece == 13: # white king
                white_king_alive = True
                white_score += weights['king_Def'] * sum([1 for x in all_neighbors if x % 2 == 1]) # friendly pieces
                white_score -= weights['king_Def'] * sum([1 for x in all_neighbors if x % 2 == 0]) # enemy pieces

            
    if not black_king_alive:
        return 100000
    
    if not white_king_alive:
        return -100000

    return white_score - black_score

# Checks which pieces are in the neighboring squares directly adjacent to the given piece
# (the piece sitting at (i,j)) in the given directions
def get_neighbors(board, i, j, directions):

    neighbors = []

    for (dr, dc) in directions:
        new_row = i + dr
        new_col = j + dc
        if new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
            if board.board[new_row][new_col] != 0:
                neighbors.append(board.board[i + dr][j + dc])

    return neighbors

# checks for pieces sharing same row/col as pincer with a gap inbetween (i.e. defended territory)
# pieces must be at least two open squares apart for this to work
def check_pincer(board, i, j):
    pinching_count = 0
    for (dr, dc) in ROOK_MOVES:
        k = 1
        new_row = i + k*dr
        new_col = j + k*dc
        enemy_count = 0
        empty_squares = 0
        while new_row >= 0 and new_col >= 0 and new_row < NUM_ROWS and new_col < NUM_COLS:
            if board.board[new_row][new_col] == 0:
                empty_squares += 1
            elif board.board[new_row][new_col] % 2 != board.board[i][j] % 2: # enemy piece
                enemy_count += 1
            elif k > 2 and enemy_count < 2 and empty_squares > 0: # we already know its a friendly piece
                pinching_count += 1 
                break

            k += 1
            new_row = i + k*dr
            new_col = j + k*dc

    return pinching_count

def check_withdrawer(board, i, j):
    takeable_neighbors = []
    for (dr, dc) in QUEEN_MOVES:
        new_row = i + dr
        new_col = j + dc
        back_row = i - dr
        back_col = j - dc
        
        if new_col >= 0 and new_row >= 0 and new_col < NUM_COLS and new_row < NUM_ROWS and back_col >=0 and back_col < NUM_COLS and back_row >= 0 and back_row < NUM_ROWS:

            if board.board[new_row][new_col] != 0 and board.board[new_row][new_col] % 2 != board.board[i][j] % 2 and board.board[back_row][back_col] == 0:
                # if there is an enemy ahead and nothing behind me!
                takeable_neighbors.append(board.board[new_row][new_col])


    return takeable_neighbors
    

