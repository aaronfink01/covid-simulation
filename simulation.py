# The Simulation class keeps track of the current state of the simulation.
# There should only ever be one of these, although more than one wouldn't likely be a problem.
class Simulation:
    def __init__(self, day_of_the_week, hour, minute, city, families):
        self.day_of_the_week = day_of_the_week
        self.hour = hour
        self.minute = minute
        self.city = city
        self.families = families
    
    # After each simulation step, the time is advanced by one minute.
    def advance_time(self):
        self.minute += 1
        if self.minute == 60:
            self.minute = 0
            self.hour += 1
            if self.hour == 24:
                self.hour = 0
                self.day_of_the_week = (self.day_of_the_week + 1) % 7
    
    # Display the time of day in a human-readable form
    def render_time(self):
        if self.hour == 0 or self.hour == 12:
            hour = "12"
        else:
            hour = str(self.hour % 12)
        if self.minute < 10:
            minute = "0" + str(self.minute)
        else:
            minute = str(self.minute)
        if self.hour < 12:
            period = "am"
        else:
            period = "pm"
        full_time = hour + ":" + minute + " " + period
        return full_time
    
    def render_day(self):
        day_dictionary = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
        return day_dictionary[self.day_of_the_week]