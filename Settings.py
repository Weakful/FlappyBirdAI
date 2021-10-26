class Settings(object):
    nnStructure = [2, 3, 1]
    numberOfIndividuals = 200
    numberofEliteWeBreed = 2
    numberofEliteWeKeep =  10
    numberofNewRandomIndividualPerGeneration = 100
    mutateRate = 0.02
    mutateElites = False
    fatherSelectionMethod = "elite"
    motherSelectionMethod = "roulette"
    mutateNewIndiv = True
    crossoverType = 1
    mutateVersion = 2
    scoreFitness = True
    maxGeneration = 2000
    maxScore = 100000
    updateNN = False
