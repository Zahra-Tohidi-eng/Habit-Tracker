from datetime import date

class Habit:
    """
    Represents a habit that can be tracked daily or weekly.

    Attributes:
        id (int): Unique identifier of the habit.
        name (str): Name of the habit.
        periodicity (str): Either "daily" or "weekly".
        start_date (date): The date when tracking starts.
        completions (List[date]): List of completion dates.
        max_streak (int): Longest streak achieved.
    """

    VALID_PERIODICITY = {"daily": 1, "weekly": 7}

    def __init__(self, habit_id:int, name:str, periodicity:str, start_date: date):
        """
        Initialize a new Habit instance.

        Raises:
            ValueError: If periodicity is not 'daily' or 'weekly'.
        """
        if periodicity not in self.VALID_PERIODICITY:
            raise ValueError("periodicity must be 'daily' or 'weekly'")

        self.id=habit_id
        self.name=name
        self.periodicity=periodicity #daily or weekly
        self.start_date=start_date
        self.completions=[] #list of date
        self.max_streak = 1



    def complete(self, completion_date=None):
        """
        Mark the habit as completed for a given date.
        If no date is provided, today's date is used.

        Raises:
            ValueError: If completion date is before start date.
        """
        if completion_date is None:
            completion_date=date.today()

        if completion_date < self.start_date:
            raise ValueError("completion date cannot be before than start date")

        if completion_date not in self.completions:
            self.completions.append(completion_date)

    def reset(self):
        """
        Reset all recorded completions.
        """
        self.completions=[]

    def __str__(self):
        """
        Return a readable string representation of the habit.
        """
        return f"{self.name} ({self.periodicity}): {len(self.completions)} completions"
