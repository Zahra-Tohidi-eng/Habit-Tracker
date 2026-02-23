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
    print("4. Delete habit")
    print("5. Exit")


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

    # Display available habits
    for h in habits:
        print(f"{h.id}. {h.name}")

    hid = get_valid_int("Habit ID to complete: ")
    if hid is None:
        print("Invalid ID.")
        return

    # Find habit by ID
    habit = next((h for h in habits if h.id == hid), None)

    if habit:
        habit.complete()
        database.save_completion(db, habit.id, date.today())
        print(f"Habit '{habit.name}' marked as completed.")
    else:
        print("Habit ID not found.")


def delete_habit(db, habits):
    """
    Delete a habit and all its completions from the database.
    Also removes it from the in-memory list.
    """
    if not habits:
        print("No habits to delete.")
        return

    # Display available habits
    for h in habits:
        print(f"{h.id}. {h.name}")

    hid = get_valid_int("Enter Habit ID to delete: ")
    if hid is None:
        print("Invalid ID.")
        return

    habit = next((h for h in habits if h.id == hid), None)

    if not habit:
        print("Habit not found.")
        return

    # Delete related completions first (foreign key dependency)
    cur = db.cursor()
    cur.execute("DELETE FROM completions WHERE habit_id=?", (hid,))
    cur.execute("DELETE FROM habits WHERE id=?", (hid,))
    db.commit()

    # Remove habit from in-memory list
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
            delete_habit(db, habits)

        elif choice == "5":
            db.close()
            print("\n<<<< Keep up the good habits! See you soon! >>>>")
            break

        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    run()