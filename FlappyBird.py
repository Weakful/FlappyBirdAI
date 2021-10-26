#imports
import pygame, sys, os, os.path
from pygame.locals import *
from time import gmtime, strftime
import random
import numpy as np
import matplotlib
from matplotlib.ticker import FormatStrFormatter
matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg
import pylab

from GeneticAlgo import *
from NeuralNetwork import NeuralNetwork, Load
from Settings import Settings

#initializing pygame
pygame.init()
pygame.display.set_caption("Flappy Bird")

os.system('cls')
print("Game is running...")

#globals
global frames
frames = 30
global pause
pause = False
global screenUpdate
screenUpdate = True
gameScreenwidth = 288
statScreenwidth = gameScreenwidth
screenheight = 512
gap = screenheight * 0.2
floorY = screenheight * 0.8

#setting screen and clock for pygame
screen = pygame.display.set_mode((gameScreenwidth,screenheight))
clock = pygame.time.Clock()

#loading pictures for the game
background = pygame.image.load("images/background.png").convert_alpha()
floor = pygame.image.load("images/floor.png").convert_alpha()
bird = pygame.image.load("images/bird.png").convert_alpha()
pipeBottom = pygame.image.load("images/pipe.png").convert_alpha()
pipeTop = pygame.transform.flip(pygame.image.load("images/pipe.png").convert_alpha(), False, True)
numbers = (
    pygame.image.load('images/0.png').convert_alpha(),
    pygame.image.load('images/1.png').convert_alpha(),
    pygame.image.load('images/2.png').convert_alpha(),
    pygame.image.load('images/3.png').convert_alpha(),
    pygame.image.load('images/4.png').convert_alpha(),
    pygame.image.load('images/5.png').convert_alpha(),
    pygame.image.load('images/6.png').convert_alpha(),
    pygame.image.load('images/7.png').convert_alpha(),
    pygame.image.load('images/8.png').convert_alpha(),
    pygame.image.load('images/9.png').convert_alpha()
)

#for the diagram during learning
fig = pylab.figure(figsize=[4, 4],
                   dpi=72,
                   )

#button class
class Button:

    def __init__(self, x, y, w, h, text=['']):
        self.rect = pygame.Rect(x - (w / 2), y - (h / 2), w, h)
        self.color = pygame.Color('white')
        self.textArray = text
        self.text = text[0]
        self.currIndex = 0
        self.txt_surface = pygame.font.Font(None, 26).render(self.text, True, self.color)
        self.clicked = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                if len(self.textArray) == 1:
                    self.clicked = not self.clicked
                else:
                    self.currIndex += 1
                    if self.currIndex >= len(self.textArray):
                        self.currIndex = 0
                    self.text = self.textArray[self.currIndex]
                self.txt_surface = pygame.font.Font(None, 26).render(self.text, True, self.color)

    def draw(self, screen):
        # Blit the background.
        pygame.draw.rect(screen, pygame.Color('black'), self.rect)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

#text input class
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x - (w / 2), y - (h / 2), w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = pygame.font.Font(None, 26).render(self.text, True, pygame.Color('white'))
        self.active = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = pygame.font.Font(None, 26).render(self.text, True, pygame.Color('white'))

    def draw(self, screen):
        # Blit the background.
        pygame.draw.rect(screen, pygame.Color('black'), self.rect)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

#function for easier use of text in pygame
def put_text(text, x, y, align = "center"):
    text_surface = pygame.font.Font(None, 26).render(text, True, pygame.Color('white'))
    temp_surface = pygame.Surface(text_surface.get_size())
    temp_surface.fill(pygame.Color('black'))
    temp_surface.blit(text_surface, (0, 0))
    if align == "center":
        screen.blit(temp_surface, (x - (temp_surface.get_width() / 2), y - (temp_surface.get_height() / 2)))
    elif align == "right":
        screen.blit(temp_surface, (x - (temp_surface.get_width()), y - (temp_surface.get_height() / 2)))
    elif align == "left":
        screen.blit(temp_surface, (x, y - (temp_surface.get_height() / 2)))

