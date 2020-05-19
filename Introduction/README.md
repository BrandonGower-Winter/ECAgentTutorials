# ECAgent Introductory tutorial
Welcome to the ECAgent Introductory tutorial. We will be taking a look at some of
the fundamental ideas that make-up the ECAgent framework. To get things started,
make sure that you are at least a little bit familiar with the core concepts of
the Entity-Component-System (ECS) architectural pattern. If you are not comfortable
with ECS, see the [Wikipedia](https://en.wikipedia.org/wiki/Entity_component_system) page for more information.

## Getting Started:

To start of with, you should clone this repo and using your favourite 
Python editor, open  to the ECAgentTutorials/Introduction/Tutorial directory.

Now that you're all sorted, we can talk about setting up our python virtual 
environment. If you are familiar with python and virtual environments,
 you can set this up yourself and just use:

```
$ pip install ECAgent 
```

If you are unfamiliar with virtual environments, don't worry. We have prepared
a makefile that will setup the virtual environment with ECAgent already included.
Simply open your terminal, navigate to the Tutorial directory and type the command:

```
$ make
```

You will see a bunch of text appear and, upon resolution a new folder called 'venv'
should appear. This is the virtual environment. If you are interested in learning
more about virtual environments, click the link [here](https://docs.python.org/3/tutorial/venv.html).

To activate the virtual environment, type the following command in your terminal:

```
$ source ./venv/bin/activate
```

You should now see '(venv)' appear as a prefix in your terminal. If you everwant to
 deactivate the virtual environment, just type the following command:

```
$ deactivate
```
 
Please be aware that these tutorials will only work on Linux or MacOS machines. To get these
tutorials to work on Windows, we highly suggest using a Python editor that can do package
management for you. You will only need the ECAgent package for this tutorial.

## Setting up the model:

Now that we have setup ECAgent, we can proceed to create our Agent-based Model (ABM).
We will be recreating a simple model inspired by [[Dragulescu2002]](http://arxiv.org/abs/cond-mat/0211175).

Our model will follow this simple procedure:

* Agents will start the simulation with 1 coin each.
* At each iteration, each agent will give 1 coin to another, randomly selected,
agent.
* After N iterations, our model will print out the wealth distribution of our agent
population.

Let's get started!

The first thing we want to do is open up, in our favourite Python editor,
the Tutorial.py file, located in the /src/ directory. You should see a completely
blank file.

Lets kick things off by first importing our package like so:

```python
from ECAgent.Core import *
```

This will ensure that we have all of the necessary classes needed to
make our wealth distribution model.

Now that we have that out of the way, lets talk about the five core classes
of ECAgent. They are:

* Model
* Environment
* System
* Agent
* Component

You will need to understand how all of these clases work in order to create ABMs
in ECAgent. If you are familiar with ECS, you should recognize the System and Component classes
and, if you are familiar with ABMs you are most likely familiar with the Model, Environment and Agent
classes.

Let's start with the simplest class, the Component class. In ECAgent and ECS 
in general, Components are plain-old-data (POD) types. This means that they only store information, 
in variables, and have little-to-no functionality. In our Model we would create
a wealth component like so:

```python
class MoneyComponent(Component):

    def __init__(self, agent, model):
        super().__init__(agent, model)
        self.wealth = 1
```  

As you can see, we inherit from the Component base class and definte a constructor.
The Component class takes two arguments: The agent that the compoenent belongs too
and the simulation model. We simply add those parameters to our MoneyComponent constrcutor
so that we pass along that information when we initialize our MoneyComponents.
We also add a wealth parameter and set it to 1. This follows our first rule in that all
agents will start with 1 coin.

You'll notice that the MoneyComponent class is incredibly simple. This is intentional.
In ECS components should rarely be complex. It is ok to add some functionality to calculate
composite or auxillary properties but, as a general rule, you should keep your components
as simple as possible.

Now lets move onto our next class, the Agent class. You probably noticed from
the class definitions that we seem to be missing the 'Entity' portion of 
our Entity-Component-System. In ECAgent, the Agent class is the Entity class.
It is responsible for keeping track of the components attached to itself. It may
even keep add/remove components from itself should the situation arise. For our
ABM, our Agent class should look something like this:

```python
class MoneyAgent(Agent):

    def __init__(self, id: str, model):
        super().__init__(id, model)
        self.addComponent(MoneyComponent(self,self.model))
```

Again, this isn't a very complex class but it illustrates all you need to know
about the Agent class. Once again, our base class requires that we pass it our
model. We just pass this off to our MoneyAgent constructor function because we
will supply the model when we create the agents for the first time. You will also
notice the 'id' property. This is a very important property in that it uniquely identifies
the agent in our model. If you do not supply each agent with a unique id, the final program
will throw an Exception.

Now that we have the Agent(Entity) and Component classes out of the way, lets create 
our system class. In ECS, Systems are responsible for modifying the values of components.
They can also trigger events that trigger other systems and so on and so forth. ECAgent
does not have an event system by default. ECAgent exectures System procedures by way of a
SystemManager. The SystemManager is responsible for scheduling when events
run and when they do not. It is possible to write your own SystemManager but
that is beyond the scope of this tutorial. We will just the default one.

As you'll remember from our brief model description, at every iteration of
our model an agent, if possible, must give away 1 coin to another random agent.
Knowing this, we can create our MoneySystem like so:

```python
class MoneySystem(System):

    def __init__(self, model)
        super().__init__("MONEY", model)

    def execute(self):
        components = self.model.systemManager.getComponents(MoneyComponent)
        
        for component in components:
            if component.wealth == 0:
                pass
            else:
                other_agent = self.model.environment.getRandomAgent()
                other_agent.getComponent(MoneyComponent).wealth += 1
                component.wealth -= 1
```  

This will be the most complicated part of our model. As is the norm, our System base class
requires a that we supply it with model it belongs too. Like before, we will just
pass this in when we create the system. You will also see one other value being pass in, "MONEY".
This is the system's id. Just like the Agents, systems also require unique identifiers. 
The id is used by the SystemManager and some of the other Systems in ECAgent.
If you look at the docs, you'll notice that the System base clas initiailization method has a
number of optional parameters. These parameters control how frequently and in what order your
systems should run. It is out of scope for this tutorial but just know that our MoneySystem
will run once at every iteration of our model.

Custom System classes also require that you overload the execute() function.
This function is called by the systemManager everytime our model needs to compute
at a given timestep. The execute function is where your ABM logic goes. In our case,
our MoneySystem needs to iterate through each MoneyComponent (which an agent has) 
and give 1 coin to a random agent if possible. We can get a list of all MoneyComponents
in our model using the SystemManager.getComponents() method supplying it 
with the name of our MoneyComponent class as input. We then iterate through 
each component and, if the agent has money, we give 1 coin to another random 
agent. We can use the Environment.getRandomAgent() method to get a random agent from our environment and then we use the
Agent.getComponent() method to get that agent's MoneyComponent.

For our simple model, using getRandomAgent() and getComponent() is fine because
we will only have one type of agent in our model and we each agent will have a 
MoneyComponent. If you are working with multiple types of Agents with varying
components, you should first make sure the agent has the component you are looking
for. This can be done using the Agent.hasComponent() function which returns True
if the agent has the desired component.

## Putting it all together:

Now that our custom system is done, we can start to put everything together.

Environments are a very important in ABMs. They are responsible for managing the
space the agents occupy. The environment may be dimensionless, 2D, 3D, continuous
or even discrete. ECAgent allows you to customize your environment in a similar fashion to 
how you can customize systems, agents and components. However, because this is an 
introductory tutorial, custom environments will not be covered (They are covered
in this tutorial here). This is ok for our simple model as we just need a
environment that contains some kind of reference to all of the agents. By default
and if no Environment is supplied to the Model upon initialization, the model
will create a empty Environment() object. This environment simply  holds
a list of the agents currently occupying it and is actually the base class for
the complex environments.

As a result of this functionality, you will not see an Environment() object being
instantiated explicitly, just be aware of the fact that it is.

Now we move onto our custom model class. It looks like this:

```python
class MoneyModel(Model):
    def __init__(self, num_agents):
        super().__init__(seed=44)

        self.systemManager.addSystem(MoneySystem(self))

        for i in range(0,num_agents):
            self.environment.addAgent(MoneyAgent('a' + str(i), self))

    def run(self):
        while self.systemManager.timestep < 10:
            self.systemManager.executeSystems()
```

As you can see, we've created a MoneyModel class that inherits from the Model base class.
The model base class has two optional parameters: The environment as mentioed above
and the seed which have set to 44 in order for us to compare results. The seed
is used to construct a psuedo-random number generator that we can use whenever we
need to add a little stochasticity to our model. We've actually already used it indirectly 
when we called getRandomAgent() in our MoneySystem. By setting the seed of the random
number generator, we will get the same results every time. This is essential if
you want to make your work reproducible. You can use the model's random number generator
just like you would use python's random. It works in exactly the same way.

After we call the base constructor, we add our MoneySystem to the systemManger
using systemManager.addSystem(). This will automatically register our system with
the system manager. Next we add the agents. You'll notice that our MoneyModel can
have a variable number of agents (num_agents). We simply create that many agents
and store them in the environment using environment.addAgent(). You'll also notice
that we are ensuring that each agent has a unique iq by using the value of i. This is
a really simply yet effective method to ensure each agent is uniquely identified.

We then define a run method than we can call from outside the model class. This
method runs the model for 10 iterations. To do this we use the timestep property found
in the systemManager object.

lastly, we call the systemManager.executeSystems() method. This method is responsible
for calling the execute() method we defined for our MoneySystem class. At the
end of the executeSystems() method the systemManager will increase the timestep counter by 1.

That's it!!! Our model is finally complete. All we now have to do is run it.

## Running the Model:

To run our model, we will add this little bit of code at the bottom of our Tutorial.py
file:

```python
if __name__ == '__main__':
    model = MoneyModel(10)
    model.run() 

    print ([x.wealth for x in model.systemManager.getComponents(MoneyComponent)])
```

This code just creates a MoneyModel object (with 10 agents), runs the model using 
model.run() and then prints out the wealth distribution of the agents using
a bit of list comprehension.

If you run this code in an IDE or in the terminal like so (make sure your virtual 
environment is active!!):

```
$ python ./src/Tutorial.py
```

You should get the following output:

```python
[3, 0, 0, 1, 1, 1, 0, 1, 1, 2]
```

This is the wealth of all the agents by id. As you can tell Agent 0 is very
lucky and seems to have come out on top.

If you did not get this result, make sure that you set the seed of the model to 44
and, if you are still stuck, check the solution folder which contains a working solution
for this entire tutorial.

## Conclusion:

You have successfully created your first ABM using ECAgent. As you can hopefully tell,
ECAgent is incredibly flexible and be extended greatly. If you are still interested in learning
more about ECAgent, take a look at some of the other, more complicated, tutorials and,
if you have any questions, please feel free to email or message one of the devs and they will
be more than happy to assist you.

Some useful links:
* [ECAgent](https://github.com/BrandonGower-Winter/ABMECS)
* [ECAgentTutorials](https://github.com/BrandonGower-Winter/ECAgentTutorials) 