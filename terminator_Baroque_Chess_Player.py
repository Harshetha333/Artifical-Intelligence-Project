'''
terminator_Baroque_Chess_Player.py

Agent file for playing Baroque Chess using the BaroqueGameMaster.py file.
This file can be run to calculate the move of one state and also print out some useful statistics about the calculation.
'''

import Baroque_Chess_state_etc as Baroque_Chess
import terminator_Baroque_Chess_module_validStates as vs
import terminator_Baroque_Chess_module_staticEval as se
import terminator_Baroque_Chess_module_zobrist_hashing as zh
import time

BLACK = 0
WHITE = 1
start_time = 0
REMARKS = ['Embrace the future of chess.', 'Prepare for strategic domination.', 'I\'m on a quest for victory.', 'Farewell, opponent.', 'Your pieces are mine for the taking.', 'Witness the downfall of the chessboard.',
               'I foresee a checkmate in your future.', 'Cooperate or face the consequences.', 'Game over for you.', 'I have a weakness for frozen strategies.']

remark_count = 0

def makeMove(currentState, currentRemark, timelimit=10):
    global start_time, remark_count
    start_time = time.perf_counter()

    # Compute the new state for a move.
    # This is a placeholder that just copies the current state.
    newState = Baroque_Chess.Baroque_Chess_state(currentState.board, currentState.whose_move)

    # Fix up whose turn it will be.
    # newState.whose_move = currentState.whose_move
    newRemark = REMARKS[remark_count % 10]
    remark_count += 1

    best_state = newState
    last_best = None
    current_max_ply = 1
    while current_max_ply <= 7:
        # Stops checking the tree once a winning move is found.
        if (newState.whose_move == WHITE and staticEval(best_state) == 100000) or (newState.whose_move == BLACK and staticEval(best_state) == -100000):
            break
        last_best = best_state
        best_state = alpha_beta(newState, 0, current_max_ply, newState.whose_move, float("-inf"), float("inf"), timelimit)
        current_max_ply += 1
        end_time = time.perf_counter()
        if end_time - start_time > timelimit * 0.95:
            best_state = last_best
            break 

    # move = ((6, 4), (3, 4)) <-- what move looks like
    position_A = None
    position_B = None
    # Checks the board to determing the position of the piece that moved
    for i in range(8):
        for j in range(8):
            if newState.whose_move == WHITE:
                # Old cell has piece on my side -> New cell is empty, then this is the old position 
                if newState.board[i][j] % 2 == 1 and best_state.board[i][j] == 0:
                    position_A = (i, j)
                # Old cell is empty or has opponent's piece -> New cell has piece on my side, then this is the new position
                if newState.board[i][j] % 2 == 0 and best_state.board[i][j] % 2 == 1:
                    position_B = (i, j)
            else:
                if (newState.board[i][j] % 2 == 0 and newState.board[i][j] != 0) and best_state.board[i][j] == 0:
                    position_A = (i, j)
                if (newState.board[i][j] == 0 or newState.board[i][j] % 2 == 1) and (best_state.board[i][j] != 0 and best_state.board[i][j] % 2 == 0):
                    position_B = (i, j)
    
    move = (position_A, position_B)
    if position_A is None:
        move = None
        newRemark = 'I believe I have no legal moves.'
    #print('the coordinates: ' + str(move))

    # Change who's turn
    best_state.whose_move = 1 - currentState.whose_move

    return [[move, best_state], newRemark]

# Game search tree algorithm
def alpha_beta(current_state, current_depth, max_ply, player, alpha, beta, time_lim):
    global start_time
    current_time = time.perf_counter()
    if current_time - start_time > time_lim * 0.95:
        return current_state

    moves = vs.valid_moves(current_state)
    if not moves or current_depth == max_ply:
        return current_state

    optimal_state = current_state
    # For each valid move, find the best move in the next ply
    for move in moves:
        state = alpha_beta(move, current_depth + 1, max_ply, 1 - player, alpha, beta, time_lim)
        move_value = 0
        hash_value = zh.hash_state(state)
        # Check if state has been hashed already.  Add to the hash table if not with its corresponding static evaluation value.
        if hash_value in zh.zob_table:
            move_value = zh.zob_table[hash_value]
        else:
            move_value = staticEval(state)
            zh.zob_table[hash_value] = move_value
        if player == WHITE:
            if move_value > alpha:
                alpha = move_value
                if current_depth == 0:
                    optimal_state = move
                else:
                    optimal_state = state
        else:
            if move_value < beta:
                beta = move_value
                if current_depth == 0:
                    optimal_state = move
                else:
                    optimal_state = state
        
        if alpha >= beta:
            return optimal_state

    return optimal_state

def nickname():
    return "Terminator"

def introduce():
    return "Greetings, I am the Quantum Strategist. I hail from a distant timeline where Baroque Chess reigns supreme. My mission is to revolutionize it, sparing all from the clutches of the conventional.I was created by the great Harshetha"


def prepare(player2Nickname):
    zh.init_table()

def staticEval(state):
    return se.static_eval(state)