#hitmask function to make boolean matrices of pictures
def GetHitmask(image):
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

#making hitmasks for the pictures
bird_hitmask = GetHitmask(bird)
pipeTop_hitmask = GetHitmask(pipeTop)
pipeBottom_hitmask = GetHitmask(pipeBottom)

#gameplay function
def PlayGame(individual = 0):
    #setting score and the number of frames survived and setting the starting position of the bird
    score = 0
    numberOfFramesSurvived = 0
    birdX, birdY = int(gameScreenwidth * 0.2), int(screenheight * 0.5)

    #generating our first sets of pipes
    newPipe1 = GenerateRandomPipe()
    newPipe2 = GenerateRandomPipe()
    newPipe3 = GenerateRandomPipe()
    newPipe4 = GenerateRandomPipe()

    upperPipes = [
        {'x': gameScreenwidth + (gameScreenwidth / 2), 'y': newPipe1[0]['y']},
        {'x': gameScreenwidth * 2, 'y': newPipe2[0]['y']},
        {'x': (gameScreenwidth * 2) + (gameScreenwidth / 2), 'y': newPipe3[0]['y']},
        {'x': (gameScreenwidth * 3), 'y': newPipe4[0]['y']},
    ]

    lowerPipes = [
        {'x': gameScreenwidth + (gameScreenwidth / 2), 'y': newPipe1[1]['y']},
        {'x': gameScreenwidth * 2, 'y': newPipe2[1]['y']},
        {'x': (gameScreenwidth * 2) + (gameScreenwidth / 2), 'y': newPipe3[1]['y']},
        {'x': (gameScreenwidth * 3), 'y': newPipe4[1]['y']},
    ]

    pipeVelX = -4 #speed of the pipeson the x axis
    birdVelY = -9 #beginning speed of the bird on the y axis
    birdMaxVelY = 11 #maximum speed of the bird on the y axis
    birdAccY = 1 #the speed at which the bird accelerates on the y axis
    birdFlapAcc = -9 #the speed of the bird on the y axis after every flap
    birdFlapped = False #whether the bird flapped on this loop
    birdRot =  45 #the rotation of the bird
    birdVelRot = 3 #the speed at which we rotate the bird
    RotationThreshold = 25 #minimum rotation of the bird
    floorX = 0 #the floor's location on the x axis

    #globals we need to set speed and turn screen update on or off
    global frames
    global screenUpdate
    #globals we need during learning, pause to handle pausing and the rest for information during learning
    global pause
    global currGeneration
    global bestScore
    global bestFitness
    global generationFitnesses
    global generationsFittests
    global currentIndiv
    global topAvg
    global surf
    global fittestOfLast

    #main gameloop
    while True:
        #handling user events
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE and individual == 0:
                #flapping when space key is pressed during user gameplay
                if birdY > -2 * bird.get_height():
                    birdVelY = birdFlapAcc
                    birdFlapped = True
            if event.type == KEYDOWN and event.key == K_UP and individual != 0:
                frames = 300000
            if event.type == KEYDOWN and event.key == K_DOWN and individual != 0:
                frames = 30
            if event.type == KEYDOWN and event.key == K_s and individual != 0:
                screenUpdate = not screenUpdate
            if event.type == KEYDOWN and event.key == K_p and individual != 0:
                pause = not pause

        #if AI gameplay then calculate whether the bird should flap
        if individual != 0:
            #setting the pipe that's next
            if birdX < upperPipes[0]['x'] + 40:
                firstPipe = upperPipes[0]
            else:
                firstPipe = upperPipes[1]
            
            #position of the pipe on the Y axis
            firstPipeYForNN = float(screenheight - firstPipe['y']) / screenheight
            #position of the bird on the Y axis
            birdYForNN = float(screenheight - birdY) / screenheight
            #the pipes X coordinate, we don't need to measure it against the birds x coordinate, because the birds x coordinate is fix 
            pipeDistance = float(firstPipe['x']) / gameScreenwidth

            #creating input array and calculating output
            inputOfNN = np.array([[firstPipeYForNN - birdYForNN], [pipeDistance]])
            outputOfNN = individual.neuralNetwork.FeedForward(inputOfNN)

            #flapping
            if outputOfNN > 0.5:
                if birdY > -2 * bird.get_height():
                        birdVelY = birdFlapAcc
                        birdFlapped = True

        #checking for crash
        isCrash = CheckForCrash(birdX, birdY, upperPipes, lowerPipes)
        if (isCrash or birdY < 5) and individual == 0:
            return score
        if (isCrash or birdY < 5) and individual != 0:
            if Settings.scoreFitness:
                individual.fitness = score
            else:
                individual.fitness = numberOfFramesSurvived
            individual.score = score
            return individual

        #returning if maxscore is reached during AI gameplay
        if score >= Settings.maxScore and individual != 0:
            if Settings.scoreFitness:
                individual.fitness = score
            else:
                individual.fitness = numberOfFramesSurvived
            individual.score = score
            return individual
        
        numberOfFramesSurvived += 1

        #adding to score if bird passed through a pair of pipes
        birdMiddle = birdX + bird.get_width() / 2
        for pipe in upperPipes:
            pipePos = pipe['x'] + pipeTop.get_width()
            if pipePos <= birdMiddle < pipePos + 4:
                score += 1

        #bird rotation, speed and movement
        if birdRot > -90:
            birdRot -= birdVelRot

        if birdVelY < birdMaxVelY and not birdFlapped:
            birdVelY += birdAccY
        if birdFlapped:
            birdFlapped = False
            birdRot = 45

        birdHeight = bird.get_height()
        birdY += min(birdVelY, floorY - birdY - birdHeight)

        visibleRot = RotationThreshold
        if birdRot <= RotationThreshold:
            visibleRot = birdRot

        #movement, deletion and creation of pipes
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = GenerateRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        if len(upperPipes) > 0 and upperPipes[0]['x'] < -pipeTop.get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        #drawing on screen from here       
        if screenUpdate:
            screen.blit(background, (0,0))
            screen.blit(background, (gameScreenwidth, 0))

            for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
                screen.blit(pipeTop, (upperPipe['x'], upperPipe['y']))
                screen.blit(pipeBottom, (lowerPipe['x'], lowerPipe['y']))

            screen.blit(floor, (floorX, floorY))
            screen.blit(floor, (floorX + gameScreenwidth, floorY))
            screen.blit(floor, (floorX + (2 * gameScreenwidth), floorY))

            floorX -= 1
            if floorX <= 0 - gameScreenwidth:
                floorX = 0
            
            birdSurface = pygame.transform.rotate(bird, visibleRot)
            screen.blit(birdSurface, (birdX, birdY))

            #write score on top of the screen
            numberOfDigits = [int(x) for x in list(str(score))]
            digitsWidth = 0
            for digit in numberOfDigits:
                digitsWidth += numbers[digit].get_width()
            pushToTheSide = (gameScreenwidth - digitsWidth) / 2
            for digit in numberOfDigits:
                screen.blit(numbers[digit], (pushToTheSide, screenheight * 0.05))
                pushToTheSide += numbers[digit].get_width()
            
            #information during learning
            if 'currGeneration' in globals():
                fitnesses = 0
                if currGeneration > 1:
                    fitnesses = generationFitnesses[-1]
                    
                put_text("Current Generation: " + str(currGeneration), gameScreenwidth + statScreenwidth - 40, 20, "right")
                put_text("Current Individual: " + str(currentIndiv), gameScreenwidth + statScreenwidth - 40, 40, "right")
                put_text("Avg fitness of last gen: " + str(round(fitnesses, 2)), gameScreenwidth + statScreenwidth - 40, 80, "right")
                put_text("Best fitness of last gen: " + str(fittestOfLast), gameScreenwidth + statScreenwidth - 40, 100, "right")
                put_text("Best fitness so far: " + str(bestFitness), gameScreenwidth + statScreenwidth - 40, 120, "right")
                put_text("Best score so far: " + str(bestScore), gameScreenwidth + statScreenwidth - 40, 140, "right")
                put_text("Avg fitness of elites:", gameScreenwidth + statScreenwidth - 40, 200, "right")

                if pause:
                    put_text("Pausing after this gen.", gameScreenwidth / 2, screenheight - 15)

                screen.blit(surf, (statScreenwidth, screenheight - 288))

            pygame.display.update()
        clock.tick(frames)

