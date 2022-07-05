import neat
import numpy as np
import pygame
from flappy_neat_rl.enums import PlayerType
from flappy_neat_rl.players.player import Player
from flappy_neat_rl.utils import add_bias_term, genetic_crossover, relu, sigmoid, tanh


class BirdHumanPlayer(Player):
    def __init__(self):
        self.fitness = 0
        self.unique_jump = True

    def jump(self, *args, **kwargs):
        if pygame.key.get_pressed()[pygame.K_SPACE] and self.unique_jump:
            return True
        if not pygame.key.get_pressed()[pygame.K_SPACE] and not self.unique_jump:
            self.unique_jump = True
        return False

    def update_fitness(self, val):
        self.fitness += val

    def method(self):
        return PlayerType.HUMAN


class BirdNN:
    activations_supported = ["relu", "tanh", "sigmoid"]
    input_dim = 4
    output_dim = 1

    def __init__(self, hidden_layers=None, inner_dims=None, activation=None, weights=None):
        self.hidden_layers = hidden_layers
        self.inner_dims = inner_dims
        self.activation = activation
        self.weights = weights

        if self.hidden_layers is None:
            self.hidden_layers = 1
        if self.inner_dims is None:
            self.inner_dims = [3]
        if self.activation is None:
            self.activation = "sigmoid"
        if self.weights is None:
            self.weights = self._create_random_network()

        self.check_params()
        self.activation_function = self._assign_activation_function()

    def check_params(self):
        if self.hidden_layers == 0:
            raise ValueError("hidden layers cannot be 0")
        if self.hidden_layers != len(self.inner_dims):
            raise ValueError("mismatch between hidden_layers and provided dimension sizes")
        if self.weights is not None and len(self.weights) != (self.hidden_layers + 1):
            raise ValueError(
                "weight matrixes provided do not match dimensions specified for Neural Network"
            )
        if self.activation.lower() not in self.activations_supported:
            raise ValueError("activation function specified not supported")

    def _assign_activation_function(self):
        functions = {"relu": relu, "tanh": tanh, "sigmoid": sigmoid}
        return functions.get(self.activation)

    def _create_random_network(self):
        dims = [self.input_dim, *self.inner_dims, self.output_dim]
        dims = [(dims[i - 1], dims[i]) for i in range(1, len(dims))]
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
            if weight_mat_ind < len(self.weights) - 1:
                current_vec = self.activation_function(current_vec)
        return tanh(current_vec)

    def _create_random_weight_matrix(self, input_dim, output_dim):
        # the '+1' accounts for bias!
        W = np.random.normal(0, 1, size=(input_dim + 1, output_dim))
        return W

    def _random_mate(self, weights1, weights2):
        dim = weights1.shape
        child_layer, mask = np.zeros(dim), np.zeros(dim)
        crossover_func = np.vectorize(genetic_crossover)
        mask = crossover_func(mask)

        # DNA from parent A
        weights1[mask < 100.0] = 0
        child_layer += weights1

        # DNA from parent B
        weights2[mask != 99.0] = 0
        child_layer += weights2

        # DNA from mutation
        mask[mask >= 99.0] = 0
        child_layer += mask
        return child_layer

    def _random_split(self, weights1, weights2):
        pass

    def _random_preterbation(self, layer):
        rows, cols = layer.shape
        child_layer = np.zeros((rows, cols))
        for r in range(rows):
            for c in range(cols):
                weight = layer[r, c]
                if np.random.rand() > 0.2:
                    weight += np.random.normal(0, 1)
                child_layer[r, c] = weight
        return child_layer

    def mate(self, otherNN):
        # assume that the inputs for the current input and the next input will be the same:
        child_weights = []
        for i in range(len(self.weights)):
            this_layer = self.weights[i]
            other_layer = otherNN.weights[i]
            # child_layer = self._random_mate(this_layer, other_layer)
            child_layer = self._random_preterbation(this_layer)
            child_weights.append(child_layer)

        return BirdNN(
            hidden_layers=self.hidden_layers,
            inner_dims=self.inner_dims,
            activation=self.activation,
            weights=child_weights,
        )

    def copy(self):
        return BirdNN(
            hidden_layers=self.hidden_layers,
            inner_dims=self.inner_dims,
            activation=self.activation,
            weights=self.weights,
        )


class BirdNNPlayer(Player):
    def __init__(self, neural_network):
        self.neural_network = neural_network
        self.past_score = 0
        self.fitness = 0

    def jump(self, *args, **kwargs):
        input_vector = kwargs.get("input_vector", None)
        if input_vector is None:
            raise ValueError("Neural Network requires an input vector")

        output = self.neural_network.forward(input_vector)
        return True if output > 0.5 else False

    def mate(self, other_player):
        """Wrapper for the mating functionality of the BirdNN class"""
        child_network = self.neural_network.mate(other_player.neural_network)
        child = BirdNNPlayer(child_network)
        # print(self.neural_network.weights)
        # print(other_player.neural_network.weights)
        # print(child.neural_network.weights)
        return child

    def copy(self):
        return BirdNNPlayer(self.neural_network.copy())

    def update_fitness(self, val):
        self.fitness += val

    def method(self):
        return PlayerType.NEURAL_NETWORK


class BirdNEATPlayer(Player):
    def __init__(self, genome, neat_config):
        self.past_score = 0
        self.genome = genome
        self.nn = neat.nn.FeedForwardNetwork.create(self.genome, neat_config)

        # set fitness
        self.genome.fitness = 0

    def jump(self, *args, **kwargs):
        input_vector = kwargs.get("input_vector", None)
        if input_vector is None:
            raise ValueError("NEAT requires an input vector")

        output = self.nn.activate(input_vector)
        return True if output[0] > 0.5 else False

    def update_fitness(self, val):
        self.genome.fitness += val

    def method(self):
        return PlayerType.NEAT
