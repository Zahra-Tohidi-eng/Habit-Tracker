from datetime import date


def list_habits(habits):
    """
    Returns a list of dictionaries with habit name and periodicity
    """
    if not habits:
        return []

    return [
        {h.name : h.periodicity}
        for h in habits
    ]


def longest_streak_for_habit(habit):
    """
    Calculates the longest streak for a single habit.
    Handles duplicate completion dates safely.
    """

    if not habit.completions:
        return 0

    # remove duplicates and sort
    sorted_dates = sorted(set(habit.completions))

    expected_gap = 1 if habit.periodicity == "daily" else 7

    max_streak = 1
    current_streak = 1

    for i in range(1, len(sorted_dates)):
        delta = (sorted_dates[i] - sorted_dates[i - 1]).days

        if delta == expected_gap:
            current_streak += 1
        else:
            current_streak = 1

        max_streak = max(max_streak, current_streak)

    return max_streak


def current_streak_for_habit(habit):
    """
    Calculates the current active streak (up to today).
    """

    if not habit.completions:
        return 0

    sorted_dates = sorted(set(habit.completions))
    expected_gap = 1 if habit.periodicity == "daily" else 7

    today = date.today()
    last_completion = sorted_dates[-1]

    # If last completion too old → no current streak
    if (today - last_completion).days > expected_gap:
        return 0

    streak = 1

    for i in range(len(sorted_dates) - 1, 0, -1):
        delta = (sorted_dates[i] - sorted_dates[i - 1]).days
        if delta == expected_gap:
            streak += 1
        else:
            break

    return streak


def habit_summary_with_current_streak(habits):
    """
    Returns a list of dictionaries:
    [
        {
            "name": habit_name,
            "periodicity": periodicity,
            "current_streak": streak
        },
    ]
    """

    summary = []

    for h in habits:
        summary.append({
            "name": h.name,
            "periodicity": h.periodicity,
            "current_streak": current_streak_for_habit(h)
        })

    return summary

def longest_streak_all_habits(habits):
    """
    Returns (list_of_habit_names, max_streak)
    """

    if not habits:
        return [], 0

    max_streak = 0
    habits_with_max = []

    for h in habits:
        streak = longest_streak_for_habit(h)

        if streak > max_streak:
            max_streak = streak
            habits_with_max = [h.name]

        elif streak == max_streak:
            habits_with_max.append(h.name)

    return habits_with_max, max_streak


def longest_streak_by_periodicity(habits):
    """
    Returns the habit with the longest streak
    for each periodicity.

    Output format:
    {
        "daily": (habit_name, streak),
        "weekly": (habit_name, streak)
    }
    """

    result = {}

    for h in habits:
        streak = longest_streak_for_habit(h)

        if h.periodicity not in result:
            result[h.periodicity] = (h.name, streak)

        else:
            current_best_name, current_best_streak = result[h.periodicity]

            if streak > current_best_streak:
                result[h.periodicity] = (h.name, streak)

    return result