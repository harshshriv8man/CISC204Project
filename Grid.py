
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

# Call your variables whatever you want
a = BasicPropositions("a")
b = BasicPropositions("b")   
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    #TODO Add while loop for each stage that goes from the start to the finish, whether it succeeds or not

    return E




class Rocket: 
    def __init__(self,fuel):
        self.fuel = fuel

R = Rocket(1800) #random fuel number

@proposition(E)
class PlanetCell:
    def __init__(self, P):
        self.Pf = P #boolean for placement

"""
Creates grid
"""
def create_grid(radius, planet_coord):
    rows = radius + 2
    grid = []

    for i in range(rows):
        row = []
        for j in range(rows):
            row.append(PlanetCell(P=False)) #setting each to false in grid first
        grid.append(row)
    
    for (x,y) in planet_coord:
        if 0 <= x< rows and 0 <= y < rows:
            grid[x][y].P = True #set to true given coordinates
            
            #TODO: Have to make sure the coordinate generating function makes sense: 
            # For example, we cannot have a planet of radius 2 on the first row. 
    
    return grid


b1 = True
b2 = True
b3 = True
b4 = False
b5 = False
b6 = False
b7 = False
b8 = False
fuel = True

arr = [b1, b2, b3, b4, b5, b6, b7, b8]

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



if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
