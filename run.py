
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

people_positions = [] # (y, x, stage)
checkpoint_positions_1 = [] # Checkpoint positions for stage 1
checkpoint_positions_2 = [] # Checkpoint positions for stage 2
checkpoint_positions_3 = [] # Checkpoint positions for stage 3
RADIUS = 2 # Changes the radius of all planets, also increasing the size of the grid by 2*RADIUS
BEACON_RANGE = 1 # The range at which a beacon can save a person

def example_theory():
    # Calculations:

    grid1 = create_grid(RADIUS, 1)
    grid2 = create_grid(RADIUS, 2)
    grid3 = create_grid(RADIUS, 3)

    add_people(grid1, RADIUS, 1)
    add_people(grid2, RADIUS, 2)
    add_people(grid3, RADIUS, 3)

    print("Stage 1:")
    debug_print(grid1, 1)

    print("Stage 2:")
    debug_print(grid2, 2)

    print("Stage 3:")
    debug_print(grid3, 3)

    # Ask user for initial conditions
    (grid1, grid2, grid3) = enter_space_objects(grid1, grid2, grid3)

    universe = [grid1, grid2, grid3]
    journey = rocket_stage_3(universe, RADIUS) # Array of tuples of every rocket position along its path through every stage.

    # Main constraints:

    # Determine Rocket reachability.
    current_stage = 1
    reachable = [] # (y, x, grid)
    beacons = [] # Beacon(x, y, grid)
    for position in journey:
        if (position == (-1, -1)):
            current_stage += 1
        else:
            for x in range(3):
                for y in range(3):
                    # Outside the grid is not reachable
                    if (position[0] - 1 + y > -1 and position[1] - 1 + x > -1 and position[0] - 1 + y < RADIUS * 2 and position[1] - 1 + x < RADIUS * 2):
                        reachable.append((position[0] - 1 + y, position[1] - 1 + x, current_stage))
                        beacons.append(Beacon(position[1] - 1 + x, position[0] - 1 + y, current_stage)) # Makes every possible reachable Beacon position (less calculations than every possible Beacon position)
                        E.add_constraint(Reachable(position[1] - 1 + x, position[0] - 1 + y, current_stage))


    # A Beacon can't be on other objects

    for grid in range(3):
        for x in range(RADIUS * 2):
            for y in range(RADIUS * 2):

                # Beacon must be within Rocket reachability
                if ((y, x, grid+1) not in reachable):
                    E.add_constraint(~Beacon(x, y, grid+1))
                
                # Beacon cannot be on a planet, person, or a SpaceObject with P=True.
                E.add_constraint(PlanetCell(x, y, grid+1, True) >> ~Beacon(x, y, grid+1))
                E.add_constraint(SpaceObject(x, y, grid+1, True) >> ~Beacon(x, y, grid+1))
                E.add_constraint(Person(x, y, grid+1) >> ~Beacon(x, y, grid+1))


    # Determine if a person is within a beacon's reachability.

    reach = []
    for i in people_positions:
        for x in range(BEACON_RANGE * 2 + 1):
            for y in range(BEACON_RANGE * 2 + 1):
                if (i[0] - BEACON_RANGE + y >= 0 and i[1] - BEACON_RANGE + x >= 0):
                    reach.append((i[0] - BEACON_RANGE + y, i[1] - BEACON_RANGE + x, i[2])) # (y, x, stage)


    # A beacon can't save no people (If no people are inside its radius, there cannot be a Beacon there)

    not_beacon = []
    for i in reach:
        for grid in range(3):
            for y in range(RADIUS*2):
                for x in range(RADIUS*2):
                    if (y, x, grid + 1) not in reach:
                        not_beacon.append((y, x, grid + 1))
                        E.add_constraint(~Beacon(x, y, grid + 1))


    # Beacon must save at least 1 more person (if one person is saved by a beacon, they cannot be the only person saved by a different beacon)
    # Summary: Go out by radius * 2, if there are no people within that range, change nothing. If there are, the overlap of radii can have a beacon, so the places on the
    # focused person that do not have overlap cannot have a beacon.

    for a in range(len(people_positions)):
        self_pos = people_positions[a]
        conjunct_pos = []
        for b in range(len(people_positions)):
            other_pos = people_positions[b]

            # Early check to lower average computation
            if (self_pos != other_pos and self_pos[2] == other_pos[2] # If not the same person, if in the same grid
            and other_pos[0] >= self_pos[0] - BEACON_RANGE * 2 and other_pos[0] <= self_pos[0] + BEACON_RANGE * 2 # If y range overlaps
            and other_pos[1] >= self_pos[1] - BEACON_RANGE * 2 and other_pos[1] <= self_pos[1] + BEACON_RANGE * 2 # If x range overlaps
            ):
                # Find location(s) of conjunction(s)
                for x_self in range(BEACON_RANGE * 2 + 1):
                    for y_self in range(BEACON_RANGE * 2 + 1):
                        for x in range(BEACON_RANGE * 2 + 1):
                            for y in range(BEACON_RANGE * 2 + 1):
                                if (other_pos[1] - BEACON_RANGE + x == self_pos[1] - BEACON_RANGE + x_self # What x value overlaps?
                                and other_pos[0] - BEACON_RANGE + y == self_pos[0] - BEACON_RANGE + y_self # What y value overlaps?
                                ):
                                    if((self_pos[0] - BEACON_RANGE + y_self, self_pos[1] - BEACON_RANGE + x_self, self_pos[2]) in reachable):
                                        conjunct_pos.append((self_pos[0] - BEACON_RANGE + y_self, self_pos[1] - BEACON_RANGE + x_self, self_pos[2]))

        # If there is a conjunction, set all non-conjunction cells relative to self_pos to ~Beacon(...)
        if len(conjunct_pos) != 0:
            for x in range(BEACON_RANGE * 2 + 1):
                for y in range(BEACON_RANGE * 2 + 1):
                    if ((self_pos[0] - BEACON_RANGE + y, self_pos[1] - BEACON_RANGE + x, self_pos[2]) not in conjunct_pos):
                        E.add_constraint(~Beacon(x, y, self_pos[2]))


    # Implied Beacon constraints:

    # Beacon cannot be on another beacon. -- This would already be covered with the beacons list.
    constraint.add_at_most_k(E, 6, beacons) # SAT Solver gets up to 6 Beacons to place across all 3 grids
    print("added final constraint")

    return E


