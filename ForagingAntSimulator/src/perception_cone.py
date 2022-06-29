import matplotlib.pyplot as plt
import numpy as np
import argparse
import matplotlib.colors as colors

from ECAgent.Environments import PositionComponent, discreteGridPosToID
from AntSim import ForagingAntSimulator, DirectionComponent


def get_neighbouring_cells(model, x_pos: int, y_pos: int, x_dir: int, y_dir: int, border_id: str):
    upper_bound = model.environment.width

    if x_dir == 0 and y_dir == 0:
        candidate_cells = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    elif x_dir == -1 and y_dir == 0:
        candidate_cells = [(-1, 0), (-1, 1), (-1, -1)]
    elif x_dir == -1 and y_dir == 1:
        candidate_cells = [(-1, 0), (-1, 1), (0, 1)]
    elif x_dir == 0 and y_dir == 1:
        candidate_cells = [(-1, 1), (0, 1), (1, 1)]
    elif x_dir == 1 and y_dir == 1:
        candidate_cells = [(0, 1), (1, 1), (1, 0)]
    elif x_dir == 1 and y_dir == 0:
        candidate_cells = [(1, 1), (1, 0), (1, -1)]
    elif x_dir == 1 and y_dir == -1:
        candidate_cells = [(1, 0), (1, -1), (0, -1)]
    elif x_dir == 0 and y_dir == -1:
        candidate_cells = [(1, -1), (0, -1), (-1, -1)]
    else:
        candidate_cells = [(-1, 0), (0, -1), (-1, -1)]

    return [(x_pos + i[0], y_pos + i[1]) for i in candidate_cells
            if 0 <= x_pos + i[0] < upper_bound and 0 <= y_pos + i[1] < upper_bound
            and model.environment.cells[border_id][
                discreteGridPosToID(x_pos + i[0], y_pos + i[1], upper_bound)] > 0]

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
    ax.set_title('Perception Cone of Ants in Foraging Ant Simulator')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    custom_cmap = colors.LinearSegmentedColormap.from_list('', ['white', 'red', 'orange'])

    image = np.zeros((50,50))

    for agent in model.environment.getAgents():
        x = agent[PositionComponent].x
        y = agent[PositionComponent].y
        image[y, x] = 1

        for cell in get_neighbouring_cells(model, agent[PositionComponent].x, agent[PositionComponent].y,
                                           agent[DirectionComponent].x, agent[DirectionComponent].y, 'border1'):
            image[cell[1], cell[0]] = 2

    ax.imshow(image, cmap=custom_cmap, interpolation='nearest', vmin = 0, vmax = 2)
    ax.set_aspect('auto')
    fig.savefig('ant_perception.png')


if __name__ == '__main__':
    main()