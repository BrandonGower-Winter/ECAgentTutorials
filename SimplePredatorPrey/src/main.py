import matplotlib.pyplot as plt
import numpy as np

from PredatorPrey import PredatorPreyModel

# TODO Add Argparse support
def main():
    model = PredatorPreyModel(50, 100, 50, 30, 4, 25, 0.04, 0.06)

    iterations = 5000

    for i in range(iterations):
        model.systemManager.executeSystems()

    records = model.systemManager.systems['collector'].records

    fig, ax = plt.subplots()
    ax.set_title('Population Dynamics of Simple\n Predator Prey Model')
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