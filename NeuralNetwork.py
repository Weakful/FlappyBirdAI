import random, os, time
import numpy as np
import json

class NeuralNetwork(object):
    def __init__(self, layers, weights=0, biases=0):
        self.layers = layers
        self.weights = weights
        self.biases = biases

        self.numberOfLayers = len(layers)
        self.numberOfWeights = 0
        for i in range (1, len(self.layers)):
            self.numberOfWeights += self.layers[i] * self.layers[i-1]
        self.numberOfBiases = sum(self.layers[1:])

        if weights == 0:
            self.weights = [np.random.randn(y, x) for x, y in zip(layers[:-1], layers[1:])]      
        if biases == 0:
            self.biases = [np.random.randn(y, 1) for y in layers[1:]]

    def FeedForward(self, x):
        for bias, weight in zip(self.biases, self.weights):
            x = Sigmoid(np.dot(weight, x) + bias)
        return x

    def GetBias(self, layer, output):
        return self.biases[layer][output]

    def SetBias(self, layer, output, value):
        self.biases[layer][output] = value

    def GetWeight(self, layer, output, input):
        return self.weights[layer][output][input]

    def SetWeight(self, layer, output, input, value):
        self.weights[layer][output][input] = value

    def NNtoGenes(self):
        genes = []
        for x in range(0, (self.numberOfLayers - 1)):
            for y in range(0, (self.layers[x + 1])):
                genes.extend(self.weights[x][y])

        for x in range(len(self.biases)):
            for element in self.biases[x]:
                genes.extend(element)

        return genes
    
    def GenesToNN(self, genes):
        counter = 0
        for x in range(len(self.weights)):
            for y in range(len(self.weights[x])):
                    for i in range(len(self.weights[x][y])):
                        self.SetWeight(x, y, i, genes[counter])
                        counter += 1

        for x in range(len(self.biases)):
            for y in range(len(self.biases[x])):
                self.SetBias(x, y, genes[counter])
                counter += 1

    def Save(self, filename):
        data = {"layers": self.layers,
                "weights": [w.tolist() for w in self.weights],
                "biases": [b.tolist() for b in self.biases]}
        saveDir = os.path.dirname(filename)
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        f = open(filename, "w")
        json.dump(data, f)
        f.close()

def Load(filename):
    f = open(filename, "r")
    data = json.load(f)
    f.close()
    nn = NeuralNetwork(data["layers"], [np.array(w) for w in data["weights"]], [np.array(b) for b in data["biases"]])
    return nn

def Sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))
