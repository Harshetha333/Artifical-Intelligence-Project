
'''BaroqueGameMaster.py
Formerly TimedGameMaster.py which was based on GameMaster.py which in turn is 
 based on code from RunKInARow.py
'''
VERSION = '0.8-BETA'

# Get names of players and time limit from the command line.


import sys
Time_Limit_Per_Move = 1.0 # default time limit , A second.
TURN_LIMIT = 100   # Good for testing.
#TURN_LIMIT = 110 # Terminates runaway games.
if len(sys.argv) > 1:
    import importlib    
    Opponent1 = importlib.import_module(sys.argv[1])
    Opponent2 = importlib.import_module(sys.argv[2])
    if len(sys.argv) > 3:
        Time_Limit_Per_Move = float(sys.argv[3])
else:

    import PlayerSkeletonA as Opponent1
    import PlayerSkeletonB as Opponent2

import Baroque_Chess_state_etc as Baroque_Chess

VALIDATE_MOVES = False # If players are trusted not to cheat, this could be turned off to save time.
if VALIDATE_MOVES: import Baroque_Chess_move_validator as V

from winTester import winTester

CURRENT_PLAYER = Baroque_Chess.WHITE


FINISHED = False
def runGame():
    # Set up for the match, and report on its details: 
    currentState = Baroque_Chess.Baroque_Chess_state()
    print('**** Baroque Chess Gamemaster v'+VERSION+' *****')
    print('The Gamemaster says, "Players, introduce yourselves."')
    print(' (Playing WHITE:) '+Opponent1.introduce())
    print(' (Playing BLACK:) '+Opponent2.introduce())

    try:
        p1comment = Opponent1.prepare(Opponent2.nickname())
    except:
        report = 'Player 1 ('+Opponent1.nickname()+' failed to prepare, and loses by default.'
        print(report)
        report = 'Congratulations to Player 2 ('+Opponent2.nickname()+')!'
        print(report)
        return
    try:
        p2comment = Opponent2.prepare(Opponent1.nickname())
    except:
        report = 'Player 2 ('+Opponent2.nickname()+' failed to prepare, and loses by default.'
        print(report)
        report = 'Congratulations to Player 1 ('+Opponent1.nickname()+')!'
        print(report)
        return
    
    print('\nThe Gamemaster says, "Let\'s get started!"\n')
    print('The initial states of Baroque chess are...')

    currentRemark = "The game is about to start."

    WHITEsTurn = True
    name = None
    global FINISHED
    FINISHED = False
    WINNER = "not yet known"
    turnCount = 1
    print(currentState)
    while not FINISHED:
        # Whoever's turn it is, well, move!
        who = currentState.whose_move
        if who==Baroque_Chess.WHITE:
            side = 'WHITE'; other_side='BLACK'
        else: side = 'BLACK'; other_side='WHITE'
        global CURRENT_PLAYER
        CURRENT_PLAYER = who
        if WHITEsTurn:
            move_fn = Opponent1.makeMove
            name = Opponent1.nickname()
        else:
            move_fn = Opponent2.makeMove
            name = Opponent2.nickname()
        playerResult = timeout(move_fn,args=(currentState, currentRemark, Time_Limit_Per_Move), kwargs={}, timeout_duration=Time_Limit_Per_Move, default=(None,"I give up!"));
        WHITEsTurn = not WHITEsTurn

        # Let's analyze the response of the player.
        moveAndState, currentRemark = playerResult
        if moveAndState==None:
            print("No move returned by "+side+".")
            WINNER = other_side
            FINISHED = True; break
        # First we handle a special case where there might be a draw, due to
        # no legal moves available to the current player.
        # The player has to return a specific string if it can't find a legal move.
        if currentRemark == "I guess I have no legal moves.":
            if VALIDATE_MOVES:
                (isDraw, newState) = V.any_legal_move(currentState)
                if isDraw:
                    FINISHED=True
                    print("Stalemate: "+side+" has no moves!"); break
                else:
                    print("You claim there are no legal moves,")
                    print("but you could go here: ")
                    print(newState.__repr__())
                    print("Game over. "+side+" loses.")
                    WINNER = other_side
                    FINISHED=True
                    break;
            else:
                print("Player "+side+" is requesting a draw. With move validation off,")
                print("we need a human umpire to OK this.")
                answer = input("Enter Y to declare a draw, or N to disallow the draw: ")
                if answer.lower()=='y': WINNER='DRAW'
                else: WINNER=other_side
                FINISHED = True; break
                
        # Some move was returned, so let's find out if it was valid.
        try:
          move, newState = moveAndState
          startsq, endsq = move
          i,j=startsq
          ii,jj=endsq
        except Exception as e:
           print("The moveAndState value did not have the proper form of [move, newState] or")
           print("the move did not have the proper form such as ((3, 7), (5, 7)).")
           WINNER = other_side
           FINISHED = True;
        print(side+"'s move: the "+Baroque_Chess.CODE_TO_INIT[currentState.board[i][j]]+\
              " at ("+str(i)+", "+str(j)+") to ("+str(ii)+", "+str(jj)+").")
        
        if VALIDATE_MOVES:
            (status, result)=V.validate(move, currentState, newState)
            
            if not status:
                print("Illegal move by "+side)  # Returned state is:\n" + str(currentState))
                print(result)

                print(side+"'s proposed, new states are: ")
                print(newState.__repr__())
                WINNER = other_side
                FINISHED=True
                break
            else:
                print("valid move")
                print(result)

        moveReport = "Turn "+str(turnCount)+": Move is by "+side
        print(moveReport)
        utteranceReport = name +' says: '+currentRemark
        print(utteranceReport)
        currentState = newState
        possibleWin = winTester(currentState)
        if possibleWin != "No win":
            WINNER = side
            FINISHED = True
            print(currentState)
            print(possibleWin)
            break
        print(currentState)
        turnCount += 1
        if turnCount > TURN_LIMIT:
            FINISHED=True
            print("TURN_LIMIT exceeded! ("+str(TURN_LIMIT)+")")
            break

    print("Game over.")
    if (WINNER=="not yet known") or (WINNER == "DRAW"):
      print("The outcome is a DRAW.  NO Winner.")
    else:
      print("Congratulations to the winner: "+WINNER)


import sys
import time
def timeout(func, args=(), kwargs={}, timeout_duration=2
            
            , default=None):
    '''This function will spawn a thread and run the given function using the args, kwargs and 
    return the given default value if the timeout_duration is exceeded 
    ''' 
    import threading
    class PlayerThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default
        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except Exception as e:
                print("It Seems there was an exception during play by "+CURRENT_PLAYER+":\n"+str(e))
                print(sys.exc_info())
                self.result = default

    pt = PlayerThread()
    pt.start()
    started_at = time.time()
    pt.join(timeout_duration)
    ended_at = time.time()
    diff = ended_at - started_at
    print("Time used for making Move: %0.5f seconds out of " % diff, timeout_duration)
    if pt.is_alive():
        print("The Player has taken too long.")
        print("We are now terminating the game.")
        print("Player "+CURRENT_PLAYER+" loses.")
        if USE_HTML: gameToHTML.reportResult("Player "+CURRENT_PLAYER+" The Player has taken too long (%04f seconds) and thus they loses." % diff)
        if USE_HTML: gameToHTML.endHTML()
        exit()
    else:
        #print("Within the time limit -- Lovely!")
        return pt.result

runGame()
