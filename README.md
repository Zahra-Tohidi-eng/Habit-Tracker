Habit Tracker with Streak Analysis

This project is a command-line Python application designed to track habits, record their completions, and analyze streaks over time. 
The application supports both daily and weekly habits and provides detailed analytics using a modular software architecture and 
persistent storage via SQLite.

FEATURES
• Create, edit, and delete habits
• Support for daily and weekly periodicity
• Record completion dates per habit
• Calculate longest streak per habit
• Calculate current active streak per habit
• Calculate longest streak overall
• Calculate longest streak per periodicity
• Persistent storage using SQLite
• Fully tested using pytest

PROJECT STRUCTURE
main.py – Command-line interface
habit.py – Habit domain model
database.py – SQLite persistence layer
analyze.py – Analytics and streak calculations
test.py – Unit tests
README.md
LICENSE
.gitignore

INSTALLATION
1. Clone the repository from GitHub.
2. (Optional) Create and activate a Python virtual environment.
3. Install dependencies using pip. Only pytest is required for testing.

USAGE
Habits can be created using the Habit class, completions can be recorded, and analytics functions can be applied to calculate streaks.
The analytics module operates independently of the database layer and works directly with Habit objects.

ANALYTICS MODULE
The analytics module provides functions to compute:
• Longest streak for a single habit
• Current streak up to today
• Longest streak across all habits
• Longest streak per periodicity (daily or weekly)

TESTING
The test suite is implemented using pytest and includes:
• Tests for habit creation, editing, and deletion
• Tests for three daily habits and two weekly habits
• Tests for longest streak calculations
• Tests for current streak calculations
• Tests for aggregate analytics per periodicity

DATABASE
The application uses SQLite with two tables:
• habits (id, name, periodicity, start_date)
• completions (habit_id, completion_date)

DEVELOPMENT ENVIRONMENT
The project was developed using PyCharm and Python 3.

GITHUB
The complete project source code is available on GitHub.

