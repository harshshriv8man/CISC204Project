
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
import random

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:
    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"

#TODO Find out how to set b1-b8 to True or False. Seems like what we set is not considered and can and is overwritten
b1 = BasicPropositions("b1")
b2 = BasicPropositions("b2")
b3 = BasicPropositions("b3")
b4 = BasicPropositions("b4")
b5 = BasicPropositions("b5")
b6 = BasicPropositions("b6")
b7 = BasicPropositions("b7")
b8 = BasicPropositions("b8")
fuel = BasicPropositions("fuel")

arr = [b1, b2, b3, b4, b5, b6, b7, b8]
checkpoint_positions_1 = [] # Checkpoint positions for stage 1
checkpoint_positions_2 = [] # Checkpoint positions for stage 2
checkpoint_positions_3 = [] # Checkpoint positions for stage 3
RADIUS = 3
stage = 1

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Base constraints before calculations:
    E.add_constraint((~b1 & ~b2 & ~b3 & ~b4 & ~b5 & ~b6 & ~b7 & ~b8) >> ~fuel) # If fuel = 0, there is no fuel.
    # E.add_constraint((b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8) >> fuel) # If fuel > 0, there is fuel. Currently creates unsolvable solution error if added.
    
    # Ask user for initial conditions
    enter_fuel()

    # Calculations:

    grid1 = create_grid(RADIUS, 1)
    grid2 = create_grid(RADIUS, 2)
    grid3 = create_grid(RADIUS, 3)

    add_to_grid(grid1, 3, RADIUS//2, SpaceObject(P=True)) # Adds asteroid to demonstrate rocket avoidance proceedure.

    universe = [grid1, grid2, grid3]
    journey = rocket_dynamics(universe, RADIUS)

    debug_print(grid2, 2)

    # Unused concept to calculate rocket movement and run fuel_calc() in propositional logic (all 3 while loops):
    while (stage == 1):
        break
        # TODO: Add constraints to calculate the path, if nothing in the way should go straight right
        # TODO: Run fuel_calc() algorithm for every cell moved

    while (stage == 2):
        break
        # TODO: Add constraints to calculate the path
        # TODO: Based on path, need to run fuel_calc() algorithm for every cell moved

    while (stage == 3):
        break
        # TODO: Add constraints to calculate the path, if nothing in the way should go straight right
        # TODO: Add constraint that stops path from being calculated if next cell to the right is a planet

    return E

@proposition(E)
class Rocket: 
    def __init__(self, x, y, checkpoint1, checkpoint2, checkpoint3):
        self.checkpoint1 = checkpoint1
        self.checkpoint2 = checkpoint2
        self.checkpoint3 = checkpoint3
        self.x = x
        self.y = y

    def _prop_name(self):
        return f"A.{self.data}"

@proposition(E)
class SpaceObject:
    def __init__(self, P):
        self.Pf = P

    def _prop_name(self):
        return f"A.{self.data}"

"""
Currently unused and unfinished function.
"""
def fly(grid):
    assert fuel, "Rocket is out of fuel."
    #TODO something needs to put the rocket in the grid before it can fly
    fuel_calc()

@proposition(E)
class PlanetCell:
    def __init__(self, P):
        # Pf indicates if the rocket cannot pass into the object (i.e. Rocket cannot crash into a planet, Pf=True implies object. 
        # Pf=False also can imply nothing is there, with the exception of Checkpoints).
        self.Pf = P
    
    def _prop_name(self):
        return f"A.{self.data}"

"""
@param Direction can be 'x' or 'y'
"""
def move(object, direction, amount: int):
    if (direction == 'y'):
        object.y += amount
    elif (direction == 'x'):
        object.x += amount

def get_position(object):
    return (object.x, object.y)

"""
Creates grid given the radius of the planet held within and the stage of the rocket's journey.
@param stage takes in a value of either 1, 2, or 3, specifying the stage and thus the structure of the grid (stage 2 has the planet in the center of the grid,
stage 1 on the left, stage 2 on the right)
@param radius, the radius of the planet in the grid. Radius of 2 generates a 2x2 cell planet, though stage 1 and 3 only show one collumn of the planet in the grid.
@return the grid as a 2D array with a planet with the specified radius at its center.
"""
def create_grid(radius, stage):
    planet_coord = planet_position(radius, stage)
    rows = radius + 2
    grid = []

    for i in range(rows):
        row = []
        for j in range(rows):
            row.append(PlanetCell(P=False)) #setting each to false in grid first
        grid.append(row)
    
    
    for (y,x) in planet_coord:
        
        if 0 <= x < rows and 0 <= y < rows:
            grid[y][x].Pf = True # Grid's order is in [y][x] to improve spacial locality as movement in the x axis is more common.
    print("Checkpoint positions:")
    if (stage == 2 or stage == 3):
        print("x =", radius, end="\ny = ")
        for i in range(rows): # Places checkpoints on the far right edge of the planet in stage 2, and the cell to the left of the planet in stage 3.
            if grid[i][radius].Pf == False:
                if (stage == 2):
                    checkpoint_positions_2.append(True)
                else:
                    checkpoint_positions_3.append(True)
                print(i, end="; ") # DEBUG (Shows y position of current Checkpoint)
            else:
                if (stage == 2):
                    checkpoint_positions_2.append(False)
                else:
                    checkpoint_positions_3.append(False)
    else:
        print("x =", radius + 1, end="\ny = ")
        for i in range(rows): # Stage 1 needs to end at the end of the grid, so Checkpoints are placed there.
            if grid[i][radius + 1].Pf == False:
                checkpoint_positions_1.append(True)
                
                print(i, end="; ") # DEBUG (Shows y position of current Checkpoint)
            else:
                checkpoint_positions_1.append(False)

    print()
    
    debug_print(grid, stage) # DEBUG
    return grid

"""
Prints given grid such that cells containing a planet print True in green, cells with a Checkpoint print False in yellow, and everything else prints False in red.
"""
def debug_print(grid, stage: int):
    x = 0
    y = 0
    for row in grid:
        for cell in row:
            if (cell.Pf):
                print("\033[32m", end="")
            # Essentially, want the checkpoints to be active (yellow) until the rocket gets there, then change to a duller colour
            elif (stage == 1 and x == RADIUS + 1 and checkpoint_positions_1[y]):
                print("\033[93m", end="")
            elif (stage == 2 and x == RADIUS  and checkpoint_positions_2[y]):
                print("\033[93m", end="")
            elif (stage == 3 and x == RADIUS and checkpoint_positions_3[y]):
                print("\033[93m", end="")
            else:
                print("\033[31m", end="")
            print(f"{cell.Pf}, ", end="")
            x += 1
        print("\b\b  ")
        x = 0
        y += 1
    print("\033[0m")

"""
Adds proposition object (default SpaceObject) to specified grid at location x, y.
"""
def add_to_grid(grid, x: int, y: int, object=SpaceObject(P=True)) -> None:
    if (grid[y][x].Pf == False):
        grid[y][x] = object
    else:
        assert grid[y][x].Pf == True, f"Object already exists at {x}, {y}"

'''
Sets the planet positions for all 3 stages. 
@return the coordinate list (planet_coord) to be used create_grid function.
'''
def planet_position(radius, stage):
    planet = []
    h=0

    if (stage == 1):
        for y in range(1, radius+1):
            planet.append((y, 0))
        return planet
    
    #TODO Note that we can have planets of different radius in each stage. Same for now for testing purpose, will change later. 

    if (stage == 2):
        for x in range(1, radius + 1):
            for y in range(1, radius +1):
                planet.append((y, x))
                h += 1
        return planet
    
    if (stage == 3):
        for y in range(1, radius+1):
            planet.append((y, radius+1))
        return planet
    
    print(planet)

'''
Rocket dynamics function maps the moving of the rocket in all 3 stages. 
@param universe: a list of the three grids corresponding to each stage, radius of planet, and stage starting from 1
@return a list of tuples (coordinates) that the rocket follows as it travels
'''
def rocket_dynamics(universe, radius, stage=1):
    journey = []
   # ------------------------------------ STAGE 1 ------------------------------------
    if (stage == 1):
        grid = universe[0] # Grid 1 for stage 1
        print(f"Stage:{stage}")

        launch = radius//2 # Rocket starts in the middle of the planet
        rocket = Rocket(checkpoint1=False, checkpoint2=False, checkpoint3=False, x=1, y=launch)

        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True)) # Uses SpaceObject as a placeholder for the Rocket in the grid to visualize.
        journey.append(get_position(rocket)) # Add initial position to map

        debug_print(grid, stage)
        print(f"Stage:{stage}")

        while rocket.x < radius+1: # Loop until end of grid, where the stage will switch
            x, y = get_position(rocket) # Position before move

            # In grid 1, rocket will move rightward always, unless blocked by a space object, in which case it moves up/down    
            if grid[y][x+1].Pf:
                if x-1 >= 0 and not grid[y-1][x].Pf:
                    move(rocket, 'y', 1)
                elif x+1 <= radius + 1 and not grid[y+1][x].Pf:
                    move(rocket, 'y', -1)

            else:
                move(rocket, 'x', 1)

            journey.append(get_position(rocket))
            add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True))
            grid[y][x].Pf=False # Sets previous Rocket position to empty space
            debug_print(grid, stage)   

        x,y = get_position(rocket)
        if x == radius + 1:
                # Check if all the positions in the next column (x == radius) are clear (opposite of checkpoint_positions_1)
                all_clear = False
                for i in range(len(checkpoint_positions_1)):
                    if checkpoint_positions_1[i] == grid[i][radius+1].Pf:  
                        all_clear = True
                        break

                # If there are no obstacles in the next column, move to the next stage
                if all_clear:
                    print(f"Rocket reached the checkpoint at ({x}, {y}) in stage 1. Moving to stage 2.", end="\n")
                    stage = 2  # Move to the next stage (stage 2) 
        
        print(f"Stage:{stage}", end="\n")

        print("Journey Path: ", end="\n") # Print the journey coordinates (path) of the rocket
        for step in journey:
            print(f"({step[0]}, {step[1]})", end=" -> ")
        print()

        # ------------------------------------ STAGE 2 ------------------------------------
        if (stage == 2):
            return

