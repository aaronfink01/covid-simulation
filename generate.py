from enum import Enum
from random import random, choice, randint
from math import floor, ceil

from building import *
from person import Person
from family import Family
from config import *

# This might not be fully necessary, but it's used in generate_family.
class FamilyType(Enum):
    married_couple = 1
    single_adult = 2
    roommates = 3

# Gender actually has no effect whatsoever on the simulation (outside of name assignment). Perhaps it will at some point, but that day seems far off.
class Gender(Enum):
    male = 1
    female = 2

# The simulation currently only contains a single city. This is definitely something I'd be interested in changing in the future, but for now this function initializes every building involved in the simulation.
#It's worth making particular note of how locations work, because the system is rather odd. Instead of worrying about realistic features of a town or city grid (roads, subway lines, etc.), we simply assign each building a random position within a unit square. Distances are calculated geometrically.
#While simple, this model should in theory create proximity-based community. For example, if two people's children attend the same school, they're more likely to shop at the same supermarket.
def generate_city(home_count, school_count, generic_workplace_count, supermarket_count):
    homes = []
    for home_index in range(home_count):
        location = (random(), random())
        initial_food_quantity = INITIAL_FOOD_QUANTITY
        homes.append(Home(location, initial_food_quantity))
    elementary_schools = []
    middle_schools = []
    high_schools = []
    for school_index in range(school_count):
        location = (random(), random())
        # The school_count parameter specifies the total number of schools. A third are elementary, a third middle, and a third high.
        if school_index < school_count / 3:
            elementary_schools.append(School(location))
        elif school_index < school_count * 2 / 3:
            middle_schools.append(School(location))
        else:
            high_schools.append(School(location))
    workplaces = {'generic': [], 'supermarkets': []}
    for supermarket_index in range(supermarket_count):
        location = (random(), random())
        workplaces['supermarkets'].append(Supermarket(location))
    for generic_workplace_index in range(generic_workplace_count):
        workplaces['generic'].append(GenericWorkplace(location))
    buildings = {'homes': homes, 'schools': {'elementary': elementary_schools, 'middle': middle_schools, 'high': high_schools}, 'workplaces': workplaces}
    return City(buildings)

# Choose a random name based on a person's gender
def choose_name(gender):
    if gender == Gender.male:
        return choice(MALE_NAMES)
    if gender == Gender.female:
        return choice(FEMALE_NAMES)
    print("Error: attempting choose_name but gender not male or female.")

# Some of the generation processes are common to all (or many) people. We automate those here so they don't have to be repeated in generate_family.
def create_person(home, age, gender, schools, city):
    school = None
    # If the person is a child, choose a school based on their age group.
    if age > 4 and age < 11:
        schools = schools['elementary']
    if age > 10 and age < 14:
        schools = schools['middle']
    if age > 13 and age < 18:
        school = schools['high']
    # If the person is of working have, assign them a random workplace.
    workplace = None
    if age > 17 and age < 67:
        all_workplaces = sum(city.buildings['workplaces'].values(), [])
        workplace = choice(all_workplaces)
    if not gender:
        gender = choice([Gender.male, Gender.female])
    if gender == Gender.male:
        name = choice(MALE_NAMES)
    if gender == Gender.female:
        name = choice(FEMALE_NAMES)
    return Person(home, school, workplace, age, gender, name)

# Family generation is remarkably complex. Hopefully it can be simplified, or at least separated into multiple functions.
def generate_family(home, city):
    # Start by choosing one of three base family types.
    # These options should be expanded in the future.
    family_type = choice([FamilyType.married_couple, FamilyType.single_adult, FamilyType.roommates])
    # A married_couple family consists of two adults (of opposite genders) with anywhere from 0 to 4 children.
    if family_type == FamilyType.married_couple:
        # To determine the two adults' ages, we pick an average and a spread. This lets us ensure that they are within 15 years of age.
        mean_age = randint(25, 85)
        maximum_age_spread = ceil(min(15, (mean_age - 25) * 2))
        age_spread = randint(0, maximum_age_spread)
        younger_age = floor(mean_age - age_spread / 2)
        older_age = ceil(mean_age + age_spread / 2)
        # We then randomly decide if the younger adult is the man or the woman.
        younger_gender = choice([Gender.male, Gender.female])
        if younger_gender == Gender.male:
            older_gender = Gender.female
        if younger_gender == Gender.female:
            older_gender = Gender.male
        
        all_workplaces = sum(city.buildings['workplaces'].values(), [])
        if younger_age < 67:
            younger_workplace = choice(all_workplaces)
        else:
            younger_workplace = None
        if older_age < 67:
            older_workplace = choice(all_workplaces)
        else:
            older_workplace = None
        younger_person = create_person(home, younger_age, younger_gender, None, city)
        older_person = create_person(home, older_age, older_gender, None, city)
        people = [younger_person, older_person]
        child_count = randint(0, 4)
        elementary_school = home.find_nearest(city.buildings['schools']['elementary'])
        middle_school = home.find_nearest(city.buildings['schools']['middle'])
        high_school = home.find_nearest(city.buildings['schools']['high'])
        schools = {'elementary': elementary_school, 'middle': middle_school, 'high': high_school}
        # Now we randomize each child and add it to the family.
        for child_index in range(child_count):
            minimum_age = floor(max(0, (mean_age - age_spread / 2) - 45))
            maximum_age = ceil(min(17, (mean_age - age_spread / 2) - 25))
            # If there aren't any valid ages for children (given their parents' ages), there will be no choldren.
            if minimum_age > maximum_age:
                break
            age = randint(minimum_age, maximum_age)
            child = create_person(home, age, None, schools, city)
            people.append(child)
        return Family(home, people)
    # A single_adult family consists of a single adult with anywhere from 0 to 4 children.
    # Other than the lack of second adult, this generation process is identical to that of the above family type.
    if family_type == FamilyType.single_adult:
        adult_age = randint(25, 85)
        adult = create_person(home, adult_age, None, None, city)
        people = [adult]
        child_count = randint(0, 4)
        elementary_school = home.find_nearest(city.buildings['schools']['elementary'])
        middle_school = home.find_nearest(city.buildings['schools']['middle'])
        high_school = home.find_nearest(city.buildings['schools']['high'])
        schools = {'elementary': elementary_school, 'middle': middle_school, 'high': high_school}
        for child_index in range(child_count):
            maximum_age = min(17, adult_age - 25)
            age = randint(0, maximum_age)
            child = create_person(home, age, None, schools, city)
            people.append(child)
        return Family(home, people)
    # A roommates family (not exactly a family, to be fair) consists of anywhere from 1 to 4 adults aged 18 to 30. At the moment, they're all of the same gender, but this could be changed.
    if family_type == FamilyType.roommates:
        roommate_count = randint(1, 4)
        people = []
        # Similarly to the married_couple family above, we first choose a mean age for the roommates in order to ensure their ages are similar. (Although here it will not quite be the true mean, just the center of the random range.)
        mean_age = randint(18, 30)
        gender = choice([Gender.male, Gender.female])
        for roommate_index in range(roommate_count):
            minimum_age = max(18, mean_age - 3)
            age = randint(minimum_age, mean_age + 3)
            person = create_person(home, age, gender, None, city)
            people.append(person)
        return Family(home, people)

# A city needs a population.
def generate_families(city):
    families = []
    for home in city.buildings['homes']:
        family = generate_family(home, city)
        families.append(family)
        # Tell each person which family they're a part of. This can't happen in generate_family because the family doesn't yet exist.
        for person in family.people:
            person.family = family
    return families