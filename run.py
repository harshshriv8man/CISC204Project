
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

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
people_positions = []
checkpoint_positions_1 = [] # Checkpoint positions for stage 1
checkpoint_positions_2 = [] # Checkpoint positions for stage 2
checkpoint_positions_3 = [] # Checkpoint positions for stage 3
RADIUS = 4
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

    add_people(grid1, RADIUS, 1)
    add_people(grid2, RADIUS, 2)
    add_people(grid3, RADIUS, 3)

    # debug_print(grid1, 1)
    # debug_print(grid2, 2)
    # debug_print(grid3, 3)

    # TODO: Ask the user what y,x coordinates they would like a SpaceObject to be. Loop this until they enter "stop".

    # Function

    add_to_grid(grid1, 3, RADIUS//2, SpaceObject(P=True)) # Adds asteroid to demonstrate rocket avoidance proceedure.

    universe = [grid1, grid2, grid3]
    journey = rocket_stage_3(universe, RADIUS) # Array of tuples of every rocket position along its path through every stage.

    current_stage = 1
    reachable1 = []
    reachable2 = []
    reachable3 = []
    for position in journey:
        if (position == (-1, -1)):
            current_stage += 1
        elif current_stage == 1:
            reachable1.append(position)
            for x in range(3):
                for y in range(3):
                    E.add_constraint(Reachable(position[1] - 1 + x, position[0] - 1 + y, 1))
        elif current_stage == 2:
            reachable2.append(position)
            for x in range(3):
                for y in range(3):
                    E.add_constraint(Reachable(position[1] - 1 + x, position[0] - 1 + y, 2))
        else:
            reachable3.append(position)
            for x in range(3):
                for y in range(3):
                    E.add_constraint(Reachable(position[1] - 1 + x, position[0] - 1 + y, 3))

    beacons = [Beacon(0, 0, 1), Beacon(0, 1, 1), Beacon(0, 2, 1), Beacon(0, 3, 1), Beacon(0, 4, 1), Beacon(0, 5, 1), Beacon(0, 6, 1)] # Temporary
    
    constraint.add_at_most_k(E, 6, beacons) # Arbitrarily chosen to get 6 beacons across all three grids

    # TODO: Add a loop that adds if each position is reachable based on 'journey' to E.constraints.

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
class Beacon:
    def __init__(self, x, y, grid: int):
        self.x = x
        self.y = y
        self.grid = grid

    def _prop_name(self):
        return f"({self.y}, {self.x}) is a beacon.\n" # (y, x) format

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

@proposition(E)
class Reachable:
    def __init__(self, x, y, grid: int):
        self.x = x
        self.y = y
        self.grid = grid

    def _prop_name(self):
        return f"({self.y}, {self.x}) is reachable." # (y, x) format

@proposition(E)
class PlanetCell:
    def __init__(self, P):
        # Pf indicates if the rocket cannot pass into the object (i.e. Rocket cannot crash into a planet, Pf=True implies object. 
        # Pf=False also can imply nothing is there, with the exception of Checkpoints).
        self.Pf = P
    
    def _prop_name(self):
        return f"A.{self.data}"

@proposition(E)
class Person:
    def __init__(self, T, x, y, P=False):
        self.Pf = P # Kill this later
        self.T = T # T for translucent
        self.x = x
        self.y = y
    
    def _prop_name(self):
        return f"Person at ({self.y}, {self.x}) (y, x)"

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
    rows = (int)(radius * 2)
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
            if grid[i][radius * 2 - 2].Pf == False:
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
            if grid[i][(int)(radius*2) - 1].Pf == False:
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
            if (y, x, stage) in people_positions:
                print("\033[36m", end="")
                print(" True, ", end="")
            else:
                if (cell.Pf):
                    print("\033[32m", end="")
                # Essentially, want the checkpoints to be active (yellow) until the rocket gets there, then change to a duller colour
                elif (stage == 1 and x == RADIUS*2 - 1 and checkpoint_positions_1[y]):
                    print("\033[93m", end="")
                elif (stage == 2 and x == RADIUS  and checkpoint_positions_2[y]):
                    print("\033[93m", end="")
                elif (stage == 3 and x == RADIUS*2 - 2 and checkpoint_positions_3[y]):
                    print("\033[93m", end="")

                else:
                    print("\033[31m", end="")
                if (cell.Pf):
                    print(f" {cell.Pf}, ", end="")
                else:
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
        return True
    else:
        assert grid[y][x].Pf == True, f"Object already exists at {x}, {y}"
        return False

def add_people(grid, radius, stage):
    x = 0
    y = 0
    a = 0
    while (x < radius*2):
        while (y < radius*2):
            if ((a % 3 == 0 and (a-2) % 2 == 0 and ((a*2) // 3) % 3 == 0) or ((a // 5 + 1) % 2 == 0 and a % 5 == 0)): # Non-specific consistant pattern to add people to grid
                occupied = add_to_grid(grid, x, y, Person(True, x, y))
                if (occupied):
                    people_positions.append((y, x, stage))
            y += 1
            a += 1
        y = 0
        x += 1

'''
Sets the planet positions for all 3 stages. 
@return the coordinate list (planet_coord) to be used create_grid function.
'''
def planet_position(radius, stage):
    planet = []
    h=0

    if (stage == 1):
        for y in range(radius//2, radius*2 - radius//2 - radius % 2):
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
            planet.append((y, radius * 2 - 1))
        return planet
    
    print(planet)

'''
Rocket dynamics function maps the moving of the rocket in all 3 stages. 
@param universe: a list of the three grids corresponding to each stage, radius of planet, and stage starting from 1
@return a list of tuples (coordinates) that the rocket follows as it travels
'''
def rocket_stage_1(universe, radius, stage=1):
    journey = []
    if (stage == 1):
        grid = universe[0] # Grid 1 for stage 1
        print(f"Stage:{stage}")

        launch = radius//2 # Rocket starts in the middle of the planet
        rocket = Rocket(checkpoint1=False, checkpoint2=False, checkpoint3=False, x=1, y=launch)

        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True)) # Uses SpaceObject as a placeholder for the Rocket in the grid to visualize.
        journey.append(get_position(rocket)) # Add initial position to map

        debug_print(grid, stage)
        print(f"Stage:{stage}")

        while rocket.x < int(radius*2)-1: # Loop until end of grid, where the stage will switch
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
        
        if x == int(radius*2)-1:
                # Check if all the positions in the next column (x == radius) are clear (opposite of checkpoint_positions_1)
                all_clear = False
                for i in range(len(checkpoint_positions_1)):
                    if checkpoint_positions_1[i] == grid[i][int(radius*2)-1].Pf:  
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
    return journey

def rocket_stage_2(universe, radius, stage=2):
    journey = rocket_stage_1(universe, radius, stage=1)
    journey.append((-1,-1))
    grid = universe[1]
    print(f"Stage: {stage}")

    start_x, start_y = 0, radius + 1
    rocket = Rocket(checkpoint1=False, checkpoint2=False, checkpoint3=False, x=start_x, y=start_y)

    add_to_grid(grid,rocket.x,rocket.y,SpaceObject(P=True))
    journey.append(get_position(rocket))
    debug_print(grid,stage)

    while rocket.y > 0 :
        x, y = get_position(rocket)

        if rocket.x < radius + 1:
            move(rocket, 'x', 1)
        elif rocket.x == radius + 1:
            if y > 0:
                move(rocket, 'y', -1)
        else:
            move(rocket, 'x', -1)

        journey.append(get_position(rocket))  # Update journey with new position
        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True))  # Visualize rocket in grid
        grid[y][x].Pf = False  # Clear previous rocket position
        debug_print(grid, stage)

    while rocket.y == 0:
        x, y = get_position(rocket)
        move(rocket, 'x', -1)

        if rocket.x == 0 and rocket.y == 0:  # End condition, when we reach (0, 0)
            journey.append(get_position(rocket))  # Update journey with new position
            add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True))  # Visualize rocket in grid
            grid[y][x].Pf = False  # Clear previous rocket position
            debug_print(grid, stage)
            break

        journey.append(get_position(rocket))  # Update journey with new position
        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True))  # Visualize rocket in grid
        grid[y][x].Pf = False  # Clear previous rocket position
        debug_print(grid, stage)

    print(f"Stage:{stage} Complete!")
    print("Journey Path: ", end="\n")
    for step in journey:
        print(f"({step[0]}, {step[1]})", end=" -> ")
    print()

    return journey

