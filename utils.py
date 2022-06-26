import chess
import numpy as np
import pygame
import pieces

def to_string(board):
    """ Converts a str rep of chess.board object to a 2d string array
    Input: chess.board object
    Output: 8x8 2d string array
    """
    B = [[" " for _ in range(8)] for _ in range(8)]
    x, y = 0, 0
    for char in board:
        if char == '\n':
            x = 0
            y += 1
        elif char == ' ':
            x += 1
        else:
            B[y][x] = char if char != "." else " "
    return B

def to_algebraic(coordinate):
    """
    Input: coordinate in range [0, 7] x [0, 7]
    Output: coordinate on board in algebraic notaton
    """
    coord_to_letter = {
        0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"
    }    
    return coord_to_letter[coordinate[0]] + str(8 - coordinate[1]) if coordinate != "-" else "-"

def to_coordinate(algebraic):
    """
    Input: coordinate on board in algebraic notaton
    Output: coordinate in range [0, 7] x [0, 7]
    """
    letter_to_coord = {
        "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7
    }
    return (letter_to_coord[algebraic[0]], 8 - int(algebraic[1]))

def print_board(B):
    """ Prints each rank of the board
    Input: None
    Output: None
    """
    for rank in B:
        print(rank)

def coord_to_move(old, new, promotion = ""):
    """ Converts coordinates to a chess.move 
    Input: coordinate in range [0, 7] x [0, 7]
    Output: chess.move in uci format
    """
    if old != new:
        return chess.Move.from_uci(to_algebraic(old) + to_algebraic(new) + promotion)
    else:
        return None

def material_count(B):
    """ Returns relative count of material
    Input: 2d string array B
    Output: Material count with positive representing white advantage
    and negative representing black advantage
    """
    m = 0
    value = {
        "Q": 9, "K": 0, "N": 3, "B": 3, "R": 5, "P": 1,
        "q": -9, "k": 0, "n": -3, "b": -3, "r": -5, "p" : -1, " ": 0
    }
    for i in range(8):
        for j in range(8):
            m += value[B[i][j]]
    return m

def get_king(B, color):
    """ Returns the coordinates of the COLOR king
    Input: 2d string array B
           COLOR of desired king
    Output: coordinate of the king in range [0, 7] x [0, 7]
    """
    king = "K" if color == chess.WHITE else "k"
    for x in range(8):
        for y in range(8):
            if B[y][x] == king:
                return (x, y)

def away_from_center(coord):
    """ Heatmap of the board that gives higher values to squares away from the center
    Input: coordinate in range [0, 7] x [0, 7]
    Output: value associated in the heatmap 
    3 3 3 3 3 3 3 3
    3 2 2 2 2 2 2 3
    3 2 1 1 1 1 2 3
    3 2 1 0 0 1 2 3
    3 2 1 0 0 1 2 3
    3 2 1 1 1 1 2 3
    3 2 2 2 2 2 2 2
    3 3 3 3 3 3 3 3 
    """
    value = {
        (0, 0): 3,(1, 0): 3,(2, 0): 3,(3, 0): 3,(4, 0): 3,(5, 0): 3,(6, 0): 3,(7, 0): 3,
        (0, 1): 3,(1, 1): 2,(2, 1): 2,(3, 1): 2,(4, 1): 2,(5, 1): 2,(6, 1): 2,(7, 1): 3,
        (0, 2): 3,(1, 2): 2,(2, 2): 1,(3, 2): 1,(4, 2): 1,(5, 2): 1,(6, 2): 2,(7, 2): 3,
        (0, 3): 3,(1, 3): 2,(2, 3): 1,(3, 3): 0,(4, 3): 0,(5, 3): 1,(6, 3): 2,(7, 3): 3,
        (0, 4): 3,(1, 4): 2,(2, 4): 1,(3, 4): 0,(4, 4): 0,(5, 4): 1,(6, 4): 2,(7, 4): 3,
        (0, 5): 3,(1, 5): 2,(2, 5): 1,(3, 5): 1,(4, 5): 1,(5, 5): 1,(6, 5): 2,(7, 5): 3,
        (0, 6): 3,(1, 6): 2,(2, 6): 2,(3, 6): 2,(4, 6): 2,(5, 6): 2,(6, 6): 2,(7, 6): 3,
        (0, 7): 3,(1, 7): 3,(2, 7): 3,(3, 7): 3,(4, 7): 3,(5, 7): 3,(6, 7): 3,(7, 7): 3,
    }
    return value[coord]

