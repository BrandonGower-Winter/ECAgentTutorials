import math
import numpy

import ECAgent.Core as Core
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from ECAgent.Environments import GridWorld, PositionComponent, discreteGridPosToID
from ECAgent.Collectors import Collector
from PIL import Image
from scipy.ndimage import gaussian_filter


class DirectionComponent(Core.Component):
    def __init__(self, agent: Core.Agent, model: Core.Model):
        super().__init__(agent, model)
        self.x = self.model.random.randint(-1, 1)
        self.y = self.model.random.randint(-1, 1)


class ModeComponent(Core.Component):
    def __init__(self, agent: Core.Agent, model: Core.Model):
        super().__init__(agent, model)
        self.home = False


class CollectedComponent(Core.Component):
    def __init__(self, agent: Core.Agent, model: Core.Model):
        super().__init__(agent, model)
        self.collected_resources = 0


class Ant(Core.Agent):

    pheromone_deposit_rate = 0.25
    ant_counter = 0

    def __init__(self, model: Core.Model, energy: float = None):
        super().__init__('a{}'.format(Ant.ant_counter), model)

        self.addComponent(DirectionComponent(self, model))
        self.addComponent(ModeComponent(self, model))

        Ant.ant_counter += 1


class MovementSystem(Core.System):

    switch_frequency = 50

    def __init__(self, id: str, model: Core.Model, switch_frequency : int):
        super().__init__(id, model)

        MovementSystem.switch_frequency = switch_frequency

        def pheromone_generator(pos, cells):
            return 0.0

        model.environment.addCellComponent('f_pheromones', pheromone_generator)
        model.environment.addCellComponent('h_pheromones', pheromone_generator)


    def get_neighbouring_cells(self, x_pos : int, y_pos : int, x_dir : int, y_dir : int, border_id : str):

        upper_bound = self.model.environment.width

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
                and self.model.environment.cells[border_id][
                    discreteGridPosToID(x_pos + i[0], y_pos + i[1], upper_bound)] > 0]

    def execute(self):

        # Get resources data
        fcells = self.model.environment.cells['f_pheromones'].to_numpy()
        hcells = self.model.environment.cells['h_pheromones'].to_numpy()

        border_id = 'border1' if (self.model.systemManager.timestep // MovementSystem.switch_frequency) % 2 == 0 else 'border2'

        for agent in self.model.environment.getAgents():

            candidate_cells = self.get_neighbouring_cells(agent[PositionComponent].x, agent[PositionComponent].y,
                                                          agent[DirectionComponent].x, agent[DirectionComponent].y,
                                                          border_id)



            if len(candidate_cells) == 0:
                agent[DirectionComponent].x = 0
                agent[DirectionComponent].y = 0
                continue

            # First check for any resources

            cells_with_resources = [c for c in candidate_cells if self.model.environment.cells['resources'][
                discreteGridPosToID(c[0], c[1], self.model.environment.width)] > 0.0
            ]

            if len(cells_with_resources) > 0 and not agent[ModeComponent].home:
                newPos = self.model.random.choice(cells_with_resources)
            elif self.model.random.random() < 0.05:
                newPos = self.model.random.choice(candidate_cells)
            else:
                pheromones = []

                tcells = hcells if agent[ModeComponent].home else fcells

                for c in candidate_cells:
                    pheromones.append(tcells[discreteGridPosToID(c[0], c[1], self.model.environment.width)])

                maxP = max(pheromones)
                newPos = candidate_cells[self.model.random.choice([
                    p for p in range(len(pheromones)) if pheromones[p] == maxP
                ])]

            #Update Direction
            agent[DirectionComponent].x = newPos[0] - agent[PositionComponent].x
            agent[DirectionComponent].y = newPos[1] - agent[PositionComponent].y

            # Update Position
            agent[PositionComponent].x = newPos[0]
            agent[PositionComponent].y = newPos[1]


class PheromoneSystem(Core.System):

    def __init__(self, id : str, model : Core.Model, decay_rate : float, reset_freq, diffuse : bool):
        super().__init__(id, model)

        self.decay_rate = decay_rate
        self.reset_freq = reset_freq
        self.diffuse = diffuse
        model.environment.addComponent(CollectedComponent(self, model))


    def execute(self):

        if self.model.systemManager.timestep % self.reset_freq == 0:
            self.model.environment.cells.update(
                { 'resources' :numpy.copy(self.model.environment.cells['resource_template'].to_numpy())}
            )

        # Get resources data
        fcells = self.model.environment.cells['f_pheromones'].to_numpy() * self.decay_rate
        hcells = self.model.environment.cells['h_pheromones'].to_numpy() * self.decay_rate

        if self.diffuse:
            for i, cells in enumerate([fcells, hcells]):
                reshaped_env = cells.reshape(self.model.environment.width, self.model.environment.width)
                reshaped_env = gaussian_filter(reshaped_env, sigma=1)
                if i ==0:
                    fcells = reshaped_env.flatten()
                else:
                    hcells = reshaped_env.flatten()

        fcells[fcells < 0.01] = 0.0
        hcells[hcells < 0.01] = 0.0

        resource_cells = self.model.environment.cells['resources'].to_numpy()

        for agent in self.model.environment.getAgents():

            posID = discreteGridPosToID(agent[PositionComponent].x, agent[PositionComponent].y,
                                        self.model.environment.width)

            if agent[ModeComponent].home:
                if 22 < agent[PositionComponent].x < 28 and 22 < agent[PositionComponent].y < 28:
                    agent[ModeComponent].home = False
                    self.model.environment[CollectedComponent].collected_resources += 1
                    agent[DirectionComponent].x = 0
                    agent[DirectionComponent].y = 0

                fcells[posID] += Ant.pheromone_deposit_rate

            elif resource_cells[posID] > 0.0:
                resource_cells[posID] -= 1
                agent[ModeComponent].home = True
                hcells[posID] += Ant.pheromone_deposit_rate
                agent[DirectionComponent].x = 0
                agent[DirectionComponent].y = 0
            else:
                hcells[posID] += Ant.pheromone_deposit_rate

        self.model.environment.cells.update({'f_pheromones': fcells, 'h_pheromones' : hcells, 'resources' : resource_cells})


class DataCollector(Collector):

    def __init__(self, id: str, model, image_write: bool):
        super().__init__(id, model)

        self.image_write = image_write
        self.custom_cmap = colors.LinearSegmentedColormap.from_list('',
                                                                   ['black', 'white', 'green', 'red', 'blue'])

    def collect(self):

        if self.image_write:
            size = self.model.environment.width
            iteration = self.model.systemManager.timestep
            border_id = 'border1' if (self.model.systemManager.timestep // MovementSystem.switch_frequency) % 2 == 0 else 'border2'
            image = numpy.copy(self.model.environment.cells[border_id].to_numpy())
            image[self.model.environment.cells['resources'].to_numpy() > 0.0] = 2
            image = image.reshape(size,size)

            for agent in self.model.environment.getAgents():
                x = agent[PositionComponent].x
                y = agent[PositionComponent].y
                image[y, x] = 4 if agent[ModeComponent].home else 3

            fig, ax = plt.subplots()
            ax.set_title('Environment at Iteration {}'.format(iteration))
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.imshow(image, cmap=self.custom_cmap, interpolation='nearest', vmin = 0, vmax = 4)

            fig.savefig('env{}'.format(iteration))
            plt.close(fig)

        self.records.append(self.model.environment[CollectedComponent].collected_resources)


class ForagingAntSimulator(Core.Model):

    def __init__(self, file1 : str, file2 : str, file3 : str, size: int, init_ants: int, deposit_rate: float,
                 decay_rate: float, switch_frequency : int, reset_freq: int, diffuse : bool, mult : int,
                 image_write: bool, seed: int):
        super().__init__(seed=seed)
        self.environment = GridWorld(size, size, self)

        # Add environment layers
        self.environment.cells['border1'] = numpy.asarray(Image.open(file1).convert('L')).flatten() / 255.0
        self.environment.cells['border2'] = numpy.asarray(Image.open(file2).convert('L')).flatten() / 255.0
        self.environment.cells['resources'] = (1.0 - numpy.asarray(Image.open(file3).convert('L')).flatten() / 255.0) * mult
        self.environment.cells['resource_template'] = numpy.copy(self.environment.cells['resources'].to_numpy())
        # Add Systems
        self.systemManager.addSystem(MovementSystem('move', self, switch_frequency))
        self.systemManager.addSystem(PheromoneSystem('phero', self, decay_rate, reset_freq, diffuse))
        self.systemManager.addSystem(DataCollector('collector', self, image_write))

        # Parameterize Agents
        Ant.pheromone_deposit_rate = deposit_rate

        # Create Agents at random locations

        for _ in range(init_ants):
            self.environment.addAgent(
                Ant(self),
                xPos = 24,
                yPos = 24
            )
