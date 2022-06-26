import chess
import random
import utils
import math
from time import time
from zbot_eval import eval
import numpy as np
import json
from joblib import Parallel, delayed

MINUS_INF = -math.inf
POS_INF = math.inf
seed = 91

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

class Zbot_minimax():
    def __init__(self, eval: eval, depth = 4, verbose = False):
        self.depth = depth
        self.eval = eval
        self.nodes = 0
        self.verbose = verbose
        self.wins = 0
    
    def get_move_random(self, board):
        moves = [m for m in board.legal_moves]
        if len(moves) > 0:
            return moves[random.randrange(0, len(moves))]

    def get_move(self, board: chess.Board):
        if board.turn == chess.WHITE:
            move, eval = self.maxi(board, d = self.depth, alpha = MINUS_INF, beta = POS_INF)
            if self.verbose:
                print(self.nodes)
            self.nodes = 0
            if move != None:
                return move
            else:
                return self.get_move_random(board)
        elif board.turn == chess.BLACK:
            move, eval = self.mini(board, d = self.depth, alpha = MINUS_INF, beta = POS_INF)
            if self.verbose:
                print(self.nodes)
            self.nodes = 0
            if move != None:
                return move
            else:
                return self.get_move_random(board)

    def mini(self, board, d, alpha, beta):
        self.nodes += 1
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
            return None, self.eval.evaluate(board)
        
        best_eval = POS_INF
        best_move = None
        search_moves = non_quiet_moves + rest if d >= 0 else non_quiet_moves
        
        for m in search_moves:
        # for m in board.legal_moves:
            board.push(m)
            move, move_eval = self.maxi(board, d-1, alpha, beta)
            if move_eval < best_eval:
                best_eval = move_eval
                best_move = m
            board.pop()

            if best_eval <= alpha:
                return best_move, best_eval
            if best_eval < beta:
                beta = best_eval

        return best_move, best_eval

    def maxi(self, board, d, alpha, beta):
        self.nodes += 1
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
            return None, self.eval.evaluate(board)

        best_eval = MINUS_INF
        best_move = None
        search_moves = non_quiet_moves + rest if d >= 0 else non_quiet_moves

        for m in search_moves:
        # for m in board.legal_moves:
            board.push(m)
            move, move_eval = self.mini(board, d-1, alpha, beta)
            if move_eval > best_eval:
                best_eval = move_eval
                best_move = m
            board.pop()

            if best_eval >= beta:
                return best_move, best_eval
            if best_eval > alpha:
                alpha = best_eval

        return best_move, best_eval

class Zbot_genetic():
    def __init__(self, population_size = 10, generations = 5, d = 1):
        self.population_size = population_size
        self.generations = generations
        self.depth = d

        self.population = []
        for i in range(self.population_size):
            # W = np.random.default_rng(seed = i + seed).uniform(-1, 1, (12, 64))
            # V = np.random.default_rng(seed = i + 2*seed).uniform(-1, 1, 12)

            M = np.random.default_rng(seed = i + 2*seed).uniform(-100, 100, 12)
            self.population.append(Zbot_minimax(eval = eval(M), depth = self.depth))

        # Wa = np.load('./weights/Wa.npy')
        # Va = np.load('./weights/Va.npy')
        # self.population.append(Zbot_minimax(eval = eval(Wa, Va), depth = self.depth))
        # Wb = np.load('./weights/Wb.npy')
        # Vb = np.load('./weights/Vb.npy')
        # self.population.append(Zbot_minimax(eval = eval(Wb, Vb), depth = self.depth))
        # for i in range(2, self.population_size):
        #     e = eval.breed(self.population[0].eval, self.population[1].eval)
        #     e.mutate(mutation_rate = 0.1)
        #     self.population.append(Zbot_minimax(eval = e, depth = self.depth))

        # Ma = np.load("./weights/Ma.npy")
        # Mb = np.load("./weights/Mb.npy")
        # self.population.append(Zbot_minimax(eval = eval(Ma), depth = self.depth))
        # e = eval(Mb)
        # while np.array_equal(Ma, Mb):
        #     e.mutate(mutation_rate = 0.5, mutation_factor = 0.5)
        # print(Ma, "\n", Mb)
        # self.population.append(Zbot_minimax(eval = e, depth = self.depth))
        # for i in range(2, self.population_size):
        #     e = eval.breed(self.population[0].eval, self.population[1].eval)
        #     e.mutate(mutation_rate = 0.3)
        #     self.population.append(Zbot_minimax(eval = e, depth = self.depth))

    def play(self, i, j):
        if i != j:
            A = self.population[i]
            B = self.population[j]
            result = utils.simulate_game(A, B, verbose = False)[0]
            # print(i, j, result)
            if result == 1:
                # A.wins += 1
                return i
            elif result == -1:
                # B.wins += 1
                return j

    def simulate_evolution(self):
        for gen in range(self.generations):

            # for i in range(self.population_size):
            #     for j in range(self.population_size):
            #         self.play(i, j)

            result = Parallel(n_jobs = 6)(delayed(self.play)(i, j) for i in range(self.population_size) for j in range(self.population_size))
            for i in result:
                if i != None:
                    self.population[i].wins += 1

            self.population.sort(key = lambda eval: eval.wins, reverse = True)
            # np.save("./weights/Wa.npy", self.population[0].eval.W)
            # np.save("./weights/Va.npy", self.population[0].eval.V)
            # np.save("./weights/Wb.npy", self.population[1].eval.W)
            # np.save("./weights/Vb.npy", self.population[1].eval.V)

            while np.array_equal(self.population[0].eval.M, self.population[1].eval.M):
                self.population[1].eval.mutate(mutation_rate = 0.3)
            np.save("./weights/Ma.npy", self.population[0].eval.M)
            np.save("./weights/Mb.npy", self.population[1].eval.M)
            print([self.population[i].wins for i in range(self.population_size)])
            self.population[0].wins = 0
            self.population[1].wins = 0
            for i in range(2, self.population_size):
                e = eval.breed(self.population[0].eval, self.population[1].eval)
                e.mutate(mutation_rate = 0.3 - 0.2*gen/self.generations, \
                    mutation_factor = 0.3 - 0.2*gen/self.generations)
                self.population[i] = Zbot_minimax(eval = e, depth = self.depth)

# t1 = time()
# G = Zbot_genetic(population_size = 7, generations = 20, d = 1)
# G.simulate_evolution()
# t2 = time()
# print(f'{(t2-t1):.4f}')

# A = Zbot_minimax(eval = eval(W, V), depth = 2)
# W = np.random.default_rng().uniform(-1, 1, (12, 64))
# V = np.random.default_rng().uniform(-1, 1, 12)
# B = Zbot_minimax(eval = eval(W, V), depth = 2)
# t1 = time()
# board_history = utils.simulate_game(A, B, verbose = False)[1]
# t2 = time()
# print(f'{(t2-t1):.4f}')
# utils.view_game(board_history)