def king_safety(B, color):
    """ Heatmap of the board that assignes value to safety of king
    Input: 8x8 2d string array B, COLOR of king
    Output: value associated in the heatmap 
    3 3 4 2 2 2 4 3
    2 2 2 2 2 2 2 2
    1 1 1 1 1 1 1 1
    1 1 1 0 0 1 1 1
    1 1 1 0 0 1 1 1
    1 1 1 1 1 1 1 1
    2 2 2 2 2 2 2 2
    3 3 4 2 2 2 4 3 
    """
    king = get_king(B, color)
    value = {
        (0, 0): 3,(1, 0): 3,(2, 0): 5,(3, 0): 2,(4, 0): 2,(5, 0): 2,(6, 0): 5,(7, 0): 3,
        (0, 1): 2,(1, 1): 2,(2, 1): 2,(3, 1): 2,(4, 1): 2,(5, 1): 2,(6, 1): 2,(7, 1): 2,
        (0, 2): 1,(1, 2): 1,(2, 2): 1,(3, 2): 1,(4, 2): 1,(5, 2): 1,(6, 2): 1,(7, 2): 1,
        (0, 3): 1,(1, 3): 1,(2, 3): 1,(3, 3): 0,(4, 3): 0,(5, 3): 1,(6, 3): 1,(7, 3): 1,
        (0, 4): 1,(1, 4): 1,(2, 4): 1,(3, 4): 0,(4, 4): 0,(5, 4): 1,(6, 4): 1,(7, 4): 1,
        (0, 5): 1,(1, 5): 1,(2, 5): 1,(3, 5): 1,(4, 5): 1,(5, 5): 1,(6, 5): 1,(7, 5): 1,
        (0, 6): 2,(1, 6): 2,(2, 6): 2,(3, 6): 2,(4, 6): 2,(5, 6): 2,(6, 6): 2,(7, 6): 2,
        (0, 7): 3,(1, 7): 3,(2, 7): 5,(3, 7): 2,(4, 7): 2,(5, 7): 2,(6, 7): 5,(7, 7): 3,
    }
    safety = value[king] if color == chess.WHITE else -value[king]
    return safety

def knight_activity(B, color):
    """ Heatmap of the board that assignes value to activity of knight
    Input: 8x8 2d string array B, COLOR of king
    Output: value associated in the heatmap 
    3 3 4 2 2 2 4 3
    2 2 2 2 2 2 2 2
    1 1 1 1 1 1 1 1
    1 1 1 0 0 1 1 1
    1 1 1 0 0 1 1 1
    1 1 1 1 1 1 1 1
    2 2 2 2 2 2 2 2
    3 3 4 2 2 2 4 3 
    """
    king = get_king(B, color)
    value = {
        (0, 0): 3,(1, 0): 3,(2, 0): 5,(3, 0): 2,(4, 0): 2,(5, 0): 2,(6, 0): 5,(7, 0): 3,
        (0, 1): 2,(1, 1): 2,(2, 1): 2,(3, 1): 2,(4, 1): 2,(5, 1): 2,(6, 1): 2,(7, 1): 2,
        (0, 2): 1,(1, 2): 1,(2, 2): 1,(3, 2): 1,(4, 2): 1,(5, 2): 1,(6, 2): 1,(7, 2): 1,
        (0, 3): 1,(1, 3): 1,(2, 3): 1,(3, 3): 0,(4, 3): 0,(5, 3): 1,(6, 3): 1,(7, 3): 1,
        (0, 4): 1,(1, 4): 1,(2, 4): 1,(3, 4): 0,(4, 4): 0,(5, 4): 1,(6, 4): 1,(7, 4): 1,
        (0, 5): 1,(1, 5): 1,(2, 5): 1,(3, 5): 1,(4, 5): 1,(5, 5): 1,(6, 5): 1,(7, 5): 1,
        (0, 6): 2,(1, 6): 2,(2, 6): 2,(3, 6): 2,(4, 6): 2,(5, 6): 2,(6, 6): 2,(7, 6): 2,
        (0, 7): 3,(1, 7): 3,(2, 7): 5,(3, 7): 2,(4, 7): 2,(5, 7): 2,(6, 7): 5,(7, 7): 3,
    }
    safety = value[king] if color == chess.WHITE else -value[king]
    return safety

