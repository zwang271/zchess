import json
import random
import chess
from zbot import Zbot
import utils
import numpy as np
from time import time

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

class evalFC():
    """ Fully connected evaluator, not very good
    """
    def __init__(self, W:np.ndarray, V:np.ndarray):
        """ 
        W is a 12x64 matrix of weights
        V is a 12x1 matrix of weights
        """
        self.W = W
        self.V = V
    
    def soft_sign(self, X: np.ndarray):
        """ 
        soft_sign(x) = x / (1 + |x|)
        """
        return X/(1 + np.abs(X))

    def evaluate(self, X:np.ndarray):
        """
        Returns the evaluation of the bitboard X
        Input: np array X of size 12x64
        Output: evaluation in range [-1, 1]
        """
        return np.sum((self.V * self.soft_sign(np.sum(self.W * X, axis = 1))))

    @staticmethod
    def breed(evalA, evalB):
        """ Takes the weight vectors of evalA and evalB and cross pollinates them
        to create a new eval object
        """
        size_W = evalA.W.shape[0]
        size_V = evalA.V.shape[0]
        W, V = np.zeros(evalA.W.shape), np.zeros(size_V)
        gene_W = np.random.choice([False, True], size = size_W)
        gene_V = np.random.choice([False, True], size = size_V)
        for i in range(len(gene_W)):
            W[i] = evalA.W[i] if gene_W[i] else evalB.W[i]
        for i in range(len(gene_V)):
            V[i] = evalA.V[i] if gene_V[i] else evalB.V[i]
        return eval(W, V)
    
    def mutate(self, mutation_rate = 0.05):
        for idx, _ in np.ndenumerate(self.W):
            if utils.simulate_probability(mutation_rate):
                self.W[idx] = np.random.default_rng().uniform(-1, 1, 1)
        for idx, _ in np.ndenumerate(self.V):
            if utils.simulate_probability(mutation_rate):
                self.V[idx] = np.random.default_rng().uniform(-1, 1, 1)

def piece_location(board: chess.Board(), pair = False) -> dict:
    """ 
    Returns a dictionary containing lists of the index of where each piece is
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

class eval():
    """ 
    """
    def __init__(self, M: np.ndarray):
        self.M = M
    
    def evaluate(self, board):
        L = piece_location(board)
        piece_count = [len(L[x]) for x in L.keys()]
        piece_count = np.array(piece_count)
        return np.sum(piece_count * self.M)

    @staticmethod
    def breed(evalA, evalB):
        """ Takes the weight vectors of evalA and evalB and cross pollinates them
        to create a new eval object
        """
        # splice = random.randrange(0, len(evalA.M))
        # M = np.concatenate([evalA.M[:splice], evalB.M[splice:]])
        # return eval(M)
        size_M = evalA.M.shape[0]
        M = np.zeros(evalA.M.shape)
        gene_M = np.random.choice([False, True], size = size_M)
        for i in range(len(gene_M)):
            M[i] = evalA.M[i] if gene_M[i] else evalB.M[i]
        return eval(M)
    
    def mutate(self, mutation_rate = 0.1, mutation_factor = 0.2):
        for i in range(len(self.M)):
            if utils.simulate_probability(mutation_rate):
                self.M[i] += mutation_factor*np.random.default_rng().uniform(-100, 100, 1)

# Ma = np.ones(12)
# Mb = np.zeros(12)
# A = eval(Ma)
# B = eval(Mb)
# print(eval.breed(A, B).M)