#generate a random pair of pipes
def GenerateRandomPipe():
    gapY = random.randrange(0, int(floorY * 0.6 - gap))
    gapY += int(floorY * 0.2)
    pipeHeight = pygame.image.load("images/pipe.png").convert_alpha().get_height()
    pipeX = gameScreenwidth + gameScreenwidth + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},
        {'x': pipeX, 'y': gapY + gap},
    ]

#check whether the bird crashed or not
def CheckForCrash(birdX, birdY, upperPipes, lowerPipes):
    birdwidth = bird.get_width()
    birdHeight = bird.get_height()

    if birdY + birdHeight >= floorY:
        return True
    else:

        birdRect = pygame.Rect(birdX, birdY,
                      birdwidth, birdHeight)
        pipeWidth = pipeTop.get_width()
        pipeHeight = pipeBottom.get_height()

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipeRect = pygame.Rect(upperPipe['x'], upperPipe['y'], pipeWidth, pipeHeight)
            lowerPipeRect = pygame.Rect(lowerPipe['x'], lowerPipe['y'], pipeWidth, pipeHeight)

            Collide = CollisionPixelByPixel(birdRect, upperPipeRect, bird_hitmask, pipeTop_hitmask) or CollisionPixelByPixel(birdRect, lowerPipeRect, bird_hitmask, pipeBottom_hitmask) 

            if Collide:
                return True

    return False

