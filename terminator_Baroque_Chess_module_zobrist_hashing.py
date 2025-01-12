'''
terminator_Baroque_Chess_module_zobreadeist_hashing.py

This is the implementation of zobrist hashing for Baroque Chess.
'''

import random

WIDTH = 8
HEIGHT = 8

PIECES = {2:'p',3:'P',4:'c',5:'C',6:'l',7:'L',8:'i',9:'I', 10:'w',11:'W',12:'k',13:'K',14:'f',15:'F'}

table = []
zob_table = {}

# example_structure = [[[343, 345345, 23523525, 34543], [2343, 2342]], [[2343, 243], [2342]], [[2343], [6575]]]

# For every cell and every piece in that cell, assign a random number to it
def init_table():
    global table
    for i in range(8):
        row = []
        for j in range(8):
            cell = {}
            for piece in PIECES:
                cell[piece] = random.getrandbits(64)
            row.append(cell)
        table.append(row)

# Returns the hash value for a given state
def hash_state(state):
    global table
    h = 0
    board = state.board
    for row in range(8):
        for column in range(8):
            piece = board[row][column]
            if piece != 0:
                h ^= table[row][column][piece]
    return h
