from scipy.stats import binom
from random import randint, choice, random
from math import floor

from building import *
from config import *

# The person class keeps track of everything relating to an individual, and contains the priorities and abilities of a person.
# This class seems massive, but I'm not yet sure how it can logically be broken up.
class Person:
    def __init__(self, home, school, workplace, age, gender, name):
        # These first variables remain constant throughout a run of the simulation.
        self.home = home
        self.school = school
        self.workplace = workplace
        self.age = age
        self.gender = gender
        self.name = name
        self.family = None # This is set immediately after the family is generated.
        # Travel-related variables
        self.location = self.home
        self.destination = None
        self.distance_to_destination = None
        self.travel_origin = None
        # Hunger-related variables
        self.hunger = 0
        self.currently_eating = False
        # Sleep-related variables
        self.asleep = True
        self.drowsiness = 0
        # The priorities list is set and cleared each minute
        # This is done to give the family time to impose extra priorities in the interim between setting and acting.
        self.priorities = None
    
    # Passive changes include growing hungrier and sleepier, as well as waking up in the morning.
    def change_passively(self, simulation):
        self.hunger += randint(0, 2)
        if self.asleep:
            # Currently everybody wakes up at exactly 6:00 am every morning. This should become more dynamic eventually.
            if simulation.hour == 6:
                self.asleep = False
                if DEBUG_MODE: print(self.name + " woke up at " + simulation.render_time() + ".")
        else:
            self.drowsiness += randint(0, 2)
    
    def determine_priorities(self, simulation):
        # Perhaps the person is sleeping
        if self.asleep:
            self.priorities = []
            self.previous_priorities = []
            return
        # Perhaps the person is currently in transit
        if self.destination != None:
            travel_priority = {'method': self.continue_travelling, 'weight': 5}
            self.priorities = [travel_priority]
            return
        # Perhaps the person is currently enjoying a meal
        if self.currently_eating:
            # If eating is no longer possible (the home is out of food, the lunch break is over), set the flag to false so they do not attempt to continue eating.
            # We additionally set the flag to false if hunger falls below 15 (a rather arbitrary threshold) to avoid a long duration of slowly eating before hunger falls to exactly 0.
            if self.eating_is_possible(simulation) and self.hunger > 15:
                eating_priority = {'method': self.consume_food, 'weight': 7}
                self.priorities = [eating_priority]
                return
            else:
                if DEBUG_MODE: print(self.name + " finished eating at " + simulation.render_time() + ".")
                self.currently_eating = False
        # Otherwise, examine all the options
        possible_priorities = [
            self.school_priority,
            self.work_priority,
            self.eating_priority,
            self.leaving_supermarket_priority,
            self.relaxing_priority,
            self.sleeping_priority
        ]
        # Each priority category (above) is a method which returns the specific related action that makes sense this minute (if any does).
        # Create a list of all of those specific actions, along with their priority weight.
        priorities = []
        for possible_priority in possible_priorities:
            priority = possible_priority(simulation)
            if priority:
                priorities.append(priority)
        self.priorities = priorities # Finally, we save that list to act on later.
    
    # The person has already determined their priorities and their weights. Now choose the highest-weighted priority.
    # If there's a tie, choose randomly.
    def select_highest_weighted_priority(self):
        highest_weight = 0
        highest_weighted_priorities = []
        for priority in self.priorities:
            if priority['weight'] > highest_weight:
                highest_weighted_priorities = [priority]
                highest_weight = priority['weight']
            elif priority['weight'] == highest_weight:
                highest_weighted_priorities.append(priority)
        return choice(highest_weighted_priorities)
    
    # Having earlier used determine_priorities to create a priority list and then given the Family object an opportunity to interject, the person now acts on their highest-weight priority.
    def act_on_priorities(self, simulation):
        if len(self.priorities) > 0:
            selected_priority = self.select_highest_weighted_priority()
            selected_priority['method'](simulation)
            self.priorities = None # Clear the priority list, so it can be freshly recreated next minute.
    
    # Start travelling somehwere.
    def begin_trip(self, destination):
        self.destination = destination
        self.distance_to_destination = self.location.distance_to(destination)
        self.origin = self.location
        self.location = None
    
    def leaving_supermarket_priority(self, simulation):
        if isinstance(self.location, Supermarket):
            return {'method': self.bring_home_food, 'weight': 5}
    
    # Calculate the chance that the person will reach a destination within a certain amount of time if they leave now.
    # Warning: The math is a bit complex.
    def on_time_arrival_probability(self, destination, minutes_remaining):
        distance = self.location.distance_to(destination)
        # The three parameters of binom.cdf are
        #       the minimum desired number of successful trials,
        #       the total number of trials,
        #       and the probability of a successful trial.
        # Since a successful trial (result of self.continue_travelling) decreases the remaining distance by 2, we need achieve only half as many successful trials as we have total trials (minutes remaining to reach the destination).
        # Since there is a 0.5 chance of decreasing distance by 2 in a minute (a successful trial), we provide 0.5 here for the probability parameter.
        # Find out more about binom.cdf here:
        #       https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.binom.html
        return 1 - binom.cdf(distance / 2, minutes_remaining, 0.5)
        
    # The school priority consists of two pieces: travelling to school in the morning, and doing schoolwork once at school.
    # It's worth noting that "doing schoolwork" actually means doing nothing. But doing nothing is important because it stops the person from doing anything else during school hours.
    def school_priority(self, simulation):
        if self.school != None: # Adults don't have schools assigned, for example. They need not search for a school-related action to perform.
            if simulation.day_of_the_week in range(1, 6):
                if simulation.hour < 9: # Before 9:00 am the person needs to go to school.
                    if self.location != self.school:
                        minutes_remaining = (9 - simulation.hour) * 60 - simulation.minute
                        if self.on_time_arrival_probability(self.school, minutes_remaining) <= 0.95:
                            return {'method': self.go_to_school, 'weight': 10}
                if simulation.hour < 16: # Before 4:00 pm, the person needs to do their schoolwork.
                    if self.location == self.school:
                        return {'method': self.do_nothing, 'weight': 5}
    
    # The work priority is essentially identical to the school priority above.
    # The only difference is that work runs until 5:00 pm while school only runs until 4:00.
    def work_priority(self, simulation):
        if self.workplace != None:
            if simulation.day_of_the_week in range(1, 6):
                if simulation.hour < 9:
                    if self.location != self.workplace:
                        minutes_remaining = (9 - simulation.hour) * 60 - simulation.minute
                        if self.on_time_arrival_probability(self.workplace, minutes_remaining) <= 0.95:
                            return {'method': self.go_to_workplace, 'weight': 10}
                if simulation.hour < 17:
                    if self.location == self.workplace:
                        return {'method': self.do_nothing, 'weight': 5}
    
    # Only sometimes is eating possible.
    def eating_is_possible(self, simulation):
        if self.hunger == 0:
            return False
        if self.location == self.home and self.home.food_quantity > 0:
            return True
        if self.location == self.school or self.location == self.workplace:
            if simulation.hour == 12:
                return True
        return False
    
    # Often people eat before they're fully hungry, because they know they'll otherwise be starving before their next opportunity. This method calculates the number of minutes before the next time they'll be able to eat that's at least an hour in the future.
            # An hour is a somewhat arbitrary length of time, but it serves to ensure that this later period of eating would meaningfully be a new meal.
    # I don't particularly like the implementation (or even the idea, really) of this function because it's so rigid. If anything about scheduling changes it will become entirely wrong quite quickly.
    def minutes_before_next_possible_meal(self, simulation):
        if simulation.day_of_the_week == 0 or simulation.day_of_the_week == 6:
            return 60 # On weekends they can eat as soon as the following hour is over
        if simulation.day_of_the_week in range(1, 6):
            # Let's imagine they'll be leaving for school or work at 8:00 am and that a meal takes half an hour. Then anytime before 6:30, an hour will leave them at 7:30 at the latest, which still gives them time to eat.
            if simulation.hour < 6 or (simulation.hour == 6 and simulation.minute < 30):
                return 60
            # Alternatively, any time before 11:00 am, the start of their lunch break (noon) will be more than an hour away. Thus they can eat immediately at 12:00.
            elif simulation.hour < 11:
                return (12 - simulation.hour) * 60 - simulation.minute
            # If the time's between 11:00 am and 11:30, they'll have to wait past the beginning of their lunch break, but they'll still have time for a full half-hour meal before 1:00.
            elif simulation.hour == 11 and simulation.minute < 30:
                return 60
            elif self.school != None:
                # The person will leave school at 4:00 pm (hour == 16) and get home around 5:00.
                if simulation.hour < 16:
                    return (17 - simulation.hour) * 60 - simulation.minute
                # If it's later than 4:00 pm, they'll be able to eat as soon as the hour is over.
                else:
                    return 60
            elif self.workplace != None:
                # The person will leave work at 5:00 pm (hour == 17) and get home around 6:00.
                if simulation.hour < 17:
                    return (18 - simulation.hour) * 60 - simulation.minute
                # If it's later than 5:00 pm, they'll be able to eat as soon as the hour is over.
                else:
                    return 60
            # If the person has no workplace or school, then they should be at home and quite able to eat.
            else:
                return 60
        if not SUPPRESS_ERRORS:
            print("Error: minutes_before_next_possible_meal has failed to return anything. Some edge case isn't being checked.")
            print("Context:")
            print("    simulation.day_of_the_week == " + str(simulation.day_of_the_week))
            print("    simulation.hour == " + str(simulation.hour))
            print("    simulation.minute == " + str(simulation.minute))
            print("    self.school is " + ("" if self.school else "not ") + "defined")
            print("    self.workplace is " + ("" if self.workplace else "not ") + "defined")
    
    
    def eating_priority(self, simulation):
        if self.eating_is_possible(simulation):
            hunger_threshold = HUNGER_EATING_THRESHOLD
            if self.hunger >= hunger_threshold:
                return {'method': self.consume_food, 'weight': 7}
            else:
                # If they'll reach 60 hunger units past the hunger threshold before their next opportunity to eat, they might as well eat now.
                        # This requirement of 60 hunger units past the threshold is so that if they'll be able to eat in an hour, they need not rush to eat now (if below the threshold now, of course).
                minutes_before_next_opportunity = self.minutes_before_next_possible_meal(simulation)
                if minutes_before_next_opportunity + self.hunger >= hunger_threshold + 60:
                    return {'method': self.consume_food, 'weight': 7}
    
    # People feel a constant (although slight) priority to relax. This brings them home after work, for example.
    def relaxing_priority(self, simulation):
        if self.location != self.home:
            return {'method': self.go_to_home, 'weight': 1}
        if self.location == self.home:
            return {'method': self.do_nothing, 'weight': 1}
    
    # People should go to sleep after accumulating a certain level of drowsiness.
    def sleeping_priority(self, simulation):
        if self.drowsiness >= DROWSINESS_SLEEPING_THRESHOLD:
            if self.location == self.home:
                return {'method': self.fall_asleep, 'weight': 3}
    
    # Doing nothing seems like a silly priority (especially because this method literally does nothing), but the priority system requires that a priority is chosen every minute, even when there's nothing to do.
    # Additionaly, this is used as a stand in for an action which needs to be done but in no way alters the simulation state, such as working while at work.
    def do_nothing(self, simulation):
        pass
    
    # A person needs to actively travel while on a trip.
    # Perhaps in the future continuing to travel could be a passive action of some type, so people could perform a limited range of other activities while on the move.
    def continue_travelling(self, simulation):
        if self.distance_to_destination != None:
            # We previously decreased the distance by a continuous (uniformly) random variable from 0 to 2, but this made calculating the likelihood of arriving in time more complex. 1 remains the average distance travelled in a minute, but the math is now simpler.
            self.distance_to_destination -= choice([0, 2])
            # Perhaps the person has just arrived at their destination.
            if self.distance_to_destination <= 0:
                if self.destination != None:
                    self.location = self.destination
                    if DEBUG_MODE: print(self.name + " arrived at " + simulation.render_time() + ".")
                else:
                    if not SUPPRESS_ERRORS: print("Error: attempting continue_travelling, but self.destination not defined.")
                self.destination = None
                self.distance_to_destination = None
        else:
            if not SUPPRESS_ERRORS: print("Error: attempting continue_travelling, but self.distance_to_destination not defined.")
    
    # Children go to school in the morning.
    def go_to_school(self, simulation):
        if DEBUG_MODE: print(self.name + " left for school at " + simulation.render_time() + ".")
        if self.school != None:
            if self.location != self.school:
                self.begin_trip(self.school)
            else:
                if not SUPPRESS_ERRORS: print("Error: attemtping go_to_school, but already at self.school.")
        else:
            if not SUPPRESS_ERRORS: print("Error: attempting go_to_school, but self.school not defined.")
    
    # Adults go to work in the morning.
    def go_to_workplace(self, simulation):
        if DEBUG_MODE: print(self.name + " left for work at " + simulation.render_time() + ".")
        if self.workplace != None:
            if self.location != self.workplace:
                self.begin_trip(self.workplace)
            else:
                if not SUPPRESS_ERRORS: print("Error: attempting go_to_workplace, but already at self.workplace.")
        else:
            if not SUPPRESS_ERRORS: print("Error: attempting go_to_workplace, but self.workplace not defined.")
    
    # Going shopping requires searching for the nearest supermarket and then travelling there.
    def go_to_supermarket(self, simulation):
        if DEBUG_MODE: print(self.name + " left for the supermarket at " + simulation.render_time() + ".")
        if not isinstance(self.location, Supermarket):
            if not self.location == None:
                # The person finds the nearest supermarket to travel to.
                # Perhaps this should be done once instead of every time the person want's to go shopping.
                        #This change would be possible because people's homes never change and supermarkets never close. If either of those could happen, the current system would make more sense.
                supermarkets = simulation.city.buildings['workplaces']['supermarkets']
                nearest_supermarket = self.location.find_nearest(supermarkets)
                self.begin_trip(nearest_supermarket)
            else:
                if not SUPPRESS_ERRORS:
                    print("Error: attempting to go_to_supermarket, but self.location is not defined.")
                    print("Context:")
                    print("    self.destination == " + str(self.destination))
        else:
            if not SUPPRESS_ERRORS: print("Error: attempting go_to_supermarket, but already at a supermarket.")
    
    # Once a person reaches the supermarket, it's time to come home.
    def bring_home_food(self, simulation):
        if DEBUG_MODE: print(self.name + " left the supermarket to return home at " + simulation.render_time() + ".")
        if isinstance(self.location, Supermarket):
            if self.home != None:
                self.home.food_quantity += FOOD_BUYING_QUANTITY # Currently food is added to their home as soon as a peron leaves the supermarket. This should be changed.
                self.begin_trip(self.home)
            else:
                if not SUPPRESS_ERRORS: print("Error: attempting bring_home_food, but self.home not defined.")
        else:
            if not SUPPRESS_ERRORS: print("Error: attempting bring_home_food, but not at a supermarket.")
    
    # The amount of food consumed in a minute is largely random, but limited by certain factors. Determine how much the person eats in a given minute.
    def minutely_consumption(self, simulation):
        # No one can eat more than 30 food units in a minute. This is rather arbitrary.
        # No one can eat enough food to have negative hunger. Thus food consumption is capped at current hunger.
        maximizing_factors = [30, self.hunger]
        # If the person is home (and thus limited by food supply), they cannot eat more food than is available.
            # If multiple people are at the same home and eating simulatneously, one of them could be denied food based on the order people are stored by the simulation. This is sort of a bug, but not an important one.
        if self.location == self.home:
            maximizing_factors.append(self.home.food_quantity)
        # It's worth notine that the maximum is set before the consumption is randomized. Another option would be to choose a random level of consumption (up to 30 unites) and then cap it, which would result in people eating more food when the maximizing factors are low.
        maximum_consumption = floor(min(maximizing_factors))
        consumption = randint(0, maximum_consumption)
        return consumption
    
    # Let's eat!
    def consume_food(self, simulation):
        if DEBUG_MODE and not self.currently_eating: print(self.name + " began eating at " + simulation.render_time() + ".")
        if self.eating_is_possible(simulation):
            consumption = self.minutely_consumption(simulation)
            self.hunger -= consumption
            if self.location == self.home:
                self.home.food_quantity -= consumption
            # Set the currently_eating flag to true so the person continues eating in the next minute.
            self.currently_eating = True
        else:
            self.currently_eating = False
            if DEBUG_MODE: print(self.name + " finished eating at " + simulation.render_time() + ".")
            if not SUPPRESS_ERRORS:
                print("Error-ish: attempting to consume_food, but self.eating_is_possible() is false.")
                print("Context:")
                print("    self.hunger == " + str(self.hunger))
                print("    self.location == " + str(self.location))
                print("    simulation.hour == " + str(simulation.hour))
                print("    self.home.food_quantity == " + str(self.home.food_quantity))
                print("    self.family.resident_already_shopping() == " + str(self.family.resident_already_shopping()))
    
    # People go home from work and school.
    # (Leaving supermarkets uses a different method).
    def go_to_home(self, simulation):
        if DEBUG_MODE: print(self.name + " headed home at " + simulation.render_time() + ".")
        if self.home != None:
            if self.location != self.home:
                self.begin_trip(self.home)
            else:
                if not SUPPRESS_ERRORS: print("Error: attempting go_to_home, but already at self.home.")
        else:
            if not SUPPRESS_ERRORS: print("Error: attempting go_to_home, but self.home not defined.")
    
    # When people get tired (and are home), they'll go to sleep.
    def fall_asleep(self, simulation):
        if DEBUG_MODE: print(self.name + " went to sleep at " + simulation.render_time() + ".")
        if self.location == self.home:
            self.asleep = True
            self.drowsiness = 0 # Perhaps drowsiness should dissipate slowly as the person sleeps. Under the current system, they could sleep for a minute and feel completely revitalized.
        else:
            if not SUPPRESS_ERRORS: print("Error-ish: attempting to fall_asleep, but not at self.home.")