def difference_from_starting(B, color):
    """ Returns how many squares of B differ from starting 
    chess position for first two rows of COLOR side
    Input: 8x8 2d string array B
           COLOR of side to check difference with
    Output: Number of squares that differ
    """
    A = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]
    
    diff = 0
    if color == chess.BLACK:
        for x in range(8):
            for y in [0, 1]:
                # if B[y][x] != A[y][x]:
                #     diff -= 1
                if B[y][x] == " ":
                    diff -= 1
    else:
        for x in range(8):
            for y in [6, 7]:
                # if B[y][x] != A[y][x]:
                #     diff += 1
                if B[y][x] == " ":
                    diff += 1
    return diff

def pieces_forward(B, color):
    """ Returns how many of COLOR pieces have been developed forward
    Input: 8x8 string array B
           COLOR of pieces to analyze forward movement of
    Output: Number of squares advanced forward
    """
    forward = 0
    if color == chess.BLACK:
        for x in range(8):
            for y in [2, 3, 4, 5, 6, 7]:
                if B[y][x] != " " and B[y][x].islower():
                    forward -= 1
    else:
        for x in range(8):
            for y in [0, 1, 2, 3, 4, 5]:
                # if B[y][x] != A[y][x]:
                #     diff += 1
                if B[y][x] != " " and B[y][x].isupper():
                    forward += 1
    return forward 

def pawn_structure(B, color):
    """ Counts how many groups of pawns there are for COLOR
    Input: 8x8 2d string array B
           COLOR of desired pawns
    Output: Number of pawn groups 
    """
    unit = -1 if color == chess.WHITE else 1
    pawn = "P" if color == chess.WHITE else "p"
    pawn_file = [False for i in range(8)]

    for x in range(8):
        for y in range(8):
            if B[y][x] == pawn:
                pawn_file[x] = True
                break
    
    islands = 0
    for i in range(8):
        if i+1 in range(8) and pawn_file[i] != pawn_file[i+1]:
            islands += 1
    return islands*unit

def simulate_game(A, B, verbose = False):
        """Simulates a full game of chess between two players A and B
        input: A and B has methods .get_move(board)
        output: 1 if A wins, -1 if B wins, 0 if tie
        """
        board = chess.Board()
        board_history = [to_string(str(board))]
        while board.outcome() == None:
            move = None
            if board.turn == chess.WHITE:
                move = A.get_move(board)
            elif board.turn == chess.BLACK:
                move = B.get_move(board)
            board.push(move)
            board_history.append(to_string(str(board)))
            if verbose:
                print(board, "\n")

        outcome = board.outcome()
        winner = None
        if verbose:
            print(outcome)
        if outcome.termination == chess.Termination.CHECKMATE:
            if outcome.winner == chess.BLACK:
                winner = -1
            elif outcome.winner == chess.WHITE:
                winner = 1
        else:
            winner = 0 
        return winner, board_history

