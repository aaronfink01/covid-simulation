Name: Simulation

Description: We simulate people inhabiting a town, tracking variables like their location, their hunger, and many more. The idea is to one day be able to use this life simulation to answer questions about society. Anything from examining methods for preventing the spread of an epidemic to testing economic models is a possible future use case. With a detailed-enough world, the possibilities are limitless.

Known Issues:
    * If two people in the same home want to eat food in the same minute, but the home doesn't have enough food, one of them simply won't be able to eat, depending on which is first in the simulation's people list. Instead they should split the remaining food.
        * Solving this will be tricky because it would require the two people to make their decision esentially simultaneously.
        * UPDATE: The infrastructure for this change is now in place with the Family class.
    * The amount of food in a home increases as soon as a person from the home leaves the supermarket. Instead, they should carry food home with them.

Future Updates:
    * People's work schedules should be made much more diverse. Instead of everyone working from nine to five with an hour-long lunchbreak, there should be people who work part time, people who work from home, people who work night shifts, and people who are unemployed.
    * The above update goes hand-in-hand with specifying people's professions to a much larger extent. Instead of having most people work unspecified jobs, everyone should have a specific role.
    * Additionally, the types of buildings in the city should be greatly expanded. Instead of including only homes, schools, supermarkets, and unspecified workplaces, there should be stores and hospitals and parks, and more.
    * Family dynamics are currently quite lacking, with everyone acting essentially on their own schedules. Instead, families should eat together, they should travel around the city together, and make plans together.
        * While none of these specific goals have yet been accomplished, the new Family class should allow for the implementation of these ideas.
    * There's no interconnection whatsoever between people who live in different homes. Perhaps there should be friendships, with friends visiting one another on the weekends.
    * The spread of disease is a mechanic that could become quite interesting. People would stay home when they're sick which would introduce many dynamics.