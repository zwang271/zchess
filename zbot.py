import chess
import random
import utils
import math
from time import time

MINUS_INF = -math.inf
POS_INF = math.inf

def timer_func(func):
    # This function shows the execution time of 
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func

class node():
    def __init__(self, eval, depth):
        self.eval = eval
        self.depth = depth

class Zbot():
    def __init__(self, mode = "random", depth = 5, w = [20, 2, 1, 8]):
        """ features = [material, activity, enemy_king, king_safety]
        """
        self.mode = mode
        self.table = {}
        self.depth = depth
        self.win = 0
        self.w = w
    
    def get_move(self, board):
        if self.mode == "random":
            return self.get_move_random(board)
        
        elif self.mode == "minimax":
            return self.get_move_minimax(board)

        elif self.mode == "genetic":
            return self.get_move_genetic(board)
    
    def get_move_random(self, board):
        moves = [m for m in board.legal_moves]
        if len(moves) > 0:
            return moves[random.randrange(0, len(moves))]

    # utility function for minimax
    def utility(self, board):
        B = utils.to_string(str(board))
        w = self.w

        # material advantage
        material = utils.material_count(B)

        # activity of pieces
        activity = 0
        activity = utils.pieces_forward(B, board.turn)
        
        # how close enemy king is to edge of board for checkmate
        enemy_king = 0
        if board.fullmove_number > 40:
            opponent = chess.WHITE if board.turn == chess.BLACK else chess.BLACK
            x, y = utils.get_king(B, opponent)
            enemy_king = utils.away_from_center((x, y)) if board.turn == chess.WHITE else -utils.away_from_center((x, y))
            enemy_king *= board.fullmove_number

        # king safety
        king_safety = 0
        if board.fullmove_number < 15:
            king_safety = utils.king_safety(B, board.turn)

        features = [material, activity, enemy_king, king_safety]
        eval = sum([w[i] * features[i] for i in range(len(features))])
        return eval

    @timer_func
    def get_move_minimax(self, board):
        depth = self.depth
        global nodes
        nodes = 0
        def maxi(board, d, alpha, beta):
            global nodes
            nodes += 1
            outcome = board.outcome()
            non_quiet_moves, rest = utils.get_sorted_legal_moves(board.copy())
            if outcome != None:
                if outcome.termination == chess.Termination.CHECKMATE:
                    if outcome.winner == chess.BLACK:
                        return None, MINUS_INF
                    elif outcome.winner == chess.WHITE:
                        return None, POS_INF
                else:
                    return None, 0
            if d == 0 and non_quiet_moves == []:
                return None, self.utility(board)

            best_eval = MINUS_INF
            best_move = None
            search_moves = non_quiet_moves + rest if d >= 0 else non_quiet_moves
            
            for m in search_moves:
            # for m in board.legal_moves:
                board.push(m)
                move, move_eval = mini(board, d-1, alpha, beta)
                if move_eval > best_eval:
                    best_eval = move_eval
                    best_move = m
                board.pop()

                if best_eval >= beta:
                    return best_move, best_eval
                if best_eval > alpha:
                    alpha = best_eval

            return best_move, best_eval
        
        def mini(board, d, alpha, beta):
            global nodes
            nodes += 1
            outcome = board.outcome()
            non_quiet_moves, rest = utils.get_sorted_legal_moves(board.copy())
            if outcome != None:
                if outcome.termination == chess.Termination.CHECKMATE:
                    if outcome.winner == chess.BLACK:
                        return None, MINUS_INF
                    elif outcome.winner == chess.WHITE:
                        return None, POS_INF
                else:
                    return None, 0
            if d == 0 and non_quiet_moves == []:
                return None, self.utility(board)
            
            best_eval = POS_INF
            best_move = None
            search_moves = non_quiet_moves + rest if d >= 0 else non_quiet_moves
            
            for m in search_moves:
            # for m in board.legal_moves:
                board.push(m)
                move, move_eval = maxi(board, d-1, alpha, beta)
                if move_eval < best_eval:
                    best_eval = move_eval
                    best_move = m
                board.pop()

                if best_eval <= alpha:
                    return best_move, best_eval
                if best_eval < beta:
                    beta = best_eval

            return best_move, best_eval
        
        if board.turn == chess.WHITE:
            move, eval = maxi(board, d = depth, alpha = MINUS_INF, beta = POS_INF)
            print(nodes)
            if move != None:
                return move
            else:
                return self.get_move_random(board)
        elif board.turn == chess.BLACK:
            move, eval = mini(board, d = depth, alpha = MINUS_INF, beta = POS_INF)
            print(nodes)
            if move != None:
                return move
            else:
                return self.get_move_random(board)
    