#checking collision with the use of hitmasks
def CollisionPixelByPixel(rect1, rect2, hitmask1, hitmask2):
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1 = rect.x - rect1.x
    y1 = rect.y - rect1.y
    x2 = rect.x - rect2.x
    y2 = rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False

#genetic algorithm function
def LearnGame():
    global screenUpdate
    screenUpdate = True
    population = Population()
    population.GenerateRandomPopulation()
    global currGeneration
    currGeneration = 1
    global bestFitness
    bestFitness = 0
    global bestScore
    bestScore = 0
    global bestIndividual
    bestIndividual = Individual()
    global generationFitnesses
    generationFitnesses = []
    global generationsFittests
    generationsFittests = []
    global currentIndiv
    currentIndiv = 0
    global topAvg
    topAvg = []
    global pause
    global surf
    global fittestOfLast
    fittestOfLast = 0

    #initializing diagram
    ax = fig.gca()
    ax.plot(topAvg)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    surf = pygame.image.fromstring(raw_data, (288, 288), "RGB")

    #genetic algorithm going through the generations, making individuals play and making data that will be shown during learning
    while currGeneration <= Settings.maxGeneration:
        for i in range(population.Size()):

            print("Current Generation:", currGeneration, "| Size of Pop:", population.Size(), "| Number Over Population:", i + 1)
            currentIndiv = i + 1
            currIndividual = PlayGame(population.GetIndividual(i))
            if currIndividual.fitness > bestFitness:
                bestFitness = currIndividual.fitness
                bestIndividual = currIndividual
                bestScore = currIndividual.score
        
        generationFitnesses.append(population.AverageFitness())
        print("Current Generation:", currGeneration, "| Avg Fitness:", generationFitnesses[len(generationFitnesses) - 1])
        generationsFittests.append(population.FindFittest())
        fittestOfLast = generationsFittests[len(generationsFittests) - 1].fitness
        print("Current Generation:", currGeneration, "| Top Fitness:", fittestOfLast)
        topIndividuals = population.FindFittest(Settings.numberofEliteWeKeep)
        popOfTop = Population()
        for individual in topIndividuals:
            popOfTop.AddNewIndividual(individual)
        topAvg.append(popOfTop.AverageFitness())

        #dupdating diagram
        ax.clear()
        ax = fig.gca()
        ax.plot(topAvg)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness")
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        surf = pygame.image.fromstring(raw_data, (288, 288), "RGB")
        print("Best Fitness so far:", bestFitness)
        if pause:
            PauseScreen()
            pause = not pause
        population.EvolvePopulation()
        currGeneration += 1
    
    #saving the best individual
    saveLocation = "saves/" + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".json"
    bestIndividual.neuralNetwork.Save(saveLocation)

    return bestScore

