import chess
from time import time
import math
import utils

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

class Zbot_negamax():
    def __init__(self, depth = 5, q = False, time_limit = math.inf, sort = True):
        self.depth = depth
        self.q = q
        self.tt = tt()
        self.time_limit = time_limit
        self.last_eval = None
        self.nodes_searched = [0, 0]
        self.sort = sort

    def nega_max(self, board: chess.Board, color: int, depth: int, alpha, beta, start_time = 0):
        self.nodes_searched[0] += 1
        if time() - start_time > self.time_limit:
            return 0, None

        original_alpha = alpha

        tt_entry = self.tt.look_up(board)
        if tt_entry != None and tt_entry.depth >= depth:
            if tt_entry.flag == "EXACT":
                return tt_entry.value, tt_entry.move
            elif tt_entry.flag == "LOWERBOUND":
                alpha = max(alpha, tt_entry.value)
            elif tt_entry.flag == "UPPERBOUND":
                beta = min(beta, tt_entry.value)
            
            if alpha > beta:
                return tt_entry.value, tt_entry.move
        elif tt_entry == None:
            tt_entry = entry()
        
        if self.q:
            if depth == 0:
                return self.q_search(board, color, depth - 1, -beta, -alpha, start_time)
            elif board.is_game_over():
                return color * eval(board).evaluate(), None
        else:
            if depth == 0 or board.is_game_over():
                return color * eval(board).evaluate(), None
        
        best_v = -math.inf
        best_m = None

        sorted_legal_moves = tt_entry.ordered_legal_moves if tt_entry.ordered_legal_moves != None and self.sort\
            else utils.get_sorted_legal_moves(board)
        move_eval_pairs = []

        break_flag = False
        for move in sorted_legal_moves:
            if break_flag:
                move_eval_pairs.append((move, -math.inf))
            else:
                board.push(move)
                board_eval, board_move = self.nega_max(board, -color, depth-1, -beta, -alpha, start_time)
                board_eval *= -1
                if board_eval > best_v:
                    best_v = board_eval
                    best_m = move
                board.pop()
                move_eval_pairs.append((move, board_eval))

            alpha = max(alpha, best_v)
            if alpha >= beta:
                break_flag = True
        move_eval_pairs.sort(key = lambda x: x[1], reverse = True)
        # print([(str(move_eval_pairs[i][0]), move_eval_pairs[i][1]) for i in range(len(move_eval_pairs))])

        tt_entry.ordered_legal_moves = [move_eval_pairs[i][0] for i in range(len(move_eval_pairs))]
        tt_entry.value = best_v
        tt_entry.move = best_m
        if best_v <= original_alpha:
            tt_entry.flag = "UPPERBOUND"
        elif best_v >= beta:
            tt_entry.flag = "LOWERBOUND"
        else:
            tt_entry.flag = "EXACT"
        tt_entry.depth = depth
        self.tt.table[hash(str(board))] = tt_entry

        return best_v, best_m

    @timer_func
    def get_move(self, board: chess.Board):
        color = 1 if board.turn == chess.WHITE else -1
        
        t_start = time()
        e, m = None, None
        if self.time_limit == math.inf:
            print(color)
            # e, m = self.nega_max(board, color, self.depth, alpha = color*math.inf, beta = color*-math.inf)
            if self.last_eval == None:
                e, m = self.nega_max(board, color, self.depth, alpha = color*math.inf, beta = color*-math.inf)
                self.last_eval = e
            else:
                e, m = self.nega_max(board, color, self.depth,\
                     alpha = self.last_eval + color*200, beta = self.last_eval-color*200)
                self.last_eval = e
        else:
            d = 1
            while time() - t_start < self.time_limit and d <= self.depth:
                e_temp, m_temp = self.nega_max(board, color, d,\
                     alpha = color*math.inf, beta = color*-math.inf, start_time = t_start)
                if m_temp != None:
                    print(d, self.nodes_searched)
                    e, m = e_temp, m_temp
                d += 1
        print(self.tt.rate())
        self.tt.reset_count()
        self.nodes_searched = [0, 0]
        return m

    def q_search(self, board: chess.Board, color: int, depth, alpha, beta, start_time):
        self.nodes_searched[1] += 1
        if time() - start_time > self.time_limit:
            return 0, None

        original_alpha = alpha

        tt_entry = self.tt.look_up(board)
        if tt_entry != None and tt_entry.depth >= depth:
            if tt_entry.flag == "EXACT":
                return tt_entry.value, tt_entry.move
            elif tt_entry.flag == "LOWERBOUND":
                alpha = max(alpha, tt_entry.value)
            elif tt_entry.flag == "UPPERBOUND":
                beta = min(beta, tt_entry.value)
            
            if alpha > beta:
                return tt_entry.value, tt_entry.move
        elif tt_entry == None:
            tt_entry = entry()

        checks, captures, castle, rest = utils.get_sorted_legal_moves(board, split = True)
        if captures == [] or board.is_game_over():
            return color * eval.material(board), None

        best_v = -math.inf
        best_m = None

        search_moves = checks + captures

        for move in search_moves:
            board.push(move)
            board_eval, board_move = self.q_search(board, -color, depth - 1, -beta, -alpha, start_time)
            board_eval *= -1
            if board_eval > best_v:
                best_v = board_eval
                best_m = move
            board.pop()

            alpha = max(alpha, best_v)
            if alpha >= beta:
                break
            
        tt_entry.value = best_v
        tt_entry.move = best_m
        if best_v <= original_alpha:
            tt_entry.flag = "UPPERBOUND"
        elif best_v >= beta:
            tt_entry.flag = "LOWERBOUND"
        else:
            tt_entry.flag = "EXACT"
        tt_entry.depth = depth
        self.tt.table[hash(str(board))] = tt_entry

        return best_v, best_m