def rocket_stage_3(universe, radius, stage=3):
    journey = rocket_stage_2(universe, radius, stage=2)
    journey.append((-1,-1))
    grid = universe[2] # Grid 3 for stage 3
    print(f"Stage:{stage}")

    launch = radius//2 # Rocket starts in the middle of the planet
    rocket = Rocket(checkpoint1=False, checkpoint2=False, checkpoint3=False, x=1, y=launch)

    add_to_grid(grid, rocket.x, rocket.y, SpaceObject(P=True)) # Uses SpaceObject as a placeholder for the Rocket in the grid to visualize.
    journey.append(get_position(rocket)) # Add initial position to map

    debug_print(grid, stage)
    print(f"Stage:{stage}")

    while rocket.x < int(radius*2)-2: # Loop until end of grid, where the stage will switch
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
        
    if x == int(radius*2)-2:
            # Check if all the positions in the next column (x == radius) are clear (opposite of checkpoint_positions_1)
            all_clear = False
            for i in range(len(checkpoint_positions_1)):
                if checkpoint_positions_1[i] == grid[i][int(radius*2)-1].Pf:  
                    all_clear = True
                    break

            # If there are no obstacles in the next column, move to the next stage
            if all_clear:
                print(f"Rocket reached the end of the journey at ({x}, {y})!", end="\n")
        
    print(f"Stage:{stage}", end="\n")

    print("Journey Path: ", end="\n") # Print the journey coordinates (path) of the rocket
    for step in journey:
        print(f"({step[0]}, {step[1]})", end=" -> ")
    print("End of journey!")   
    
    return journey

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