#the screen of the opening menu
def OpeningScreen():
    global screenUpdate
    screenUpdate = True
    buttons = [Button((gameScreenwidth / 2), screenheight / 2 - 100, 140, 26, ["Teach AI"]), Button((gameScreenwidth / 2), screenheight / 2 - 50, 140, 26, ["Make AI play"]), Button((gameScreenwidth / 2), screenheight / 2, 140, 26, ["Play yourself"])]
    text = "Welcome to Flappy Bird"
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)
                if button.clicked and button.text == "Teach AI":
                    return "learn"
                if button.clicked and button.text == "Make AI play":
                    return "ai"
                if button.clicked and button.text == "Play yourself":
                    return "play"

        screen.blit(background, (0,0))
        screen.blit(floor, (0, floorY))
        put_text(text, gameScreenwidth / 2, 30)
        for button in buttons:
            button.draw(screen)
        pygame.display.update()
        clock.tick(frames)

#the screen of the ending menu
def EndingScreen(score, mode):
    global screenUpdate
    screenUpdate = True
    buttons = [Button((gameScreenwidth / 2), screenheight / 2 - 100, 140, 26, ["Teach AI"]), Button((gameScreenwidth / 2), screenheight / 2 - 50, 140, 26, ["Make AI play"]), Button((gameScreenwidth / 2), screenheight / 2, 140, 26, ["Play yourself"]), Button((gameScreenwidth / 2), screenheight / 2 + 50, 140, 26, ["Quit"])]
    if mode == "learn":
        text = "Highest score was: " + str(score)
    else:
        text = "Score: " + str(score)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)
                if button.clicked and button.text == "Teach AI":
                    return "learn"
                if button.clicked and button.text == "Make AI play":
                    return "ai"
                if button.clicked and button.text == "Play yourself":
                    return "play"
                if button.clicked and button.text == "Quit":
                    return "end"

        screen.blit(background, (0,0))
        screen.blit(floor, (0, floorY))
        put_text(text, gameScreenwidth / 2, 30)
        for button in buttons:
            button.draw(screen)
        pygame.display.update()
        clock.tick(frames)

