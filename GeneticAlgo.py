import random, math, importlib
from NeuralNetwork import NeuralNetwork
from Settings import Settings

class Individual(object):
    fitness = 0
    score = 0

    def __init__(self, neuralNetwork = NeuralNetwork(Settings.nnStructure)):
        self.neuralNetwork = neuralNetwork
        self.genes = self.neuralNetwork.NNtoGenes()

    def __lt__(self, other): #for FindFittness' sort
        return self.fitness < other.fitness
    
    def GetGene(self,x):
        return self.genes[x]
    
    def SetGene(self,x,value):
        self.genes[x] = value
        if Settings.updateNN:
            self.neuralNetwork.GenesToNN(self.genes)
    
    def GetNN(self):
        return self.neuralNetwork

    def SetNN(self, neuralNetwork):
        self.neuralNetwork = neuralNetwork

    def Size(self):
        return len(self.genes)

    def Mutate(self, mutationRate):
        mutatedGenes = []

        if Settings.mutateVersion == 1: #mutateVersion 1
            needUpdate = False
            for gene in self.genes:
                if random.random() <= mutationRate:
                    gene = random.random()
                    needUpdate = True
                mutatedGenes.append(gene)
            self.genes = mutatedGenes
            if needUpdate and Settings.updateNN:
                self.neuralNetwork.GenesToNN(mutatedGenes)
            return

        if Settings.mutateVersion == 2: #mutateVersion 2
            needUpdate = False
            for gene in self.genes:
                if random.random() <= mutationRate:
                    gene = gene * random.uniform(-2, 2)
                    needUpdate = True
                mutatedGenes.append(gene)
            self.genes = mutatedGenes
            if needUpdate and Settings.updateNN:
                self.neuralNetwork.GenesToNN(mutatedGenes)
            return

class Population(object):
    def __init__(self):
        self.individuals = []

    def FindFittest(self,number = 1):
        fittest = []
        fittest = fittest + self.individuals
        fittest.sort(reverse = True)
        while len(fittest) > number:
            fittest.pop()
        if number==1:
            fittest=fittest[0]
        return fittest

    def GenerateRandomPopulation(self):
        for i in range(Settings.numberOfIndividuals):
            individual = GenerateRandomIndividual()
            self.individuals.append(individual)

    #evolves population for the next generation
    def EvolvePopulation(self):
        individuals = []
        
        #finding the individual we will breed and keep
        elitesWeBreed = self.FindFittest(Settings.numberofEliteWeBreed)
        elitesWeKeep = self.FindFittest(Settings.numberofEliteWeKeep)

        if Settings.mutateElites:
            for individual in elitesWeKeep:
                individual.Mutate(Settings.mutateRate)

        #selecting and mating parents
        for i in range(self.Size() - Settings.numberofEliteWeKeep - Settings.numberofNewRandomIndividualPerGeneration):
            if Settings.fatherSelectionMethod == "roulette":
                father = RouletteWheelSelection(self)
            elif Settings.fatherSelectionMethod == "tournament":
                father = TournamentSelection(self)
            elif Settings.fatherSelectionMethod == "fittest":
                father = self.FindFittest()
            else:
                father = RandomIndividual(elitesWeBreed)
            
            if Settings.motherSelectionMethod == "roulette":
                mother = RouletteWheelSelection(self)
            elif Settings.motherSelectionMethod == "tournament":
                mother = TournamentSelection(self)
            else:
                mother = RandomIndividual(elitesWeBreed)

            newIndiv = self.Crossover(father, mother)
            if Settings.mutateNewIndiv:
                newIndiv.Mutate(Settings.mutateRate)

            individuals.append(newIndiv)

        #adding random individuals to the population
        for i in range(Settings.numberofNewRandomIndividualPerGeneration):
            newIndiv = GenerateRandomIndividual()

            if Settings.mutateNewIndiv:
                newIndiv.Mutate(Settings.mutateRate)
            individuals.append(newIndiv)

        #adding the newborn individuals and randomly generated individuals together with the elites we keep
        if Settings.numberofEliteWeKeep !=1:
            individuals = elitesWeKeep + individuals
        else:
            individuals = individuals.append(elitesWeKeep)
        
        self.individuals = individuals

    def Crossover(self,individualLeft, individualRight):
        if type(individualRight) == type(None):
            individualRight = RandomIndividual(self.individuals)
        if type(individualLeft) == type(None):
            individualLeft = RandomIndividual(self.individuals)

        if Settings.crossoverType == 1: #crossover 1: 
            individual = Individual()
            for i in range(individualLeft.Size()):
                if random.random() <= 0.5:
                    individual.SetGene(i, individualLeft.GetGene(i))
                else:
                    individual.SetGene(i, individualRight.GetGene(i))
            return individual

        if Settings.crossoverType == 2: #crossover 2
            individual = Individual()
            rand1 = random.randint(1, individualLeft.Size())
            rand2 = random.random()
            for i in range(individualLeft.Size()):
                if i < rand1:
                    if rand2 <= 0.5:
                        individual.SetGene(i, individualLeft.GetGene(i))
                    else:
                        individual.SetGene(i, individualRight.GetGene(i))
                else:
                    if rand2 <= 0.5:
                        individual.SetGene(i, individualRight.GetGene(i))
                    else:
                        individual.SetGene(i, individualLeft.GetGene(i))
            return individual

    def AddNewIndividual(self, individual):
        self.individuals.append(individual)

    def SetFitnessOfIndividual(self,i,fitness):
        self.individuals[i].fitness = fitness

    def GetIndividual(self,i):
        return self.individuals[i]

    def AverageFitness(self):
        fitness = []
        for i in self.individuals:
            fitness.append(i.fitness)
        return sum(fitness) / float(len(fitness))

    def Size(self):
        return len(self.individuals)

def GenerateRandomIndividual():
    neuralNetwork = NeuralNetwork(Settings.nnStructure)
    individual = Individual(neuralNetwork)
    return individual

def RandomIndividual(individuals):
    i = random.randint(0,len(individuals) - 1)
    return individuals[i]

def TournamentSelection(population):
    tournament = Population()
    for i in range(5):
        randomInt = random.randint(0,population.Size() - 1)
        tournament.AddNewIndividual(population.individuals[randomInt])
    fittest = tournament.FindFittest()
    return fittest

def RouletteWheelSelection(population):
    SumOfFitnesses = sum([individual.fitness for individual in population.individuals])
    rouletteChoice = random.uniform(0, SumOfFitnesses)
    current = 0
    for individual in population.individuals:
        current += individual.fitness
        if current >= rouletteChoice:
            return individual