"""
Sets fuel to the number specified by the user.
"""
def enter_fuel() -> None:
    fuel_str = input("Please enter the rocket's starting fuel amount in binary, up to 8 digits.\n")
    assert len(fuel_str) < 9, "Your number is more than 8 digits"
    i = 0
    for num in fuel_str:
        if (num == '1'):
            arr[i] = True # This just changed arr[i] to True, not set the proposition to True. How do we set the proposition's status?
                          # Idea: Create two classes, one with the constraint that it is always True, one that it is always False, then set b1-b8 to be one of those
                          # propositions and change/set a new b{x} to the other when that b{x} is changed.
        elif (num == '0'):
            arr[i] = False
        else:
            print("The character at index", i, "cannot be accepted.")
            return
        i += 1
    if (i<7):
        for j in range(i, 8): # If the binary number entered is less than 8 digits, set the remaining binary values to false.
            arr[j] = False
    print(arr)

""" Subtract 1 to arr (value of fuel). If arr is filled with false (Fuel = 0) sets fuel to False and ends process, returning fuel.
"""
def fuel_calc():
    for i in arr: 
        if i:
            i = False
            break
        i = True
    if (not b1 and not b2 and not b3 and not b4 and not b5 and not b6 and not b7 and not b8):
        fuel = False # TODO: Does not set universal proposition "fuel" to False? Why?

# Included code as reference:

# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
# @constraint.at_least_one(E)
# @proposition(E)
# class FancyPropositions:

#     def __init__(self, data):
#         self.data = data

#     def _prop_name(self):
#         return f"A.{self.data}"

# At least one of these will be true
# x = FancyPropositions("x")
# y = FancyPropositions("y")
# z = FancyPropositions("z")

if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T)) # This doesn't work, produces error!

    S = T.solve()

    if(S):
        print("Solution: %s" % S)
    else:
        print("No solution!")
    print()
