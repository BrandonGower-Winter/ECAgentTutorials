import matplotlib.pyplot as plt
import numpy as np
import argparse
import random

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
    parser.add_argument('--iterations', help='Length of Simulation.', default=1000, type=int)
    parser.add_argument('--diffuse', help='Diffuse Pheromones to adjacent cells?', action='store_true')
    parser.add_argument('--mult', help='Number of resources to deposit on a resource cell', default=1.0, type=float)

    parser = parser.parse_args()

    seeds = [73142, 61272, 47223, 96646, 43169, 27701, 67950, 58312, 22496, 43277,
             87574, 85422, 39446, 91878, 90483, 74729, 30464, 94072, 41488, 80227,
             73890, 48275, 23865, 96789, 93226, 5819, 60490, 4067, 98684, 22235,
             53161, 55927, 53825, 44493, 72365, 6057, 1518, 81830, 59560, 92746,
             31778, 52347, 5120, 44947, 70959, 93148, 94759, 40965, 75834, 30914]

    print("Seeds:")
    print(seeds)

    graphs = np.zeros((3, parser.iterations))
    delta = np.zeros((3, parser.iterations))

    for seed in seeds:

        decay_model = ForagingAntSimulator(
            parser.file1,
            parser.file2,
            parser.file3,
            parser.size,
            parser.ants,
            parser.deposit,
            0.9,
            parser.frequency,
            parser.reset,
            parser.diffuse,
            parser.mult,
            False,
            seed)


        iterations = parser.iterations
        for _ in range(iterations):
            decay_model.systemManager.executeSystems()

        graphs[0] += np.array(decay_model.systemManager.systems['collector'].records)

    for seed in seeds:

        nodecay_model = ForagingAntSimulator(
            parser.file1,
            parser.file2,
            parser.file3,
            parser.size,
            parser.ants,
            parser.deposit,
            1.0,
            parser.frequency,
            parser.reset,
            parser.diffuse,
            parser.mult,
            False,
            seed)


        iterations = parser.iterations
        for _ in range(iterations):
            nodecay_model.systemManager.executeSystems()

        graphs[1] += np.array(nodecay_model.systemManager.systems['collector'].records)

    for seed in seeds:
        nophero_model = ForagingAntSimulator(
            parser.file1,
            parser.file2,
            parser.file3,
            parser.size,
            parser.ants,
            0.0,
            0.0,
            parser.frequency,
            parser.reset,
            parser.diffuse,
            parser.mult,
            False,
            seed)


        iterations = parser.iterations
        for _ in range(iterations):
            nophero_model.systemManager.executeSystems()

        graphs[2] += np.array(nophero_model.systemManager.systems['collector'].records)

    graphs /= 50

    delta = np.copy(graphs)
    delta[0, 1:] -= graphs[0, 0:-1]
    delta[1, 1:] -= graphs[1, 0:-1]
    delta[2, 1:] -= graphs[2, 0:-1]

    fig, ax = plt.subplots(dpi=200)
    ax.set_title('Amount of Resources Collected by Different\n Ant Types in a Dynamic Environment')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Collected Resources')

    iterations = np.arange(iterations)

    for i, prop in enumerate(['with decay', 'no decay', 'random search']):
        ax.plot(iterations, graphs[i], label=prop)

    ax.legend(loc='lower right')

    ax.set_aspect('auto')
    fig.savefig('collected.png')
    plt.close(fig)

    fig, ax = plt.subplots(dpi=200)
    ax.set_title('Rate of Resource Collection Resources by Different \n Ant Types in the Dynamic Environment Scenario')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Collected Resources')

    for i, prop in enumerate(['with decay', 'no decay', 'random search']):
        ax.plot(iterations, delta[i], label=prop)

    ax.legend(loc='upper right')

    ax.set_aspect('auto')
    fig.savefig('collected_rate.png')
    plt.close(fig)


if __name__ == '__main__':
    main()