def view_game(board_history):
    """ Displays a full game played in GUI 
    Input: BOARD_HISTORY of every board positin reached
    Output: GUI that lets user click through the game
    """
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    pygame.init()
    X = 1000
    Y = 800
    size = [X, Y]
    BOARD_POS = ((X-Y)/2, 0)
    STEP = Y//8
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()  

    def draw_board(screen): 
        for i in range(8):
            for j in range(8):
                if (i + j)%2 == 0:
                    pygame.draw.rect(screen, WHITE, [(X-Y)/2 + i*STEP, j*STEP, STEP, STEP])
                else:
                    pygame.draw.rect(screen, (138, 95, 3), [(X-Y)/2 + i*STEP, j*STEP, Y//8, Y//8]) 
    
    def draw_pieces(screen):
        for i in range(8):
            for j in range(8):
                piece = B[i][j]
                if piece != " ":
                    pieces.show(screen, pieces.png[piece], STEP, (i, j), X, Y)

    game = True
    i = 0
    while(game):
        B = board_history[i]
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                game = False # Flag that we are done so we exit this loop
            if event.type == pygame.MOUSEBUTTONDOWN:
                i += 1

        screen.fill((250, 243, 182))
        draw_board(screen)
        draw_pieces(screen)
        pygame.display.flip()
        clock.tick(60)

def get_sorted_legal_moves(board: chess.Board, split = False):
    """ Sorts legal moves of the board in order of heuristic goodness
    Input: chess.Board object BOARD
           SPLIT = TRUE will output non_quiet_moves, quiet_moves
    Output: legal moves sorted by checks, captures, castle, rest 
    """
    legal_moves = [m for m in board.legal_moves]
    lan_list = [board.lan(m) for m in board.legal_moves]
    checks = []
    captures = []
    castle = []
    rest = []
    for i in range(len(lan_list)):
        if "+" in lan_list[i]:
            checks.append(legal_moves[i])
        elif "x" in lan_list[i]:
            captures.append(legal_moves[i])
        elif "O" in lan_list[i]:
            castle.append(legal_moves[i])
        else:
            rest.append(legal_moves[i])
    if split:
        return checks, captures, castle, rest
    else:
        return checks + captures + castle + rest

def to_bit_map(board: chess.Board):
    """ Converts a chess.board object to a 12x64 np array
    """
    # B = to_string(str(board))
    # B_flatten = [c for row in B for c in row]
    # bit_map = np.zeros((12, 64))
    # for i in range(len(B_flatten)):
    #     if B_flatten[i] != " ":

    bit_map = np.zeros((12, 64))
    for i in range(64):
        c = str(board.piece_at(i))
        if c != None:
            if c == "R":
                bit_map[0, i] = 1
            elif c == "N":
                bit_map[1, i] = 1
            elif c == "B":
                bit_map[2, i] = 1
            elif c == "K":
                bit_map[3, i] = 1
            elif c == "Q":
                bit_map[4, i] = 1
            elif c == "P":
                bit_map[5, i] = 1
            elif c == "r":
                bit_map[6, i] = 1
            elif c == "n":
                bit_map[7, i] = 1
            elif c == "b":
                bit_map[8, i] = 1
            elif c == "k":
                bit_map[9, i] = 1
            elif c == "q":
                bit_map[10, i] = 1
            elif c == "p":
                bit_map[11, i] = 1
    return bit_map
        
def simulate_probability(p):
    if np.random.default_rng().uniform(0, 1, 1) < p:
        return True
    else:
        return False

def piece_location(board: chess.Board(), pair = False) -> dict:
    """ 
    Returns a dictionary containing lists of the indices of where each piece is
    Set pair = True to obtain pairs describing location of each piece instead
    """
    L = {
        "P": [], "B": [], "N": [], "Q": [], "K": [], "R": [],
        "p": [], "b": [], "n": [], "q": [], "k": [], "r": []
    }
    for i in range(64):
        x = board.piece_at(i)
        if x != None:
            coord = i
            if pair:
                coord = (i%8, i//8)
            L[str(x)].append(coord)
    return L  