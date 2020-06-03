from building import *
from config import *

class Family:
    def __init__(self, home, people):
        self.home = home
        self.people = people
    
    def update(self, simulation):
        for person in self.people:
            person.change_passively(simulation)
            person.determine_priorities(simulation)
        # In between people's determining their priorities and acting on them, the family has the chance to insert (or remove) priorities for family cohesion.
        self.insert_shopping_priority(simulation)
#        self.remove_eating_priority()
        # Now let the people execute their highest-weighted priority
        for person in self.people:
            person.act_on_priorities(simulation)
    
    # Check if anyone in the family is currently on a shipping trip
    # If this is the case, there's no need for another family member to head out.
    def resident_already_shopping(self):
        for person in self.people:
            # Currently at the supermarket
            if isinstance(person.location, Supermarket):
                return True
            # Travelling to the supermarket
            if isinstance(person.destination, Supermarket):
                return True
            # Returning home from the supermarket
            if isinstance(person.travel_origin, Supermarket):
                return True
        return False
    
    # When a priority needs to be inserted, it should be given to the least busy member of the family, sometimes the least busy member at a certain location.
    # Precisely, the least busy person is the person who's highest-weight priority has the lowest weight.
    def least_busy_person(self, requisite_location=None):
        least_busy_person = None
        least_busy_person_highest_priority_weight = float('inf')
        for person in self.people:
            if (not requisite_location) or (person.location == requisite_location):
                if not person.asleep:
                    highest_priority_weight = person.select_highest_weighted_priority()['weight']
                    if highest_priority_weight < least_busy_person_highest_priority_weight:
                        least_busy_person = person
                        least_busy_person_highest_priority_weight = highest_priority_weight
        return least_busy_person
    
    # When the family's home is running low on food, tell the least busy family member to go shopping.
    def insert_shopping_priority(self, simulation):
        if self.home.food_quantity < FOOD_SHOPPING_THRESHOLD:
            if not self.resident_already_shopping():
                least_busy_person = self.least_busy_person(requisite_location=self.home)
                shopping_priority = {'method': least_busy_person.go_to_supermarket, 'weight': 8}
                least_busy_person.priorities.append(shopping_priority)
    
#    # If by waiting some number of minutes the person can increase the number of family members with whom they can eat, they will.
#            # The complication is that no one is willing to wait too long (as defined by the time after which their hunger is greated than a configured threshold), and so if a mealmate will be lossed before one is gained, it isn't worth waiting.
#    # Note that I'm not at all sure that the logic hear makes great sense.
#    def remove_eating_priority(self):
#        for person in self.people:
#            eating_priority = {'method': person.consume_food, 'weight': 7}
#            if eating_priority in person.priorities and not person.currently_eating:
#                minutes_until_max_hunger = MAX_HUNGER_EATING_THRESHOLD - person.hunger
#                minutes_until_first_mealmate_lost = float("inf")
#                minutes_until_first_mealmate_gained = float("inf")
#                for possible_mealmate in self.people:
#                    if possible_mealmate != person:
#                        minutes_until_possible_mealmate_lost = MAX_HUNGER_EATING_THRESHOLD - possible_mealmate.hunger
#                        if 0 < minutes_until_possible_mealmate_lost:
#                            minutes_until_first_mealmate_lost = min(minutes_until_first_mealmate_lost, minutes_until_possible_mealmate_lost)
#                        minutes_until_possible_mealmate_gained = MIN_HUNGER_EATING_THRESHOLD - possible_mealmate.hunger
#                        if 0 < minutes_until_possible_mealmate_gained:
#                            minutes_until_first_mealmate_gained = min(minutes_until_first_mealmate_gained, minutes_until_possible_mealmate_gained)
#                if minutes_until_first_mealmate_gained < minutes_until_first_mealmate_lost and minutes_until_first_mealmate_gained < minutes_until_max_hunger:
#                    person.priorities.remove(eating_priority)
#                