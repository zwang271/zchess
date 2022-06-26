import chess
import chess.svg
import utils
import pieces
import pygame
import threading
import time
from zbot import Zbot
from zbot_negamax import Zbot_negamax

board = chess.Board()
white = "manual"
black = "auto"

zbot = Zbot_negamax(time_limit = 60, depth = 4, q = False, sort = True)

def get_square_under_mouse(board):
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) - BOARD_POS
    x, y = [int(v // STEP) for v in mouse_pos]
    try: 
        if x >= 0 and y >= 0: return (board[y][x], x, y)
    except IndexError: pass
    return None, None, None

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

def zbot_turn(board: chess.Board):
    if board.outcome() == None:
        m = zbot.get_move(board.copy())
        if ((black == "auto" and board.turn == chess.BLACK) or (white == "auto" and board.turn == chess.WHITE)):
            board.push(m)
            print(utils.piece_location(board))
            if board.outcome() != None:
                print(board.outcome())

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
show_coordinates = True
selected_piece = None
new_x, new_y = None, None

game = True
flag = True
while(game):
    B = utils.to_string(str(board))

    piece, x, y = get_square_under_mouse(B)
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            game = False # Flag that we are done so we exit this loop
        if (black == "manual" and board.turn == chess.BLACK) or (white == "manual" and board.turn == chess.WHITE):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # print([board.lan(m) for m in utils.get_sorted_legal_moves(board)])
                if selected_piece == None:
                    selected_piece = piece, x, y 
            if event.type == pygame.MOUSEBUTTONUP:
                piece, old_x, old_y = selected_piece
                m = utils.coord_to_move((old_x, old_y), (new_x, new_y))
                if m in board.legal_moves:
                    board.push(m)
                    threading.Thread(target = zbot_turn, args=[board]).start()
                else:
                    p = "q"
                    m_promote = utils.coord_to_move((old_x, old_y), (new_x, new_y), promotion = p)
                    if m_promote in board.legal_moves:
                        board.push(m_promote)
                        threading.Thread(target = zbot_turn, args=[board]).start()
                if board.outcome() != None:
                    print(board.outcome())            

                selected_piece = None
                
    if ((black == "auto" and board.turn == chess.BLACK) or (white == "auto" and board.turn == chess.WHITE)) and flag:  
        threading.Thread(target = zbot_turn, args=[board]).start()
        flag = False

    screen.fill((250, 243, 182))
    draw_board(screen)
    draw_pieces(screen)

    if x != None:
        rect = (BOARD_POS[0] + x * STEP, BOARD_POS[1] + y * STEP, STEP, STEP)
        pygame.draw.rect(screen, (255, 0, 0, 50), rect, 2)
    
    _, new_x, new_y = get_square_under_mouse(B)

    pygame.display.flip()
    clock.tick(60)


