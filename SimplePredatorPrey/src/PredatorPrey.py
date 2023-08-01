import math
import numpy

import ECAgent.Core as Core
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from ECAgent.Environments import GridWorld, PositionComponent, discreteGridPosToID
from ECAgent.Collectors import Collector


class EnergyComponent(Core.Component):
    def __init__(self, agent: Core.Agent, model: Core.Model, energy: float):
        super().__init__(agent, model)
        self.energy = energy


class Wolf(Core.Agent):

    gain = 1.0
    reproduce_rate = 0.01
    wolf_counter = 0

    def __init__(self, model: Core.Model, energy: float = None):
        super().__init__('w{}'.format(Wolf.wolf_counter), model)

        self.addComponent(
            EnergyComponent(
                self, model, energy if energy is not None else model.random.random() * 2 * Wolf.gain
        ))

        Wolf.wolf_counter += 1


class Sheep(Core.Agent):

    gain = 1.0
    reproduce_rate = 0.01
    sheep_counter = 0

    def __init__(self, model: Core.Model, energy: float = None):
        super().__init__('s{}'.format(Sheep.sheep_counter), model)

        self.addComponent(
            EnergyComponent(
                self, model, energy if energy is not None else model.random.random() * 2 * Sheep.gain
        ))

        Sheep.sheep_counter += 1


class MovementSystem(Core.System):

    def __init__(self, id: str, model: Core.Model):
        super().__init__(id, model)

    def execute(self):
        upper_bound = self.model.environment.width -1
        for agent in self.model.environment.getAgents():
            # Move within Moore Neighbourhood
            newX = max(0, min(upper_bound, agent[PositionComponent].x + int(round(2* self.model.random.random() - 1))))
            newY = max(0, min(upper_bound, agent[PositionComponent].y + int(round(2* self.model.random.random() - 1))))
            # Spend Energy
            agent[EnergyComponent].energy -= 1

            agent[PositionComponent].x = newX
            agent[PositionComponent].y = newY


class ResourceConsumptionSystem(Core.System):

    def __init__(self, id: str, model: Core.Model, regrow_time: int):
        super().__init__(id, model)

        self.regrow_time = regrow_time

        def resource_generator(pos, cells):
            return 1 if model.random.random() < 0.5 else 0

        # Generate the initial resources
        model.environment.addCellComponent('resources', resource_generator)

        def countdown_generator(pos, cells):
            return int(model.random.random() * regrow_time)

        # Generate the initial resources
        model.environment.addCellComponent('countdown', countdown_generator)

    def execute(self):

        # Get resources data
        resource_cells = self.model.environment.cells['resources'].to_numpy()
        countdown_cells = self.model.environment.cells['countdown'].to_numpy()

        eaten_sheep = []

        targets_at_pos = {}

        # Process Sheep and Wolves first
        for agent in self.model.environment.getAgents():

            posID = discreteGridPosToID(agent[PositionComponent].x, agent[PositionComponent].y,
                                        self.model.environment.width)

            # Is wolf or is sheep
            if agent.id.startswith('w'):
                # Get all agents at position

                if posID not in targets_at_pos:
                    targets_at_pos[posID] = self.model.environment.getAgentsAt(agent[PositionComponent].x, agent[PositionComponent].y)

                for target in targets_at_pos[posID]:
                    if target.id.startswith('s') and target.id not in eaten_sheep: # If sheep
                        eaten_sheep.append(target.id) # Mark Sheep for death
                        agent[EnergyComponent].energy += Wolf.gain
                        break

            elif agent.id not in eaten_sheep:
                # Check is grass is Alive
                if resource_cells[posID] > 0:
                    # Consume and Gain Energy
                    agent[EnergyComponent].energy += Sheep.gain
                    resource_cells[posID] = 0

        # Remove eaten sheep
        for sheep in eaten_sheep:
            self.model.environment.removeAgent(sheep)

        # Regrow Grass
        countdown_cells[resource_cells < 1] -= 1
        mask = countdown_cells < 1
        resource_cells[mask] = 1

        countdown_cells = numpy.where(mask, numpy.asarray([
            int(self.model.random.random() * self.regrow_time) for i in range(len(countdown_cells))
        ]), countdown_cells)

        self.model.environment.cells.update({'resources': resource_cells, 'countdown': countdown_cells})


