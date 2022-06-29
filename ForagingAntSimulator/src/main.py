import matplotlib.pyplot as plt
import numpy as np
import argparse

from AntSim import ForagingAntSimulator

# TODO Add Argparse support
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-f1', '--file1', help='Path to first File.', default=None, type=str)
    parser.add_argument('-f2', '--file2', help='Path to second File.', default=None, type=str)
    parser.add_argument('-f3', '--file3', help='Path to third File.', default=None, type=str)
    parser.add_argument('--frequency', help='Frequency of f1 and f2 border switch.', default=50, type=int)
    parser.add_argument('--reset', help='Frequency of resource resetting.', default=100, type=int)
    parser.add_argument('-s', '--size', help='Size of the environment.', default=50, type=int)
    parser.add_argument('--ants', help='Number of ants.', default=50, type=int)
    parser.add_argument('--deposit', help='Pheromone Deposit Rate', default=0.25, type=int)
    parser.add_argument('--decay', help='Pheromone Decay Rate', default=0.6, type=float)
    parser.add_argument('--iterations', help='Length of Simulation.', default=1000, type=int)
    parser.add_argument('--seed', help='Seed of random number generator.', default=345968, type=int)
    parser.add_argument('--images', help='Write environment to images?', action='store_true')
    parser.add_argument('--diffuse', help='Diffuse Pheromones to adjacent cells?', action='store_true')
    parser.add_argument('--mult', help='Number of resources to deposit on a resource cell', default=1.0, type=float)

    parser = parser.parse_args()

    model = ForagingAntSimulator(
        parser.file1,
        parser.file2,
        parser.file3,
        parser.size,
        parser.ants,
        parser.deposit,
        parser.decay,
        parser.frequency,
        parser.reset,
        parser.diffuse,
        parser.mult,
        parser.images,
        parser.seed)

    iterations = parser.iterations
    for _ in range(iterations):
        model.systemManager.executeSystems()

    fig, ax = plt.subplots(dpi=200)
    ax.set_title('Collected resources in \nForaging Ant Simulator')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Collected Resources')

    iterations = np.arange(iterations)

    ax.plot(iterations, model.systemManager.systems['collector'].records)
    ax.set_aspect('auto')
    fig.savefig('collected.png')


if __name__ == '__main__':
    main()