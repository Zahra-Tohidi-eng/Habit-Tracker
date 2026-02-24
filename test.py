import os
import pytest
from datetime import date, timedelta

from habit import Habit
from database import get_db, create_tables, load_habits, save_habits
from analyze import (
    longest_streak_for_habit,
    longest_streak_all_habits,
    longest_streak_by_periodicity,
    habit_summary_with_current_streak,
    list_habits,
)


class TestHabitTracker:
    """
    Test suite for the Habit Tracker application.

    This class tests:
    - Habit creation and validation
    - Habit deletion
    - All analytics functions
    - Database persistence
    """

    def setup_method(self):
        """
        Runs before every test.

        - Creates a fresh test database
        - Seeds it with 3 daily and 2 weekly habits
        - Inserts realistic completion data
        """
        self.db_name = "test.db"

        # Ensure a clean test database
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

        self.db = get_db(self.db_name)
        create_tables(self.db)

        start_date = date(2026, 1, 1)

        # -------------------------
        # 3 DAILY HABITS
        # -------------------------

        self.skin_rutin = Habit(1, "Skin Rutin", "daily", start_date)
        self.mini_podcast = Habit(2, "Mini Podcast", "daily", start_date)
        self.quality_time = Habit(3, "Kids Quality Time", "daily", start_date)

        # Skin Rutin → 28 days
        for i in range(28):
            self.skin_rutin.complete(start_date + timedelta(days=i))

        # Mini Podcast → 14 days
        for i in range(14):
            self.mini_podcast.complete(start_date + timedelta(days=i))

        # Quality Time → 14 days
        for i in range(14):
            self.quality_time.complete(start_date + timedelta(days=i))

        # -------------------------
        # 2 WEEKLY HABITS
        # -------------------------

        self.workout = Habit(4, "Work Out", "weekly", start_date)
        self.entertainment = Habit(5, "Entertainment", "weekly", start_date)

        # Work Out → 4 weeks
        for i in range(4):
            self.workout.complete(start_date + timedelta(days=i * 7))

        # Entertainment → 2 weeks
        self.entertainment.complete(start_date)
        self.entertainment.complete(start_date + timedelta(days=7))

        # Persist all habits and completions into test database
        save_habits(
            self.db,
            [
                self.skin_rutin,
                self.mini_podcast,
                self.quality_time,
                self.workout,
                self.entertainment,
            ],
        )

    def teardown_method(self):
        """
        Runs after every test.

        - Closes database connection
        - Deletes test database file
        - Ensures complete isolation between tests
        """
        self.db.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    # -------------------------------------------------
    # HABIT CREATION TESTS
    # -------------------------------------------------

    def test_habit_creation(self):
        """
        Tests whether all seeded habits are correctly
        stored and loaded from the database.
        """
        habits = load_habits(self.db)

        # Verify total number of habits
        assert len(habits) == 5

        names = [h.name for h in habits]

        # Verify all expected habits exist
        assert "Skin Rutin" in names
        assert "Mini Podcast" in names
        assert "Kids Quality Time" in names
        assert "Work Out" in names
        assert "Entertainment" in names

    def test_invalid_periodicity(self):
        """
        Ensures that invalid periodicity values
        raise a ValueError.
        """

        with pytest.raises(ValueError):
            Habit(99, "Invalid", "monthly", date(2026, 1, 1))

    # -------------------------------------------------
    # HABIT DELETION TEST
    # -------------------------------------------------

    def test_delete_habit(self):
        """
        Tests whether a habit and its completions
        can be removed from the database correctly.
        """
        habits = load_habits(self.db)
        habit_to_delete = habits[0]

        cur = self.db.cursor()
        cur.execute("DELETE FROM completions WHERE habit_id=?", (habit_to_delete.id,))
        cur.execute("DELETE FROM habits WHERE id=?", (habit_to_delete.id,))
        self.db.commit()

        updated = load_habits(self.db)

        assert habit_to_delete.name not in [h.name for h in updated]
        assert len(updated) == 4

    def test_edit_habit(self):
        habits = load_habits(self.db)

        habit = habits[0]
        original_name = habit.name

        from database import update_habit

        update_habit(self.db, habit.id, new_name="Updated Habit")

        updated_habits = load_habits(self.db)
        updated_names = [h.name for h in updated_habits]

        assert "Updated Habit" in updated_names
        assert original_name not in updated_names

    # -------------------------------------------------
    # ANALYTICS TESTS
    # -------------------------------------------------

    def test_longest_streak_per_habit(self):
        habits = load_habits(self.db)
        habit_dict = {h.name: h for h in habits}

        assert longest_streak_for_habit(habit_dict["Skin Rutin"]) == 28
        assert longest_streak_for_habit(habit_dict["Mini Podcast"]) == 14
        assert longest_streak_for_habit(habit_dict["Kids Quality Time"]) == 14
        assert longest_streak_for_habit(habit_dict["Work Out"]) == 4
        assert longest_streak_for_habit(habit_dict["Entertainment"]) == 2

    def test_longest_streak_overall(self):
        habits = load_habits(self.db)

        names, max_streak = longest_streak_all_habits(habits)

        assert max_streak == 28
        assert names == ["Skin Rutin"]

    def test_longest_streak_by_periodicity(self):
        habits = load_habits(self.db)

        result = longest_streak_by_periodicity(habits)

        daily_name, daily_streak = result["daily"]
        weekly_name, weekly_streak = result["weekly"]

        assert daily_name == "Skin Rutin"
        assert daily_streak == 28

        assert weekly_name == "Work Out"
        assert weekly_streak == 4

    def test_habit_summary(self):
        habits = load_habits(self.db)

        summary = habit_summary_with_current_streak(habits)

        assert isinstance(summary, list)
        assert len(summary) == 5
        assert "name" in summary[0]
        assert "periodicity" in summary[0]
        assert "current_streak" in summary[0]

    def test_list_habits(self):
        habits = load_habits(self.db)

        result = list_habits(habits)

        assert isinstance(result, list)
        assert len(result) == 5
        assert isinstance(result[0], dict)