class BirthSystem(Core.System):
    def __init__(self, id: str, model: Core.Model):
        super().__init__(id, model)

    def execute(self):

        for agent in self.model.environment.getAgents():
            if agent.id.startswith('w') and self.model.random.random() < Wolf.reproduce_rate:

                agent[EnergyComponent].energy /= 2.0

                # Birth Wolf
                self.model.environment.addAgent(
                    Wolf(self.model, energy=agent[EnergyComponent].energy),
                    xPos = agent[PositionComponent].x,
                    yPos = agent[PositionComponent].y
                )

            elif self.model.random.random() < Sheep.reproduce_rate:

                agent[EnergyComponent].energy /= 2.0

                # Birth Sheep
                self.model.environment.addAgent(
                    Sheep(self.model, energy=agent[EnergyComponent].energy),
                    xPos=agent[PositionComponent].x,
                    yPos=agent[PositionComponent].y
                )


class DeathSystem(Core.System):

    def __init__(self, id: str, model: Core.Model):
        super().__init__(id, model)

    def execute(self):
        toRem = []

        for agent in self.model.environment.getAgents():
            if agent[EnergyComponent].energy <= 0:
                toRem.append(agent.id)

        for a in toRem:
            self.model.environment.removeAgent(a)


class DataCollector(Collector):

    def __init__(self, id: str, model, image_write: bool):
        super().__init__(id, model)

        self.records = {'sheep': [], 'wolves': []}
        self.image_write = image_write
        self.custom_cmap = colors.LinearSegmentedColormap.from_list('',
                                                                   ['lightyellow', 'green','black', 'red'])

    def collect(self):

        self.records['sheep'].append(len([1 for a in self.model.environment.getAgents() if a.id.startswith('s')]))
        self.records['wolves'].append(len([1 for a in self.model.environment.getAgents() if a.id.startswith('w')]))

        if self.image_write:
            size = self.model.environment.width
            iteration = self.model.systemManager.timestep
            image = numpy.copy(self.model.environment.cells['resources'].to_numpy()).reshape(size,size)
            for agent in self.model.environment.getAgents():
                x = agent[PositionComponent].x
                y = agent[PositionComponent].y
                if image[y, x] < 3 and agent.id.startswith('w'):
                    image[y, x] = 3
                else:
                    image[y, x] = 2

            fig, ax = plt.subplots(1, 2,)# width_ratios=[1, 2])
            ax[0].set_title('Environment at Iteration {}'.format(iteration))
            ax[0].set_xlabel('x')
            ax[0].set_ylabel('y')
            ax[0].imshow(image, cmap=self.custom_cmap, interpolation='nearest', vmin = 0, vmax = 3)

            ax[1].set_title('Sheep and Wolf Populations in \nSimple Predator Prey Model')
            ax[1].set_xlabel('Iterations')

            iterations = numpy.arange(iteration + 1)
            for prop in self.records:
                ax[1].plot(iterations, self.records[prop], label=prop)

            ax[1].legend(loc='lower right')
            fig.set_figwidth(15)
            fig.savefig('env{}'.format(iteration), dpi=200)
            plt.close(fig)


class PredatorPreyModel(Core.Model):

    def __init__(self, size: int, init_sheep: int, init_wolf: int, regrow_rate: int,
                 sheep_gain: float, wolf_gain: float, sheep_reproduce: float, wolf_reproduce: float,
                 seed: int, image_write: bool):
        super().__init__(seed=seed)
        self.environment = GridWorld(size, size, self)

        # Add Systems
        self.systemManager.addSystem(MovementSystem('move', self))
        self.systemManager.addSystem(ResourceConsumptionSystem('food', self, regrow_rate))
        self.systemManager.addSystem(BirthSystem('birth', self))
        self.systemManager.addSystem(DeathSystem('death', self))
        self.systemManager.addSystem(DataCollector('collector', self, image_write))

        # Parameterize Agents
        Wolf.gain = wolf_gain
        Sheep.gain = sheep_gain

        Wolf.reproduce_rate = wolf_reproduce
        Sheep.reproduce_rate = sheep_reproduce

        # Create Agents at random locations

        for _ in range(init_sheep):
            self.environment.addAgent(
                Sheep(self),
                xPos = self.random.randint(0, size - 1),
                yPos = self.random.randint(0, size - 1)
            )

        for _ in range(init_wolf):
            self.environment.addAgent(
                Wolf(self),
                xPos = self.random.randint(0, size - 1),
                yPos = self.random.randint(0, size - 1)
            )
