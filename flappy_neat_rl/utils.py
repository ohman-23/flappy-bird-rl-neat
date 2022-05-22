import numpy as np

def relu(cls, x):
    x[x < 0] = 0
    return x

def sigmoid(cls, x):
    return 1 / (1 + np.exp(-x))

def add_bias_term(cls, vec):
    if len(vec.shape) < 2:
        vec = vec.reshape((1, -1))
    new_vec = np.ones((1, len(vec[0]) + 1))
    new_vec[0, : len(vec[0])] = vec[0]
    return new_vec.reshape((1, -1))

def genetic_crossover(cls, genome):
    rand = np.random.random()
    if 0 < rand < 0.45:
        return 100.0
    if 0.45 < rand < 0.9:
        return 99.0
    return np.random.randn()