@proposition(E)
class Beacon:
    def __init__(self, x, y, grid: int):
        self.x = x
        self.y = y
        self.grid = grid

    def _prop_name(self):
        return f"\033[36m Beacon at ({self.y}, {self.x}). \033[0m"  # (y, x) format

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
    def __init__(self, x, y, grid, P):
        self.x = x
        self.y = y
        self.grid = grid
        self.P = P

    def _prop_name(self):
        return f"Space Object at ({self.y}, {self.x}, {self.grid}), P={self.P}"

@proposition(E)
class Reachable:
    def __init__(self, x, y, grid: int):
        self.x = x
        self.y = y
        self.grid = grid

    def _prop_name(self):
        return f"({self.y}, {self.x}, {self.grid}) is reachable." # (y, x) format

@proposition(E)
class PlanetCell:
    def __init__(self, x, y, grid: int, P):
        # P indicates if the rocket cannot pass into the object (i.e. Rocket cannot crash into a planet, P=True implies object. 
        # P=False also can imply nothing is there, with the exception of Checkpoints).
        self.P = P
        self.x = x
        self.y = y
        self.grid = grid
    
    def _prop_name(self):
        return f"Grid at: ({self.y}, {self.x}, {self.grid})"

@proposition(E)
class Person:
    def __init__(self, x, y, grid: int, P=False):
        self.P = P
        self.x = x
        self.y = y
        self.grid = grid
    
    def _prop_name(self):
        return f"Person at ({self.y}, {self.x}) (y, x)"

