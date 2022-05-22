import numpy as np
from flappy_neat_rl.utils import (relu, sigmoid, genetic_crossover, add_bias_term)
from player import Player, PlayerType

class BirdNN:
    activations_supported = ("relu")
    input_dim = 3
    output_dim = 1
    
    def __init__(self, hidden_layers=None, inner_dims=None, activation=None, weights=None):
        self.hidden_layers = hidden_layers
        self.inner_dims = inner_dims
        self.activation = activation
        self.weights = weights
        
        if self.hidden_layers is None:
            self.hidden_layers = 1
        if self.inner_dims is None:
            self.inner_dims = [6]
        if self.activation is None:
            self.activation = 'relu'
        if self.weights is None:
            self.weights = self._create_random_network()
            
        self.check_params()
        self.activation_function = self._assign_activation_function()
        
    def check_params(self):
        if self.hidden_layers == 0:
            raise ValueError("hidden layers cannot be 0")
        if self.hidden_layers != len(self.inner_dims):
            raise ValueError("mismatch between hidden_layers and provided dimension sizes")
        if self.weights is not None and len(self.weights) != (self.hidden_layers+1):
            raise ValueError("weight matrixes provided do not match dimensions specified for Neural Network")
        if self.activation.lower() not in self.activations_supported:
            raise ValueError("activation function specified not supported")
    
    def _assign_activation_function(self):
        functions = {'relu':relu}
        return functions.get(self.activation)
        
    def _create_random_network(self):
        dims = [self.input_dim, *self.inner_dims , self.output_dim]
        dims = [(dims[i-1], dims[i]) for i in range(1, len(dims))]
        weights = []
        for matsize in dims:
            weights.append(self._create_random_weight_matrix(matsize[0], matsize[1]))
        return weights
            
    def forward(self, input_vec):
        current_vec = input_vec
        for weight_mat_ind in range(len(self.weights)):
            weight_mat = self.weights[weight_mat_ind]
            current_vec = add_bias_term(current_vec)
            # (1,n+1) * (n+1, m) = (1, m)
            current_vec = np.dot(current_vec, weight_mat)
            if weight_mat_ind < len(self.weights)-1:
                current_vec = self.activation_function(current_vec)
        return sigmoid(current_vec)
            
    def _create_random_weight_matrix(self, input_dim, output_dim):
        # the '+1' accounts for bias!
        W = np.random.normal(0,1, size=(input_dim+1, output_dim))
        # normalize just in case
        MAX = np.max(W)
        W = W/MAX
        return W

    
    def mate(self, otherNN):
        # assume that the inputs for the current input and the next input will be the same:
        child_weights = []
        for i in range(len(self.weights)):
            this_layer = self.weights[i]
            other_layer = otherNN.weights[i]
            dim = this_layer.shape
            child_layer, mask = np.zeros(dim), np.zeros(dim)
            crossover_func = np.vectorize(genetic_crossover)
            mask = crossover_func(mask)
            
            # DNA from parent A
            this_layer[mask<100.0] = 0
            child_layer += this_layer
            
            # DNA from parent B
            other_layer[mask!=99.0] = 0
            child_layer += other_layer
            
            # DNA from mutation
            mask[mask>=99.0] = 0
            child_layer += mask
            
            child_weights.append(child_layer)
        return BirdNN(hidden_layers=self.hidden_layers, inner_dims=self.inner_dims, activation="relu", weights=child_weights)

class BirdNNPlayer(Player):
    def __init__(self, neural_network):
        self.neural_network = neural_network
        self.score = 0
        self.time_alive = 0
    
    def jump(self, *args, **kwargs):
        input_vector = kwargs.get("input_vector", None)
        if input_vector is None:
            raise BaseException("Neural Network requires an input vector")
        output = self.neural_network.forward(input_vector)
        return True if output > 0.5 else False 

    def mate(self, other_player):
        """ Wrapper for the mating functionality of the BirdNN class """
        child_network = self.neural_network.mate(other_player.neural_network)
        return BirdNNPlayer(child_network)

    def set_score(self, score):
        self.score = score

    def set_time_alive(self, time_alive):
        self.time_alive = time_alive

    def method(self):
        return PlayerType.NEURAL_NETWORK
        