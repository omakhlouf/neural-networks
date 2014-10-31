from numpy import *
from numpy.matlib import repmat


class Layer(object):
    def __init__(self, size):
        self.size = size
        self.bias = zeros((1, size))
        self.activities = zeros((1, size))

    def process(self, weighted_input):
        assert False, "This is an abstract class"

    def gradient(self):
        '''I'm having every layer compute it's own dy/dz 's, that way backprop can work with any layer
        type, where the layer provides backprop with dy/dz, using it's activity values '''
        assert False, "This is an abstract class"

    def repbias(self, data):
        '''Replicates the bias vector in so that it can be used in matrix operations with data'''
        return repmat(self.bias, data.shape[0], 1)


class LogisticLayer(Layer):
    def process(self, weighted_input):
        self.activities = 1/(1 + exp(-(weighted_input + self.repbias(weighted_input))))
        return self.activities

    def gradient(self):
        #In logistic units, dy/dz = y*(1-y)
        return self.activities * (1 - self.activities)


class BinaryStochasticLayer(LogisticLayer):
    def process(self, weighted_input):
        probs = LogisticLayer.process(self, weighted_input)
        self.activities = sample_binary_stochastic(probs)
        return self.activities


class LinearLayer(Layer):
    def process(self, weighted_input):
        self.activities = weighted_input + self.repbias(weighted_input)
        return self.activities


class BinaryThresholdLayer(Layer):
    def process(self, weighted_input):
        self.activities = ((weighted_input + self.repbias(weighted_input)) > zeros((1, self.size))).astype(int)
        return self.activities


class SoftMax(Layer):
    def normalizer(self, a):
        max_small = a.max(axis=1)
        max_big = repmat(max_small, self.size, 1).transpose()
        return log(exp(a - max_big).sum(1)) + max_small

    def process(self, weighted_input):
        normalizer = self.normalizer(weighted_input).reshape((1, weighted_input.shape[0]))
        log_prob = weighted_input - repmat(normalizer, self.size, 1).transpose()
        self.activities = exp(log_prob)
        return self.activities

    def gradient(self):
        return self.activities * (1 - self.activities)


def sample_binary_stochastic(probmat):
    return (probmat > random.random(probmat.shape)).astype(int)
