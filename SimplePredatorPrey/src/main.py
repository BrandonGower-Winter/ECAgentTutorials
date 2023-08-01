import matplotlib.pyplot as plt
import numpy as np
import argparse

from PredatorPrey import PredatorPreyModel

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--size', help='Size of the environment.', default=50, type=int)
    parser.add_argument('--sheep', help='Number of initial Sheep.', default=100, type=int)
    parser.add_argument('--wolf', help='Number of initial Wolves.', default=50, type=int)
    parser.add_argument('--grow', help='Regrow Rate of Grass Entities.', default=30, type=int)
    parser.add_argument('--sgain', help='Sheep Gain.', default=4, type=int)
    parser.add_argument('--wgain', help='Wolf Gain.', default=25, type=int)
    parser.add_argument('--srepro', help='Reproduction Rate of Sheep.', default=0.04, type=float)
    parser.add_argument('--wrepro', help='Reproduction Rate of Wolves.', default=0.06, type=float)
    parser.add_argument('--iterations', help='Length of Simulation.', default=1000, type=int)
    parser.add_argument('--seed', help='Seed of random number generator.', default=345968, type=int)
    parser.add_argument('--images', help='Write environment to images?', action='store_true')

    parser = parser.parse_args()

    model = PredatorPreyModel(
        parser.size,
        parser.sheep,
        parser.wolf,
        parser.grow,
        parser.sgain,
        parser.wgain,
        parser.srepro,
        parser.wrepro,
        parser.seed,
        parser.images)

    iterations = parser.iterations
    records = model.systemManager.systems['collector'].records
    for i in range(iterations):
        model.systemManager.executeSystems()
        print('Iteration: {}: Sheep: {} Wolves:{}'.format(i, records['sheep'][-1], records['wolves'][-1]))

    fig, ax = plt.subplots()
    ax.set_title('Sheep and Wolf Populations in \nSimple Predator Prey Model')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Population')

    iterations = np.arange(iterations)

    for prop in records:
        ax.plot(iterations, records[prop], label=prop)

    ax.legend(loc='lower right')

    ax.set_aspect('auto')
    fig.savefig('population.png')


if __name__ == '__main__':
    main()