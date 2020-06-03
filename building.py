# There are a number of types of buildings. They all inherit from this general Building class.
class Building:
    def __init__(self, location):
        # Unlike a person's location (which is a building), a building's location is a point (x, y) within the unit square.
        # (Read more above generate_city() in generate.py.)
        self.location = location
    
    # A building calculates its distance to another building using the pythagorean distance formula.
    def distance_to(self, other_building):
        horizontal_distance = abs(other_building.location[0] - self.location[0])
        vertical_distance = abs(other_building.location[1] - self.location[1])
        distance = (horizontal_distance ** 2 + vertical_distance ** 2) ** 0.5
         # The scale_factor is chosen arbitrarily to make distances feel reasonable, given that the unit distance takes an average of one minute to travel.
        # Also, the average distance (before scaling) between two buildings should be approximately 0.52, as determined experimentally.
        scale_factor = 60
        return distance * scale_factor
    
    # Find the nearest building in a list of buildings.
    # This is currently only used for finding the nearest supermarket, but it will hopefully be expanded soon.
    def find_nearest(self, other_buildings):
        nearest_building = other_buildings[0]
        nearest_distance = self.distance_to(other_buildings[0])
        for building in other_buildings[1:]:
            distance = self.distance_to(building)
            if distance < nearest_distance:
                nearest_building = building
                nearest_distance = distance
        return nearest_building

class Home(Building):
    def __init__(self, location, food_quantity):
        Building.__init__(self, location)
        self.food_quantity = food_quantity

class School(Building):
    def __init__(self, location):
        self.location = location

# The only specified workplace is a supermarket. Anyone who does not work at a supermarket currently works at a GenericWorkplace.
class GenericWorkplace(Building):
    def __init__(self, location):
        Building.__init__(self, location)

class Supermarket(Building):
    def __init__(self, location):
        Building.__init__(self, location)

# The simulation currently only supports a single city, but it would be great to have multiple cities interact in the future.
class City:
    def __init__(self, buildings):
        self.buildings = buildings