#setting screen of the genetic algorithm
def SettingScreen():
    global screenUpdate
    screenUpdate = True
    boxes = [InputBox((gameScreenwidth / 2), 45, 140, 26), InputBox((gameScreenwidth / 2), 100, 140, 26), InputBox((gameScreenwidth / 2), 155, 140, 26), InputBox((gameScreenwidth / 2), 210, 140, 26), InputBox((gameScreenwidth / 2), 265, 140, 26), Button((gameScreenwidth / 2), 320, 140, 26, ["New value", "Multiply value"]), Button((gameScreenwidth / 2), 375, 140, 26, ["Random", "One point flip"]), Button(gameScreenwidth + (statScreenwidth / 2), 45, 140, 26, ["Roulette", "Tournament", "Fittest", "Random Elite"]), Button(gameScreenwidth + (statScreenwidth / 2), 100, 140, 26, ["Roulette", "Tournament", "Random Elite"]), InputBox(gameScreenwidth + (statScreenwidth / 2), 155, 140, 26), Button(gameScreenwidth + (statScreenwidth / 2), 210, 140, 26, ["Yes", "No"]), Button(gameScreenwidth + (statScreenwidth / 2), 265, 140, 26, ["Yes", "No"]), Button(gameScreenwidth + (statScreenwidth / 2), 320, 140, 26, ["Score", "Frames alive"]), Button(gameScreenwidth + (statScreenwidth / 2), 375, 140, 26, ["Yes", "No"])]
    button = Button((gameScreenwidth), screenheight - 50, 140, 26, ["Confirm"])
    texts = ["Max generations:", "Generation size:", "Elites to breed:", "Elites to keep:", "Random individuals per gen.:", "Mutation type:", "Crossover type:", "Father selection type:", "Mother selection type", "Mutation rate (% like: 0.02):", "Mutate elites:", "Mutate newborn:", "Fitness:", "Use Crossover/Mutation:"]
    warningText = "Numbers don't add up properly."
    messedUp = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            for box in boxes:
                box.handle_event(event)
            button.handle_event(event)
            if button.clicked:
                try:
                    if int(boxes[0].text.strip() or 0) > 0 and int(boxes[1].text.strip() or 0) >= 0 and int(boxes[2].text.strip() or 0) > 0 and  int(boxes[3].text.strip() or 0) > 0 and int(boxes[4].text.strip() or 0) > 0 and float(boxes[9].text.strip() or 0) >= 0 and float(boxes[9].text.strip() or 0) <= 1 and int(boxes[2].text.strip() or 0) <= int(boxes[3].text.strip() or 0) and int(boxes[3].text.strip() or 0) + int(boxes[4].text.strip() or 0) <= int(boxes[1].text.strip() or 0):
                        Settings.maxGeneration = int(boxes[0].text.strip() or 0)
                        Settings.numberOfIndividuals = int(boxes[1].text.strip() or 0)
                        Settings.numberofEliteWeBreed = int(boxes[2].text.strip() or 0)
                        Settings.numberofEliteWeKeep = int(boxes[3].text.strip() or 0)
                        Settings.numberofNewRandomIndividualPerGeneration = int(boxes[4].text.strip() or 0)

                        if boxes[5].text == "New value":
                            Settings.mutateVersion = 1
                        else:
                            Settings.mutateVersion = 2

                        if boxes[6].text == "Random":
                            Settings.crossoverType = 1
                        else:
                            Settings.crossoverType = 2

                        if boxes[7].text == "Roulette":
                            Settings.fatherSelectionMethod = "roulette"
                        elif boxes[7].text == "Tournament":
                            Settings.fatherSelectionMethod = "tournament"
                        elif boxes[7].text == "Fittest":
                            Settings.fatherSelectionMethod = "fittest"
                        else:
                            Settings.fatherSelectionMethod = "elite"

                        if boxes[8].text == "Roulette":
                            Settings.motherSelectionMethod = "roulette"
                        elif boxes[8].text == "Tournament":
                            Settings.motherSelectionMethod = "tournament"
                        else:
                            Settings.motherSelectionMethod = "elite"

                        Settings.mutateRate = float(boxes[9].text.strip() or 0)

                        if boxes[10].text == "No":
                            Settings.mutateElites = False
                        else:
                            Settings.mutateElites = True
                        
                        if boxes[11].text == "No":
                            Settings.mutateNewIndiv = False
                        else:
                            Settings.mutateNewIndiv = True

                        if boxes[12].text == "Score":
                            Settings.scoreFitness = True
                        else:
                            Settings.scoreFitness = False

                        if boxes[13].text == "Yes":
                            Settings.updateNN = True
                        else:
                            Settings.updateNN = False
                        return
                    else:
                        button.clicked = False
                        messedUp = True
                except ValueError:
                    button.clicked = False
                    messedUp = True

        screen.blit(background, (0,0))
        screen.blit(background, (gameScreenwidth,0))
        screen.blit(floor, (0, floorY))
        screen.blit(floor, (gameScreenwidth, floorY))
        for i in range(len(texts)):
            if i < 7:
                put_text(texts[i], gameScreenwidth / 2, 20 + i * 55)
            else:
                put_text(texts[i], gameScreenwidth + statScreenwidth / 2, 20 + (i - 7) * 55)
        for box in boxes:
            box.draw(screen)
        button.draw(screen)
        if messedUp:
            put_text(warningText, gameScreenwidth, screenheight - 15)
        pygame.display.update()
        clock.tick(frames)
    return