#########################################################
# Heatmaps for activity values of pieces
a_knight = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 3, 3, 1, 0, 0,
    1, 1, 5, 2, 2, 5, 1, 1, 
    1, 1, 3, 5, 5, 3, 1, 1, 
    1, 1, 3, 5, 5, 3, 1, 1,
    1, 1, 5, 2, 2, 30, 1, 1, 
    0, 0, 1, 3, 3, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
]

a_bishop = [
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 5, 1, 2, 2, 1, 5, 1,
    1, 1, 2, 4, 4, 2, 1, 1, 
    1, 3, 5, 2, 2, 5, 3, 1,
    1, 3, 5, 2, 2, 5, 3, 1,
    1, 1, 2, 4, 4, 2, 1, 1, 
    1, 5, 1, 2, 2, 1, 5, 1,  
    0, 0, 0, 0, 0, 0, 0, 0  
]

a_pawn = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 2, 3, 4, 4, 3, 2, 1,
    3, 3, 4, 10, 10, 4, 3, 3,
    3, 3, 4, 10, 10, 4, 3, 3,
    1, 2, 3, 4, 4, 3, 2, 1,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
]
#########################################################

class eval():
    def __init__(self, board: chess.Board, W = [1, 1, 1, 1, 1]):
        """ W is the vector of weights for 
        features = [material, bishop_pair, activity_bishop, activity_knight, activity_pawn]
        Overall heuristic evaluation = W * features
        """
        self.W = W
        self.board = board
        self.L = utils.piece_location(board)
        self.color = 1 if board.turn == chess.WHITE else -1
        
    @staticmethod
    def material(board: chess.Board):
        outcome = board.outcome()
        if outcome != None:
            if outcome.termination == chess.Termination.CHECKMATE:
                if outcome.winner == chess.BLACK:
                    return -100000
                elif outcome.winner == chess.WHITE:
                    return 100000
            else:
                return 0

        m = 0
        piece_value = {
            "Q": 900, "K": 0, "N": 300, "B": 300, "R": 500, "P": 100,
            "q": -900, "k": 0, "n": -300, "b": -300, "r": -500, "p" : -100, " ": 0
        }
        for i in range(64):
            piece = board.piece_at(i)
            if  piece != None:
                m += piece_value[str(piece)]
        return m

    def bishop_pair(self):
        bishop_location = self.L["B"] if self.board.turn == chess.WHITE else self.L["b"]
        if len(bishop_location) == 2:
            return 25
        else:
            return 0

    def activity_knight(self):
        knight = "N" if self.board.turn == chess.WHITE else "n"
        return sum([a_knight[i] for i in self.L[knight]])

    def activity_bishop(self):
        bishop = "B" if self.board.turn == chess.WHITE else "b"
        return sum([a_bishop[i] for i in self.L[bishop]])
    
    def activity_pawn(self):
        pawn = "P" if self.board.turn == chess.WHITE else "p"
        return sum([a_pawn[i] for i in self.L[pawn]])

    def evaluate(self):
        material = eval.material(self.board)
        bishop_pair = self.bishop_pair() * self.color
        activity_bishop = self.activity_bishop() * self.color
        activity_knight = self.activity_knight() * self.color
        activity_pawn = self.activity_pawn() * self.color

        feature = [material, bishop_pair, activity_bishop, activity_knight, activity_pawn]
        return sum([feature[i] * self.W[i] for i in range(len(feature))])

class entry():
    def __init__(self, value = 0, flag = "", depth = 0, move = None):
        self.value = value
        self.flag = flag
        self.depth = depth
        self.move = move
        self.ordered_legal_moves = None
        
class tt():
    def __init__(self):
        self.table = {}
        self.hit = 0.0
        self.total = 0.0
    
    def look_up(self, board: chess.Board) -> entry:
        self.total += 1
        try:
            entry = self.table[hash(str(board))]
            self.hit += 1
            return entry
        except:
            return None

    def rate(self):
        if self.total > 0:
            return self.hit / self.total
        else:
            return 0
    
    def reset_count(self):
        self.hit = 0
        self.total = 0

