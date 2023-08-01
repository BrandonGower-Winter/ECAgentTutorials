import math
import numpy

import ECAgent.Core as Core
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from ECAgent.Environments import GridWorld, PositionComponent, discreteGridPosToID
from ECAgent.Collectors import Collector


class SegregationComponent(Core.Component):
    def __init__(self, agent: Core.Agent, model: Core.Model, location: (int, int), is_blue: bool):
        super().__init__(agent, model)
        self.location = location
        self.blue = is_blue


class Household(Core.Agent):

    counter = 0

    def __init__(self, model: Core.Model, location: (int, int), is_blue: bool):
        super().__init__(Household.counter, model)
        self.addComponent(
            SegregationComponent(
                self, model, location, is_blue
        ))

        Household.counter += 1


class MovementSystem(Core.System):

    @staticmethod
    def get_similarity(id, width, x, y, map) -> float:
        count = 0
        matches = 0

        xless = x - 1 > -1
        xmax = x + 1 < width
        yless = y - 1 > -1
        ymax = y + 1 < width

        if xless:
            matches += 1 if map[x-1][y] == id else 0
            count += 1 if map[x-1][y] != 0 else 0

        if yless:
            matches += 1 if map[x][y-1] == id else 0
            count += 1 if map[x][y-1] != 0 else 0

        if xmax:
            matches += 1 if map[x+1][y] == id else 0
            count += 1 if map[x+1][y] != 0 else 0

        if ymax:
            matches += 1 if map[x][y+1] == id else 0
            count += 1 if map[x][y+1] != 0 else 0

        if ymax and xless:
            matches += 1 if map[x - 1][y + 1] == id else 0
            count += 1 if map[x - 1][y + 1] != 0 else 0

        if ymax and xmax:
            matches += 1 if map[x + 1][y + 1] == id else 0
            count += 1 if map[x + 1][y + 1] != 0 else 0

        if yless and xmax:
            matches += 1 if map[x + 1][y - 1] == id else 0
            count += 1 if map[x + 1][y - 1] != 0 else 0

        if yless and xless:
            matches += 1 if map[x - 1][y - 1] == id else 0
            count += 1 if map[x - 1][y - 1] != 0 else 0

        return matches / count if count > 0 else 0.0

    def __init__(self, id: str, model: Core.Model, preference : float):
        super().__init__(id, model)
        self.preference = preference

    def execute(self):
        map = numpy.zeros((self.model.size, self.model.size))

        for agent in self.model.environment.getAgents():
            ax, ay = agent[SegregationComponent].location
            blue = agent[SegregationComponent].blue
            map[ax][ay] = 1 if blue else 2

        free_locations = []

        for x in range(self.model.size):
            for y in range(self.model.size):
                if map[x][y] == 0:
                    free_locations.append((x,y))

        # Move unhappy agents
        for agent in self.model.environment.getAgents():
            ax, ay = agent[SegregationComponent].location
            blue = agent[SegregationComponent].blue

            if MovementSystem.get_similarity(1 if blue else 2, self.model.size, ax, ay, map
                                             ) < self.preference:
                self.model.random.shuffle(free_locations)
                moved = None
                for x ,y in free_locations:
                    if MovementSystem.get_similarity(1 if blue else 2, self.model.size, x, y, map
                                             ) >= self.preference:
                        moved = (x, y)
                        break

                if moved is None:
                    moved = self.model.random.choice(free_locations)

                agent[SegregationComponent].location = moved
                free_locations.remove(moved)
                free_locations.append((ax, ay))


class DataCollector(Collector):

    def __init__(self, id: str, model, image_write: bool):
        super().__init__(id, model, priority=2)
        self.image_write = image_write
        self.custom_cmap = colors.LinearSegmentedColormap.from_list('',
                                                                   ['white','blue', 'red'])

    def collect(self):

        if self.image_write:
            iteration = self.model.systemManager.timestep

            map = numpy.zeros((self.model.size, self.model.size))
            for agent in self.model.environment.getAgents():
                ax, ay = agent[SegregationComponent].location
                blue = agent[SegregationComponent].blue
                map[ax][ay] = 1 if blue else 2

            fig, ax = plt.subplots()# width_ratios=[1, 2])
            ax.set_title('Environment at Iteration {}'.format(iteration))
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.imshow(map, cmap=self.custom_cmap, interpolation='nearest', vmin = 0, vmax = 2)
            fig.savefig('env{}'.format(iteration), dpi=200)
            plt.close(fig)


class SegregationModel(Core.Model):

    def __init__(self, size: int, init_blue: int, init_red: int, preference: float,
                 seed: int, image_write: bool):
        super().__init__(seed=seed)
        self.size = size
        # Add Systems
        self.systemManager.addSystem(MovementSystem('move', self, preference))
        self.systemManager.addSystem(DataCollector('collector', self, image_write))

        locations = []
        for x in range(size):
            for y in range(size):
                locations.append((x, y))

        self.random.shuffle(locations)
        total = 0

        # Create Agents at random locations
        for _ in range(init_blue):
            self.environment.addAgent(Household(self, locations[total], True))
            total += 1

        # Create Agents at random locations
        for _ in range(init_red):
            self.environment.addAgent(Household(self, locations[total], False))
            total += 1