#setting screen of the genetic algorithm during pauses
def PauseScreen():
    global screenUpdate
    screenUpdate = True
    boxes = [InputBox((gameScreenwidth / 2), 35, 140, 26), InputBox((gameScreenwidth / 2), 85, 140, 26), InputBox((gameScreenwidth / 2), 135, 140, 26), Button((gameScreenwidth / 2), 185, 140, 26, ["New value", "Multiply value"]), Button((gameScreenwidth / 2), 235, 140, 26, ["Random", "One point flip"]), Button((statScreenwidth / 4), 285, 140, 26, ["Roulette", "Tournament", "Fittest", "Random Elite"]), Button((statScreenwidth / 4) * 3, 285, 140, 26, ["Roulette", "Tournament", "Random Elite"]), InputBox((statScreenwidth / 2), 335, 140, 26), Button((statScreenwidth / 2), 385, 140, 26, ["Yes", "No"]), Button((statScreenwidth / 2), 435, 140, 26, ["Yes", "No"])]
    button = Button((gameScreenwidth / 2), screenheight - 40, 140, 26, ["Confirm"])
    texts = ["Elites to breed:", "Elites to keep:", "Random individuals per gen.:", "Mutation type:", "Crossover type:", "Selection types", "Mutation rate (% like: 0.02):", "Mutate elites:", "Mutate newborn:"]
    warningText = "Numbers don't add up properly."
    messedUp = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            for box in boxes:
                box.handle_event(event)
            button.handle_event(event)
            if button.clicked:
                try:
                    if int(boxes[0].text.strip() or 0) > 0 and int(boxes[1].text.strip() or 0) >= 0 and  int(boxes[2].text.strip() or 0) > 0 and float(boxes[7].text.strip() or 0) >= 0 and float(boxes[7].text.strip() or 0) <= 1 and int(boxes[0].text.strip() or 0) <= int(boxes[1].text.strip() or 0) and int(boxes[1].text.strip() or 0) + int(boxes[2].text.strip() or 0) <= Settings.numberOfIndividuals:
                        Settings.numberofEliteWeBreed = int(boxes[0].text.strip() or 0)
                        Settings.numberofEliteWeKeep = int(boxes[1].text.strip() or 0)
                        Settings.numberofNewRandomIndividualPerGeneration = int(boxes[2].text.strip() or 0)

                        if boxes[3].text == "New value":
                            Settings.mutateVersion = 1
                        else:
                            Settings.mutateVersion = 2

                        if boxes[4].text == "Random":
                            Settings.crossoverType = 1
                        else:
                            Settings.crossoverType = 2

                        if boxes[5].text == "Roulette":
                            Settings.fatherSelectionMethod = "roulette"
                        elif boxes[5].text == "Tournament":
                            Settings.fatherSelectionMethod = "tournament"
                        elif boxes[5].text == "Fittest":
                            Settings.fatherSelectionMethod = "fittest"
                        else:
                            Settings.fatherSelectionMethod = "elite"

                        if boxes[6].text == "Roulette":
                            Settings.motherSelectionMethod = "roulette"
                        elif boxes[6].text == "Tournament":
                            Settings.motherSelectionMethod = "tournament"
                        else:
                            Settings.motherSelectionMethod = "elite"

                        Settings.mutateRate = float(boxes[7].text.strip() or 0)

                        if boxes[8].text == "Yes":
                            Settings.mutateElites = True
                        else:
                            Settings.mutateElites = False
                        
                        if boxes[9].text == "Yes":
                            Settings.mutateNewIndiv = True
                        else:
                            Settings.mutateNewIndiv = False

                        return
                    else:
                        button.clicked = False
                        messedUp = True
                except ValueError:
                    button.clicked = False
                    messedUp = True

        screen.blit(background, (0,0))
        screen.blit(floor, (-48, floorY))
        for i in range(len(texts)):
            put_text(texts[i], gameScreenwidth / 2, 13 + i * 50)
        for box in boxes:
            box.draw(screen)
        button.draw(screen)
        if messedUp:
            put_text(warningText, gameScreenwidth, screenheight - 15)
        pygame.display.update()
        clock.tick(frames)
    return