"""
Queue of positions.
"""
class PositionQueue:
    def __init__(self, previous, x, y, length):
        self.queue_previous = previous
        self.x = x
        self.y = y
        self.length = length

    def get_previous(self):
        return self.queue_previous
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def len(self):
        return self.length

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
            row.append(PlanetCell(i, j, stage, P=False)) # Setting entire grid to a false PlanetCell to represent empty space first
        grid.append(row)
    
    
    for (y,x) in planet_coord:
        
        # Put a planet in the empty space (grid)
        if 0 <= x < rows and 0 <= y < rows:
            grid[y][x].P = True # Grid's order is in [y][x] to improve spacial locality as movement in the x axis is more common.
            E.add_constraint(PlanetCell(x, y, stage, True))
    if (stage == 2 or stage == 3):
        for i in range(rows): # Places checkpoints on the far right edge of the planet in stage 2, and the cell to the left of the planet in stage 3.
            if grid[i][radius * 2 - 2].P == False:
                if (stage == 2):
                    checkpoint_positions_2.append(True)
                else:
                    checkpoint_positions_3.append(True)
            else:
                if (stage == 2):
                    checkpoint_positions_2.append(False)
                else:
                    checkpoint_positions_3.append(False)
    else:
        for i in range(rows): # Stage 1 needs to end at the end of the grid, so Checkpoints are placed there.
            if grid[i][(int)(radius*2) - 1].P == False:
                checkpoint_positions_1.append(True)
            else:
                checkpoint_positions_1.append(False)
    
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
                if (cell.P):
                    print("\033[32m", end="")
                elif (stage == 1 and x == RADIUS*2 - 1 and checkpoint_positions_1[y]):
                    print("\033[93m", end="")
                elif (stage == 2 and x == RADIUS  and checkpoint_positions_2[y]):
                    print("\033[93m", end="")
                elif (stage == 3 and x == RADIUS*2 - 2 and checkpoint_positions_3[y]):
                    print("\033[93m", end="")

                else:
                    print("\033[31m", end="")
                if (cell.P):
                    print(f" {cell.P}, ", end="")
                else:
                    print(f"{cell.P}, ", end="")
                
            x += 1
        print("\b\b  ")
        x = 0
        y += 1
    print("\033[0m")

"""
Adds proposition object (default SpaceObject(x, y, grid, P=True), set within function) to specified grid at location x, y.
"""
def add_to_grid(grid, x: int, y: int, object=SpaceObject(-1, -1, -1, P=True)) -> bool:
    # To set default SpaceObject using given x, y, grid values (can't use the x, y, grid values in the parameters)
    if object == SpaceObject(-1, -1, -1, True):
        object = SpaceObject(x, y, grid, P=True)
    if (grid[y][x].P == False):
        grid[y][x] = object
        return True
    else:
        assert grid[y][x].P == True, f"Object already exists at {x}, {y}"
        return False

