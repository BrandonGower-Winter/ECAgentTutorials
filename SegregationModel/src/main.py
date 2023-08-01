import argparse

from SegregationModel import SegregationModel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--size', help='Size of the environment.', default=50, type=int)
    parser.add_argument('--red', help='Number of blue houses.', default=1000, type=int)
    parser.add_argument('--blue', help='Number of red houses.', default=1000, type=int)
    parser.add_argument('--preference', help='How similar an agents neighbours need to be.', default=0.0, type=float)
    parser.add_argument('--iterations', help='Length of Simulation.', default=100, type=int)
    parser.add_argument('--seed', help='Seed of random number generator.', default=345968, type=int)
    parser.add_argument('--images', help='Write environment to images?', action='store_true')

    parser = parser.parse_args()

    model = SegregationModel(
        parser.size,
        parser.blue,
        parser.red,
        parser.preference,
        parser.seed,
        parser.images
    )

    iterations = parser.iterations
    for i in range(iterations):
        model.systemManager.executeSystems()
        print('Iteration: {}...'.format(i))

    print('...Done!')


if __name__ == '__main__':
    main()