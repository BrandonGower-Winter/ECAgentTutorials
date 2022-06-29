import matplotlib.pyplot as plt
import numpy as np
import argparse
import matplotlib.colors as colors

from ECAgent.Environments import PositionComponent, discreteGridPosToID
from AntSim import ForagingAntSimulator, DirectionComponent

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
    for i in range(iterations):
        model.systemManager.executeSystems()

        if (i+1) % parser.frequency == 0:
            fig, ax = plt.subplots(dpi=200)
            ax.set_title('Pheromone Intensity of Ants at timestep {} in a Dynamic Environment'.format(i+1))
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

            custom_cmap = colors.LinearSegmentedColormap.from_list('', ['white', 'black'])

            image = np.copy(model.environment.cells['f_pheromones']).reshape(50, 50) #+ np.copy(model.environment.cells['h_pheromones']).reshape(50, 50)

            ax.imshow(image, cmap=custom_cmap, interpolation='nearest', vmin = 0.0)
            ax.set_aspect('auto')
            fig.savefig('pheromone_{}.png'.format(i))
            plt.close(fig)


if __name__ == '__main__':
    main()