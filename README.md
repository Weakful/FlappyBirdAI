# FlappyBirdAI
Flappy Bird game and an AI for it that learns how to play.

Writen using python 3.9.0 (should work with any 3.x.x)

Modules to install: Matplotlib, Numpy, Pygame

The best AI I found scored 4225, but there are still some problems with the program (for example.: because of the random generation of the holes between the tubes, we can have some worse performing individuals outperforming better ones every once in a while, and take over the elite spot they don't deserve and mess up the process).

Teaching the AI goes until the bird reaches 10000 score

Settings for the Learning process:
Max generations: If it didn't reach 10000 points the learning process ends here.
Generation Size: The size of the population each generation.
Elites to breed: The number of best performing individuals we use to make the next generation.
Elites to keep: The number of best performing individuals we keep as is in the next generation.
Random individuals per gen.: Number of random made individuals we add to the population.
Mutation type: New value means that the gene to mutate will be completely new, while the Multiply value only multiplies the previous value by a random number between -2 and 2.
Crossover type: With Random we flip a coin on every gene and with One point flip we randomize a point between the genes and the newborn recieves all genes before that point from one parent and all genes after that point from the other parent.
Selection types: With Roulette each individual have a chance equial to their performance to be selected, with Tournament we select 5 individuals randomly and choose the best from them, with Fittest we choose the best individual and with Random elite we choose a random individual from the best performing ones.
Mutation rate: The chance at which we mutate each gene.
Mutate elites: Whether we want to mutate elites or take them to the next generation without touching them.
Mutate newborn: Whether we want to mutate newborns.
Fitness: We can choose to take the score or the frames stayed alive as fitness.
Use Crossover/Mutation: If turned off all individuals that are not elites will be randomly generated individuals.

When making an AI play you only have to give the file name and not type from the "saves" directory.
