from datetime import datetime, timedelta, time


class Schedule:
    def __init__(self, start_time, end_time, interval_minutes=15):
        # If the input times are strings (e.g., '08:00'), convert them to datetime objects
        if isinstance(start_time, str) and isinstance(end_time, str):
            self.start_time = datetime.strptime(start_time, '%H:%M')
            self.end_time = datetime.strptime(end_time, '%H:%M')
        elif isinstance(start_time, time) and isinstance(end_time, time):
            # If the input times are datetime.time objects, combine with today's date
            self.start_time = datetime.combine(datetime.today(), start_time)
            self.end_time = datetime.combine(datetime.today(), end_time)
        else:
            raise ValueError("start_time and end_time must be either strings or datetime.time objects")

        self.interval_minutes = interval_minutes
        self.schedule = self.generate_schedule()
        self.blocked_times = []

    # Function to generate the full schedule
    def generate_schedule(self):
        current_time = self.start_time
        schedule = []

        while current_time < self.end_time:
            end_slot = current_time + timedelta(minutes=self.interval_minutes)
            # Avoid appending a slot with an end time that is equal to the final time
            if end_slot <= self.end_time:
                schedule.append((current_time.time(), end_slot.time()))  # Store as time objects
            current_time = end_slot

        return schedule

    # Function to add blocked time slots, accepting datetime.time objects
    def add_blocked_time(self, blocked_start, blocked_end):
        if isinstance(blocked_start, time) and isinstance(blocked_end, time):
            blocked_start = datetime.combine(datetime.today(), blocked_start)
            blocked_end = datetime.combine(datetime.today(), blocked_end)
            self.blocked_times.append((blocked_start.time(), blocked_end.time()))
        else:
            raise ValueError("blocked_start and blocked_end must be datetime.time objects")

    # Function to mark the blocked slots
    def mark_blocked_slots(self):
        blocked_slots = []
        for blocked_start, blocked_end in self.blocked_times:
            blocked_slots.extend(
                [(start, end) for start, end in self.schedule if start >= blocked_start and end <= blocked_end]
            )
        return blocked_slots

    # Function to find free slots
    def find_free_slots(self):
        blocked_slots = self.mark_blocked_slots()
        free_slots = []
        blocked_times = set(blocked_slots)  # Convert blocked slots to a set for fast lookup

        for time_slot in self.schedule:
            if time_slot not in blocked_times:
                free_slots.append(time_slot)

        return free_slots

    def display_free_slots(self):
        free_slots = self.find_free_slots()

        if free_slots:  # Check if there are any free slots
            result = []
            for start, end in free_slots:
                result.append(f"Free slot: {start} - {end}")
            return "\n".join(result)  # Return the formatted string instead of printing
        else:
            return "No free slots available."

    def total_free_time(self):
        free_slots = self.find_free_slots()
        total_minutes = 0

        for start, end in free_slots:
            # Calculate the difference in minutes between start and end times
            duration = (datetime.combine(datetime.today(), end) - datetime.combine(datetime.today(),
                                                                                   start)).seconds / 60
            total_minutes += duration

        # Return the total free time in minutes
        return total_minutes
