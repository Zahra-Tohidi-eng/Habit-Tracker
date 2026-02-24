from datetime import date
from habit import Habit
import analyze
import database


def print_menu():
    """
    Display the main menu options to the user.
    """
    print("\n===== HABIT TRACKER =====")
    print("1. Add habit")
    print("2. Complete habit")
    print("3. View analytics")
    print("4. Edit Habit")
    print("5. Delete habit")
    print("6. Exit")


def get_valid_int(prompt):
    """
    Safely convert user input to an integer.
    Returns None if conversion fails.
    """
    try:
        return int(input(prompt))
    except ValueError:
        return None


def add_habit(db, habits):
    """
    Add a new habit to the database and refresh the in-memory habit list.
    Prevents duplicate habit names (case-insensitive).
    """
    name = input("Habit name: ").strip()

    # Check for duplicate habit names
    if any(h.name.lower() == name.lower() for h in habits):
        print("Habit already exists.")
        return

    # Validate periodicity input
    while True:
        periodicity = input("daily / weekly: ").strip().lower()
        if periodicity in Habit.VALID_PERIODICITY:
            break
        print("Invalid input! Type 'daily' or 'weekly'.")

    # Create habit object (ID assigned by database)
    habit = Habit(None, name, periodicity, date.today())

    # Save habit to database
    database.save_habit(db, habit)

    # Reload habits to get correct ID from database
    habits.clear()
    habits.extend(database.load_habits(db))

    print(f"Habit '{name}' added successfully.")


def complete_habit(db, habits):
    """
    Mark a habit as completed for today and store the completion in the database.
    """
    if not habits:
        print("No habits available.")
        return

    # Display habits with clean numbering (
        # We use clean numbering (1..n) instead of database IDs.
        # Database IDs are not renumbered after deletions (AUTOINCREMENT behavior),
        # so using enumerate ensures no gaps are shown to the user.)
    for index, h in enumerate(habits, start=1):
        print(f"{index}. {h.name}")

    choice = get_valid_int("Select habit: ")

    if choice is None or choice < 1 or choice > len(habits):
        print("Invalid selection.")
        return

    habit = habits[choice - 1]

    if habit:
        habit.complete()
        database.save_completion(db, habit.id, date.today())
        print(f"Habit '{habit.name}' marked as completed.")
    else:
        print("Habit ID not found.")


def edit_habit(db, habits):
    """
    Edit an existing habit's name and/or periodicity.
    """

    if not habits:
        print("No habits available.")
        return

    # Show habits
    # We use clean numbering (1..n) instead of database IDs.
    # Database IDs are not renumbered after deletions (AUTOINCREMENT behavior),
    # so using enumerate ensures no gaps are shown to the user.
    for index, h in enumerate(habits, start=1):
        print(f"{index}. {h.name} ({h.periodicity})")

    choice = get_valid_int("Select habit to edit: ")

    if choice is None or choice < 1 or choice > len(habits):
        print("Invalid selection.")
        return

    habit = habits[choice - 1]

    if not habit:
        print("Habit not found.")
        return

    print("Leave field empty to keep current value.")

    new_name = input(f"New name (current: {habit.name}): ").strip()
    new_periodicity = input(
        f"New periodicity (daily/weekly) (current: {habit.periodicity}): "
    ).strip().lower()

    # Handle empty input
    if new_name == "":
        new_name = None

    if new_periodicity == "":
        new_periodicity = None
    elif new_periodicity not in Habit.VALID_PERIODICITY:
        print("Invalid periodicity.")
        return

    # Check duplicate name
    if new_name and any(
        h.name.lower() == new_name.lower() and h.id != habit.id
        for h in habits
    ):
        print("Another habit with this name already exists.")
        return

    # Update database
    database.update_habit(
        db,
        habit.id,
        new_name=new_name,
        new_periodicity=new_periodicity,
    )

    # Update in-memory object
    if new_name:
        habit.name = new_name
    if new_periodicity:
        habit.periodicity = new_periodicity

    print("Habit edited successfully.")

def delete_habit_cli(db, habits):
    """
    Delete a habit using the database layer.
    Also removes it from the in-memory list.
    """

    if not habits:
        print("No habits to delete.")
        return

    # Display habits with clean numbering
    #          We use clean numbering (1..n) instead of database IDs.
    #          Database IDs are not renumbered after deletions (AUTOINCREMENT behavior),
    #          so using enumerate ensures no gaps are shown to the user.
    for index, h in enumerate(habits, start=1):
        print(f"{index}. {h.name}")

    choice = get_valid_int("Select habit to delete: ")

    if choice is None or choice < 1 or choice > len(habits):
        print("Invalid selection.")
        return

    habit = habits[choice - 1]

    if not habit:
        print("Habit not found.")
        return

    # Call database layer
    database.delete_habit(db, habit.id)

    # Remove from memory
    habits.remove(habit)

    print(f"Habit '{habit.name}' deleted successfully.")


def show_analytics(habits):
    """
    Display analytics for all habits including:
    - Current streak
    - Longest streak per habit
    - Longest streak by periodicity
    - Longest streak overall
    """

    if not habits:
        print("No habits available.")
        return

    print("\n--- Habit Overview ---")

    summary = analyze.habit_summary_with_current_streak(habits)

    # Print summary table
    print(f"{'Name':15} {'Periodicity':12} {'Current Streak'}")
    print("-" * 40)

    for item in summary:
        print(f"{item['name']:15} {item['periodicity']:12} {item['current_streak']}")

    print("\n--- Longest Streak Per Habit ---")
    for h in habits:
        streak = analyze.longest_streak_for_habit(h)
        print(f"{h.name}: {streak}")

    print("\n--- Longest Streak By Periodicity ---")
    result = analyze.longest_streak_by_periodicity(habits)

    # Handle tie situations (multiple habits with same streak)
    for period, value in result.items():
        if isinstance(value, list):  # tie-handling version
            for name, streak in value:
                print(f"{period}: {name} ({streak})")
        else:
            name, streak = value
            print(f"{period}: {name} ({streak})")

    print("\n--- Longest Streak Overall ---")
    names, streak = analyze.longest_streak_all_habits(habits)
    print(f"{names} → {streak}")


def run():
    db = database.get_db()
    database.create_tables(db)

    # Load existing habits from database
    habits = database.load_habits(db)

    while True:
        print_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            add_habit(db, habits)

        elif choice == "2":
            complete_habit(db, habits)

        elif choice == "3":
            show_analytics(habits)

        elif choice == "4":
            edit_habit(db, habits)

        elif choice == "5":
            delete_habit_cli(db, habits)

        elif choice == "6":
            db.close()
            print("\n<<<< Keep up the good habits! See you soon! >>>>")
            break

        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    run()
