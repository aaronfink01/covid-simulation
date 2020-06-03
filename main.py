from random import seed

import generate
from simulation import Simulation
from config import *

if RANDOM_SEED:
    seed(RANDOM_SEED)

# Create the simulation
city = generate.generate_city(HOME_COUNT, SCHOOL_COUNT, WORKPLACE_COUNT, SUPERMARKET_COUNT)
families = generate.generate_families(city)
simulation = Simulation(INITIAL_DAY, INITIAL_HOUR, INITIAL_MINUTE, city, families)

# The basic simulation loop: let the people do something, advance time by a minute, repeat.
print("healthy,infected,recovered,dead")
while True:
    if simulation.hour == 0 and simulation.minute == 0:
        print("\033[1m" + simulation.render_day() + "\033[0m")
    
    for family in simulation.families:
        family.update(simulation)
    simulation.advance_time()
    
    # Eventually end the simulation
    # Maybe these should become config variables
    if simulation.minute == 0 and simulation.hour == 0 and simulation.day_of_the_week == 6:
        break