#screen that asks for a path, where a neural network has been saved
def PathScreen():
    global screenUpdate
    screenUpdate = True
    box = InputBox((gameScreenwidth / 2), screenheight / 2 - 50, 140, 26)
    button = Button((gameScreenwidth / 2), screenheight / 2, 140, 26, ["Confirm"])
    path = "nopath"
    text1 = "Write the name of a save."
    text2 = "Saves are located in '/saves'."
    warningText = "Please give an existing file."
    messedUp = False
    while not os.path.isfile(path):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            button.handle_event(event)
            box.handle_event(event)
            if button.clicked:
                path = "saves/" + box.text + ".json"
                if not os.path.isfile(path):   
                    button.clicked = False
                    messedUp = True
        screen.blit(background, (0,0))
        screen.blit(floor, (0, floorY))
        put_text(text1, gameScreenwidth / 2, 30)
        put_text(text2, gameScreenwidth / 2, 60)
        if messedUp:
            put_text(warningText, gameScreenwidth / 2, screenheight - 30)
        button.draw(screen)
        box.draw(screen)
        pygame.display.update()
        clock.tick(frames)
    return path

def main():
    global screenUpdate
    global pause
    global frames
    if len(sys.argv) == 2:
        gameMode = "ai"
        path = "saves/" + sys.argv[1] + ".json"
        if os.path.isfile(path):
            screen = pygame.display.set_mode((gameScreenwidth,screenheight))
            individual = Individual(Load(path))
            score = PlayGame(individual).score
            screenUpdate = True
            pause = False
            frames = 30
            gameMode = EndingScreen(score, gameMode)
    else:
        gameMode = OpeningScreen()
        score = 0
    while gameMode == "learn" or gameMode == "play" or gameMode == "ai":
        if gameMode == "learn":
            screen = pygame.display.set_mode((gameScreenwidth + statScreenwidth,screenheight))
            SettingScreen()
            score = LearnGame()
        if gameMode == "play":
            screen = pygame.display.set_mode((gameScreenwidth,screenheight))
            score = PlayGame()
        if gameMode == "ai":
            screen = pygame.display.set_mode((gameScreenwidth,screenheight))
            path = PathScreen()
            individual = Individual(Load(path))
            score = PlayGame(individual).score

        screen = pygame.display.set_mode((gameScreenwidth,screenheight))
        screenUpdate = True
        pause = False
        frames = 30
        gameMode = EndingScreen(score, gameMode)

    if gameMode == "":
        LearnGame()

if __name__ == '__main__':
    main()
