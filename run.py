
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

#TODO Find out how to set b1-b8 to True or False
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
RADIUS = 3
stage = 1

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():

    # Base constraints before calculations:
    E.add_constraint((~b1 & ~b2 & ~b3 & ~b4 & ~b5 & ~b6 & ~b7 & ~b8) >> ~fuel) # If fuel = 0, there is no fuel

    # Calculations:

    # Repeat for each grid, modified to fit each stage's needs:
    create_grid(3)
    
    # TODO: Add rocket to grid
    # TODO: Add checkpoint(s) to grid

    # End repeat

    while (stage == 1):
        pass
        # TODO: Add constraints to calculate the path, if nothing in the way should go straight right
        # TODO: Run fuel_calc() algorithm for every cell moved

    while (stage == 2):
        pass
        # TODO: Add constraints to calculate the path
        # TODO: Based on path, need to run fuel_calc() algorithm for every cell moved

    while (stage == 3):
        pass
        # TODO: Add constraints to calculate the path, if nothing in the way should go straight right
        # TODO: Add constraint that stops path from being calculated if next cell to the right is a planet
    

    #TODO Remove below code before submitting

    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    # constraint.add_exactly_one(E, a, b, c)

    return E

@proposition(E)
class Rocket: 
    def __init__(self, fuel, x, y):
        self.fuel = fuel
        self.x = x
        self.y = y

    def _prop_name(self):
        return f"A.{self.data}"

def fly(grid):
    assert fuel, "Rocket is out of fuel."
    #TODO something needs to put the rocket in the grid before it can fly
    fuel_calc()

@proposition(E)
class PlanetCell:
    def __init__(self, P):
        self.Pf = P #boolean for placement
    
    def _prop_name(self):
        return f"A.{self.data}"

"""
Creates grid
"""
def create_grid(radius):
    planet_coord = planet_position(radius)
    rows = radius + 2
    grid = []

    for i in range(rows):
        row = []
        for j in range(rows):
            row.append(PlanetCell(P=False)) #setting each to false in grid first
        grid.append(row)
    
    for (x,y) in planet_coord:
        if 0 <= x < rows and 0 <= y < rows:
            grid[x][y].Pf = True #set to true given coordinates
            #TODO: Have to make sure the coordinate generating function makes sense: 
            # For example, we cannot have a planet of radius 2 on the first row. 
    
    debug_print(grid) # DEBUG
    return grid

# DEBUG Print
def debug_print(grid):
    for row in grid:
        print([cell.Pf for cell in row])

def planet_position(radius):
    planet = []
    h=0
    for x in range(1, radius + 1):
        for y in range(1, radius +1):
            planet.append((x, y))
            h += 1
    print(planet)
    return planet

def enter_fuel():
    fuel_str = input("Please enter the rocket's starting fuel amount in binary, up to 8 digits.")
    assert len(fuel_str) < 9, "Your number is more than 8 digits"
    i = 0
    for num in fuel.str:
        if (num == 1):
            arr[i] = True
        elif (num == 0):
            arr[i] = False
        else:
            print("The character at index " +i+ " cannot be accepted.")
            return
        i += 1
    if (i<7):
        for j in range(i, 8): # If the binary number entered is less than 8 digits, set the remaining binary values to false.
            arr[j] = False

""" Subtract 1 to arr (value of fuel). If arr is filled with false (Fuel = 0) sets fuel to False and ends process, returning fuel.
"""
def fuel_calc():
    for i in arr: 
        if i:
            i = False
            break
        i = True
    if (not b1 and not b2 and not b3 and not b4 and not b5 and not b6 and not b7 and not b8):
        fuel = False
        #TODO end process here, return result fuel

# Included code as reference:

# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"

# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")

if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    # print("\nSatisfiable: %s" % T.satisfiable()) ***
    # print("# Solutions: %d" % count_solutions(T))

    # S = T.solve()

    # if(S):
    #     print("Solution: %s" % S)
    # else:
    #     print("No solution!")
    print()