def add_people(grid, radius, stage):
    x = 0
    y = 0
    a = 0
    while (x < radius*2):
        while (y < radius*2):
            if ((a % 3 == 0 and (a-2) % 2 == 0 and ((a*2) // 3) % 3 == 0) or ((a // 5 + 1) % 2 == 0 and a % 5 == 0)): # Non-specific consistant pattern to add people to grid
                not_occupied = add_to_grid(grid, x, y, Person(x, y, grid))
                if (not_occupied):
                    E.add_constraint(Person(x, y, stage))
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
    if stage == 1:
        grid = universe[0]  # Grid 1 for stage 1
        print(f"Stage: {stage}")

        launch = radius - 1  # Rocket starts in the middle of the planet
        rocket = Rocket(checkpoint1=False, checkpoint2=False, checkpoint3=False, x=1, y=launch)

        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid, P=True))  # Visualize rocket in grid
        journey.append(get_position(rocket))  # Add initial position to map

        debug_print(grid, stage)
        print(f"Stage: {stage}")
        
        direction = 0  # Start by moving to the right (x++)
        queue = PositionQueue(None, rocket.x, rocket.y, 1)  # Queue to track rocket's positions

        visited_positions = set()  # Set to track visited positions and directions

        while rocket.x < int(radius * 2) - 1:  # Loop until end of grid, where the stage will switch
            x, y = get_position(rocket)  # Position before move

            if (x, y, direction) in visited_positions:  # Check if current position with direction is visited before
                print("Unsolvable, no valid path for the Rocket in stage 1 (detected loop).")
                return journey  # If visited before, exit the function as it's unsolvable
            visited_positions.add((x, y, direction))  # Add the current position and direction to the visited set

            # Move in the current direction
            if direction == 0:  # Move right (x++)
                if x + 1 > int(radius * 2) - 1 or grid[y][x + 1].P:  # If next position in x is blocked or out of bounds
                    direction = (direction + 1) % 4  # Try the next direction (down)
                else:
                    move(rocket, 'x', 1)

            elif direction == 1:  # Move down (y++)
                if y + 1 > int(radius * 2) - 1 or grid[y + 1][x].P:  # If next position in y is blocked or out of bounds
                    direction = (direction + 1) % 4  # Try the next direction (left)
                else:
                    move(rocket, 'y', 1)

            elif direction == 2:  # Move left (x--)
                if x - 1 < 0 or grid[y][x - 1].P:  # If next position in x is blocked or out of bounds
                    direction = (direction + 1) % 4  # Try the next direction (up)
                else:
                    move(rocket, 'x', -1)

            elif direction == 3:  # Move up (y--)
                if y - 1 < 0 or grid[y - 1][x].P:  # If next position in y is blocked or out of bounds
                    direction = (direction + 1) % 4  # Try the next direction (right)
                else:
                    move(rocket, 'y', -1)

            # Track the rocket's journey
            if (rocket.x, rocket.y) != (x, y):  # If the position has changed, update journey
                queue = PositionQueue(queue, rocket.x, rocket.y, queue.len() + 1)  # Add current position to queue
                journey.append(get_position(rocket))  # Add new position to journey

                # Visualize rocket in grid
                add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid, P=True))
                grid[y][x].P = False  # Set previous position to empty space
                debug_print(grid, stage)

        # Check if we have reached the end of the journey and can proceed to the next stage
        x, y = get_position(rocket)
        if x == int(radius * 2) - 1:
            # Check if the column ahead is clear of obstacles
            all_clear = False
            for i in range(len(checkpoint_positions_1)):
                if checkpoint_positions_1[i] == grid[i][int(radius * 2) - 1].P:
                    all_clear = True
                    break

            if all_clear:
                print(f"Rocket reached the checkpoint at ({x}, {y}) in stage 1. Moving to stage 2.", end="\n")
                stage = 2  # Move to the next stage (stage 2)

        print(f"Stage: {stage}", end="\n")
        print("Journey Path: ", end="\n")
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

    visited_positions = set()

    add_to_grid(grid,rocket.x,rocket.y,SpaceObject(rocket.x, rocket.y, grid, P=True))
    journey.append(get_position(rocket))
    debug_print(grid,stage)

    while rocket.y > 0 :
        x, y = get_position(rocket)

        if (x, y) in visited_positions:  # Check if current position with direction is visited before
                print("Unsolvable, no valid path for the Rocket in stage 1 (detected loop).")
                return journey  # If visited before, exit the function as it's unsolvable
        visited_positions.add((x, y))  # Add the current position and direction to the visited set

        if rocket.x < radius + 1:
            move(rocket, 'x', 1)
        elif rocket.x == radius + 1:
            if y > 0:
                move(rocket, 'y', -1)
        else:
            move(rocket, 'x', -1)

        journey.append(get_position(rocket))  # Update journey with new position
        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid,P=True))  # Visualize rocket in grid
        grid[y][x].P = False  # Clear previous rocket position
        debug_print(grid, stage)

    while rocket.y == 0:
        x, y = get_position(rocket)
        move(rocket, 'x', -1)

        if rocket.x == 0 and rocket.y == 0:  # End condition, when we reach (0, 0)
            journey.append(get_position(rocket))  # Update journey with new position
            add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid, P=True))  # Visualize rocket in grid
            grid[y][x].P = False  # Clear previous rocket position
            debug_print(grid, stage)
            break

        journey.append(get_position(rocket))  # Update journey with new position
        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid, P=True))  # Visualize rocket in grid
        grid[y][x].P = False  # Clear previous rocket position
        debug_print(grid, stage)

    print(f"Stage:{stage} Complete!")
    print("Journey Path: ", end="\n")
    for step in journey:
        print(f"({step[0]}, {step[1]})", end=" -> ")
    print()

    return journey

