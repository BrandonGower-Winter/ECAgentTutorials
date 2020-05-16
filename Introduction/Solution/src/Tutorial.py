from random import randrange

from ECAgent.Core import *

# This tutorial is based on the MESA introductory tutorial

# We now create our own custom model called MoneyModel by inheriting from the base Model class.
# A Model is the backbone of the entire framework
class MoneyModel(Model):

    def __init__(self, num_agents):
        # The Model base requires that an environment be supplied to it upon initialization
        # Because our model does not need a complex environment with positional information, we can just
        # use the default Environment class instead.
        super().__init__(Environment())

        # After we've created our System, we now have to register it with SystemManager.
        self.systemManager.addSystem(MoneySystem(self))
        # Now, whenever we execute a cycle of our model, the MoneySystem will automatically run.

        # Now we can add our agents
        # It is important to remember to add your Systems first and then your agents.
        for i in range(0,num_agents):
            # We are just giving the agents the id 'a' + the i value in the loop
            # This ensure that each agent will have a unique ID
            self.environment.addAgent(MoneyAgent('a' + str(i), self))

    # This method will be used by our main method to run the simulation.
    def run(self):
        # Our basic simulation will run for 10 iterations but you can create more complicated stopping conditions if
        # you want to.
        while self.systemManager.timestep < 10:
            # Execute systems calls the execute functions of all of the registered systems (when appropriate) and
            # increments the timestep counter by 1
            self.systemManager.executeSystems()

# This is our custom system class. It inherits from the base System class.
class MoneySystem(System):

    def __init__(self, model: Model):
        # Here we call the base class constructor and give our custom system a unique ID called 'MONEY'
        # The ID of the system is very important because it is responsible for ensuring that the system interacts with
        # the appropriate components.
        # The system base class has a number of optional parameters that are out of scope for this tutorial.
        super().__init__("MONEY", model)

    # In order for our system to do anything at runtime, we must override the execute function like so.
    def execute(self, components: [Component]):
        # The execute function is called by the SystemManager whenever our System must process some logic.
        # In the case of our MoneySystem, it will execute once every cycle.

        # As you'll notice, the execute function takes a list of components as input
        # These components are the components created specifically for the MoneySystem ie: MoneyComponents

        # Here we iterate over the components
        for component in components:
            # Make sure the agent has money to give away
            if component.wealth == 0:
                pass
            # Give away money to a random agent
            else:
                # We can use the environment object get a random agent
                # Be careful when using this method, if there are agents that have different components
                # then you must include a component filter like so: getRandomAgent([Component1,Component2,..])
                other_agent = self.model.environment.getRandomAgent()
                # Now we grab the MoneyComponent from the agent using the getComponent() method
                other_agent.getComponent(MoneyComponent).wealth += 1
                component.wealth -= 1

# This is our custom component class. It inherits from the base Component class.
# Components are added to agents and are used by the SystemManager to determine which Agents
# are affected by a specific system.
class MoneyComponent(Component):

    def __init__(self, agentID: str, model: Model):
        # Here we call the base class constructor and supply it with the agent's, that this component is attached to, ID
        # the system ID which for our custom system is 'MONEY' and a reference to the model
        super().__init__(agentID,"MONEY",model)

        # Components of intended to be POD (Plain old data) so they will have little functionality.
        # Here we create and store the only property that this component will hold
        self.wealth = 1


# This is our custom agent class. It inherits from the base Agent class.
class MoneyAgent(Agent):

    def __init__(self, id: str, model: Model):
        # Here we call the base class constructor. The agent class requires that the agent be given a unqiue ID
        super().__init__(id, model)

        # This is where the beauty of ECS comes into play.
        # Now we add a money component to agent and the agent will automatically be registered with the appropriate
        # system and will be affected by said system whenever it executes.
        self.addComponent(MoneyComponent(self.id,self.model))


if __name__ == '__main__':
    # Now we create our Model
    model = MoneyModel(10) # We will just have 10 agents
    model.run() # This will run our model for 10 iterations

    # Now we can print out the wealth distribution of our model here is a simple way to do that using
    # list comprehension. We use the SystemManager.getComponents() to get all of the components registered to
    # a specific system
    print ([x.wealth for x in model.systemManager.getComponents("MONEY")])