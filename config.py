# When debug mode is enabled, people print out the action they take each minute.
# Additionally, generate_family only creates single-person families.
DEBUG_MODE = True
RANDOM_SEED = None
SUPPRESS_ERRORS = False


HOME_COUNT = 100 # The number of homes
SCHOOL_COUNT = 6 # The number of schools, split evenly between elementary, middle, and high
WORKPLACE_COUNT = 15 # The number of total workplaces, including both generic and specific
SUPERMARKET_COUNT = 10 # The number of supermarkets


INITIAL_DAY = 0 # Starting day of the week
INITIAL_HOUR = 0 # Starting hour
INITIAL_MINUTE = 0 # Starting minute


INITIAL_FOOD_QUANTITY = 10000 # How much food should each home start with? This initial amount of food is quite arbitrary. In the future it should probably be dependent on the number of people living in the home.
FOOD_SHOPPING_THRESHOLD = 1800 # How low should a home's food quantity go before someone goes shopping? A person should go shopping when their home has less than enough food for 5 meals. This threshold is rather arbitrary, and additionally should be based on the number of people in the household eventually.
HUNGER_EATING_THRESHOLD = 360 # How hungry must someone be to eat spontaneously? The hunger level at which eating feels right is the average amount of hunger gained over six hours, although this is somewhat arbitrary.
MIN_HUNGER_EATING_THRESHOLD = 300 # How hungry must someone be to be willing to eat if it means sharing a meal with others?
MAX_HUNGER_EATING_THRESHOLD = 420 # How hungry must someone be before they refuse to wait for others to eat?
FOOD_BUYING_QUANTITY = 5000 # How much food should someone buy at once?


DROWSINESS_SLEEPING_THRESHOLD = 960 # How tired must someone be to fall asleep? This takes an average of sixteen hours to accumulate.


# The lists of names (male and female) come from a Carnegie Mellon database: https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/nlp/corpora/names/
MALE_NAMES = [name.strip() for name in open("names/male.txt", "r").readlines()]
FEMALE_NAMES = [name.strip() for name in open("names/female.txt", "r").readlines()]