def rocket_stage_3(universe, radius, stage=3):
    # Call stage 2 and append the ending point as a placeholder for Stage 3
    journey = rocket_stage_2(universe, radius, stage=2)
    journey.append((-1,-1))  # Placeholder for separation between stages
    grid = universe[2]
    print(f"Stage: {stage}")

    launch = radius - 1  # Rocket starts in the middle of the planet
    rocket = Rocket(checkpoint1=False, checkpoint2=False, checkpoint3=False, x=1, y=launch)

    add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid, P=True))
    journey.append(get_position(rocket))  # Add initial position to map

    debug_print(grid, stage)
    print(f"Stage:{stage}")

    direction = 0  # Start by moving right (x++)
    visited_positions = set()  # Set to track visited positions with direction

    while rocket.x < int(radius * 2) - 2:  # Loop until end of grid
        x, y = get_position(rocket)

        if (x, y, direction) in visited_positions:  # Loop detection
            print("Unsolvable, no valid path for the Rocket in stage 3 (detected loop).")
            return journey
        visited_positions.add((x, y, direction))

        # Check direction and move the rocket
        if direction == 0:  # Move right (x++)
            if x + 1 > int(radius * 2) - 1 or grid[y][x + 1].P:  # Blocked or out of bounds
                direction = (direction + 1) % 4  # Try moving down
            else:
                move(rocket, 'x', 1)

        elif direction == 1:  # Move down (y++)
            if y + 1 > int(radius * 2) - 1 or grid[y + 1][x].P:  # Blocked or out of bounds
                direction = (direction + 1) % 4  # Try moving left
            else:
                move(rocket, 'y', 1)

        elif direction == 2:  # Move left (x--)
            if x - 1 < 0 or grid[y][x - 1].P:  # Blocked or out of bounds
                direction = (direction + 1) % 4  # Try moving up
            else:
                move(rocket, 'x', -1)

        elif direction == 3:  # Move up (y--)
            if y - 1 < 0 or grid[y - 1][x].P:  # Blocked or out of bounds
                direction = (direction + 1) % 4  # Try moving right
            else:
                move(rocket, 'y', -1)

        journey.append(get_position(rocket))
        add_to_grid(grid, rocket.x, rocket.y, SpaceObject(rocket.x, rocket.y, grid, P=True))
        grid[y][x].P = False  # Clear previous rocket position
        debug_print(grid, stage)

        x, y = get_position(rocket)

    if x == int(radius * 2) - 2:
        # Check if all the positions in the next column are clear
        all_clear = False
        for i in range(len(checkpoint_positions_1)):
            if checkpoint_positions_1[i] == grid[i][int(radius * 2) - 1].P:
                all_clear = True
                break

        if all_clear:
            print(f"Rocket reached the end of the journey at ({x}, {y})!", end="\n")

    print(f"Stage:{stage}", end="\n")

    print("Journey Path: ", end="\n")
    for step in journey:
        print(f"({step[0]}, {step[1]})", end=" -> ")
    print("End of journey!")

    return journey

def enter_space_objects(grid1, grid2, grid3) -> tuple:
    complete = False
    print("Please enter the position of a SpaceObject in the format 'y, x, grid'.\nSpaceObjects on people, planets, or the starting position of the rocket will not be accepted.\nType 'stop' to continue with currently set SpaceObjects.")
    while not complete:
        SpaceObject_str = input("\n")
        if (SpaceObject_str != "stop"):
            SpaceObject_list = SpaceObject_str.split(", ")
            if (len(SpaceObject_list) == 3 and SpaceObject_list[0].isdigit() and SpaceObject_list[1].isdigit() and SpaceObject_list[2].isdigit()):
                y = (int)(SpaceObject_list[0])
                x = (int)(SpaceObject_list[1])
                stage = (int)(SpaceObject_list[2])
                if (y > -1 and y < RADIUS * 2 and x > -1 and x < RADIUS * 2 and stage < 4 and stage > 0):
                    success = False
                    if stage == 1:
                        if (grid1[y][x].P == False and (y, x, stage) not in people_positions and (y, x) != (RADIUS - 1, 1)):
                            success = add_to_grid(grid1, (int)(SpaceObject_list[1]), (int)(SpaceObject_list[0]))
                    elif stage == 2:
                        if (grid2[y][x].P == False and (y, x, stage) not in people_positions and (y, x) != (RADIUS, 0)):
                            success = add_to_grid(grid2, (int)(SpaceObject_list[1]), (int)(SpaceObject_list[0]))
                    else:
                        if (grid3[y][x].P == False and (y, x, stage) not in people_positions and (y, x) != (RADIUS - 1, 0)):
                            success = add_to_grid(grid3, (int)(SpaceObject_list[1]), (int)(SpaceObject_list[0]))
                    print(f"Adding SpaceObject to ({SpaceObject_list[0]}, {SpaceObject_list[1]}, {SpaceObject_list[2]})", end=" ")
                    if (success):
                        E.add_constraint(SpaceObject(x, y, stage, True))
                        print("succeeded.")
                    else:
                        print("failed.")
            else:
                print("Invalid format.")
        else:
            complete = True
    return (grid1, grid2, grid3)


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