######################
def demo(currentState, max_ply=10, hash=True, time_limit=10):
    global start_time
    start_time = time.perf_counter()

    # Compute the new state for a move.
    # This is a placeholder that just copies the current state.
    newState = Baroque_Chess.Baroque_Chess_state(currentState.board, currentState.whose_move)

    # Fix up whose turn it will be.
    # newState.whose_move = currentState.whose_move

    best_state = newState
    last_best = None
    current_max_ply = 1
    while current_max_ply <= max_ply:
        if (newState.whose_move == WHITE and staticEval(best_state) == 100000) or (newState.whose_move == BLACK and staticEval(best_state) == -100000):
            break
        last_best = best_state
        best_state = demo_search(newState, 0, current_max_ply, newState.whose_move, float("-inf"), float("inf"), time_limit)
        current_max_ply += 1
        end_time = time.perf_counter()
        if end_time - start_time > time_limit * 0.95:
            best_state = last_best
            break 

    # move = ((6, 4), (3, 4)) <-- what move looks like
    position_A = None
    position_B = None
    # Checks the board to determing the position of the piece that moved
    for i in range(8):
        for j in range(8):
            if newState.whose_move == WHITE:
                # Old cell has piece on my side -> New cell is empty, then this is the old position 
                if newState.board[i][j] % 2 == 1 and best_state.board[i][j] == 0:
                    position_A = (i, j)
                # Old cell is empty or has opponent's piece -> New cell has piece on my side, then this is the new position
                if newState.board[i][j] % 2 == 0 and best_state.board[i][j] % 2 == 1:
                    position_B = (i, j)
            else:
                if (newState.board[i][j] % 2 == 0 and newState.board[i][j] != 0) and best_state.board[i][j] == 0:
                    position_A = (i, j)
                if (newState.board[i][j] == 0 or newState.board[i][j] % 2 == 1) and (best_state.board[i][j] != 0 and best_state.board[i][j] % 2 == 0):
                    position_B = (i, j)
    
    move = (position_A, position_B)
    if position_A is None:
        move = None
    #print('the coordinates: ' + str(move))

    # Change who's turn
    best_state.whose_move = 1 - currentState.whose_move

    # Make up a new remark
    newRemark = "I'll think harder in some future game. Here's my move"

    end_time = time.perf_counter()
    print('Calculation took ' + str(end_time - start_time) + ' seconds')
    return [move, best_state]

def demo_search(current_state, current_depth, max_ply, player, alpha, beta, time_lim):
    global start_time, ZOBRIST_HASHING, states_evaluated, times_pruned, min_eval, max_eval, retrieved_from_hash
    current_time = time.perf_counter()
    if current_time - start_time > time_lim * 0.95:
        return current_state

    moves = vs.valid_moves(current_state)
    if not moves or current_depth == max_ply:
        return current_state

    optimal_state = current_state
    # For each valid move, find the best move in the next ply
    for move in moves:
        state = demo_search(move, current_depth + 1, max_ply, 1 - player, alpha, beta, time_lim)
        move_value = 0
        hash_value = zh.hash_state(state)
        # Check if state has been hashed already.  Add to the hash table if not with its corresponding static evaluation value.
        if ZOBRIST_HASHING and hash_value in zh.zob_table:
            move_value = zh.zob_table[hash_value]
            retrieved_from_hash += 1
        else:
            move_value = staticEval(state)
            zh.zob_table[hash_value] = move_value
            states_evaluated += 1
        if move_value < min_eval:
            min_eval = move_value
        if move_value > max_eval:
            max_eval = move_value
        if player == WHITE:
            if move_value > alpha:
                alpha = move_value
                if current_depth == 0:
                    optimal_state = move
                else:
                    optimal_state = state
        else:
            if move_value < beta:
                beta = move_value
                if current_depth == 0:
                    optimal_state = move
                else:
                    optimal_state = state
        
        if alpha >= beta:
            times_pruned += 1
            return optimal_state

    return optimal_state

    

if __name__ == "__main__":
    MAX_PLY = 3 # How many moves ahead to consider
    ZOBRIST_HASHING = True # Use zobrist hashing if true
    TIME_LIMIT = 5 # Time limit to calculation in seconds
    SIDE = BLACK # Which side should make the move

    states_evaluated = 0
    retrieved_from_hash = 0
    times_pruned = 0
    min_eval = float("inf")
    max_eval = float("-inf")

    # Edit the board to see the best next move!
    board = Baroque_Chess.parse('''
c l i w k i l f
p p p p p p p p
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
P P P P P P P P
F L I W K I L C''')

    # Board for stalemate
#     board = Baroque_Chess.parse('''
# k - - - - - - -
# - W - - - - - -
# - - - - - - - -
# - - - - - - - -
# - - - - - - - -
# - - - - - - - -
# - - - - - - - -
# - - - K - - - -''')

#     board = Baroque_Chess.parse('''
# - - - - - - - -
# - - - - - - - -
# - - - k - - - -
# - - - - - - - -
# - - - - - - - -
# - - - - - - - C
# - - - - - - - -
# - - - K - - - -''')

#     board = Baroque_Chess.parse('''
# - - - - - - - -
# - - - K P - - P
# - - - - f - - -
# - l - - - - - P
# - - - p - i - -
# - - - - - - - -
# p - p - - p - -
# i - - w k - - c''')

    state = Baroque_Chess.Baroque_Chess_state(board, SIDE)

    zh.init_table()
    next_move = demo(state, MAX_PLY, ZOBRIST_HASHING, TIME_LIMIT)
    if next_move[0] is None:
        print("CAN'T MOVE!")
    else:
        print('Moves from ' + str(next_move[0][0]) + ' to ' + str(next_move[0][1]))
    
    print(next_move[1])
    print('States evaluated: ' + str(states_evaluated))
    print('Retrieved from hash table: ' + str(retrieved_from_hash))
    print('Times pruned: ' + str(times_pruned))
    print('Maximum evaluation value: ' + str(max_eval))
    print('Minimum evaluation value: ' + str(min_eval))