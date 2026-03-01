"""
Track and manage weekly budgets.

This module provides a command-line application for tracking and managing weekly budgets.
It allows users to monitor spending against a fixed weekly budget and track additional expenses
that don't count toward the main budget (like bills or irregular expenses).

Features:
- Track main costs that count against weekly budget (default £200)
- Track other costs separately (bills, etc.) that don't affect weekly budget
- View remaining budget for the current week
- Show total spending by day and week
- Interactive terminal UI using simple_term_menu

Usage:
    $ python budget_per_week.py

Data Storage:
    - Main costs are stored in budget_per_week.json
    - Other costs are stored in budget_per_week_other_costs.json

Dependencies:
    - simple_term_menu: For terminal-based menu interface
    - prompt_toolkit: For enhanced input prompts
"""

from datetime import datetime
import json
import tempfile
import os
from simple_term_menu import TerminalMenu
from prompt_toolkit import prompt

BUDGET_PER_WEEK = 200


class BudgetPerWeek:
    """
    Manage and track weekly budget spending.

    This class provides methods to track spending against a weekly budget, calculate remaining
    budget, and manage separate tracking for different types of costs. It offers functionality
    to add new costs, view totals by day or week, and run an interactive terminal interface
    for budget management.

    Attributes:
        current_week (str): The ISO calendar week number for the current date.
        current_day (str): The name of the current day (e.g., "Monday").
        current_month (str): The name of the current month (e.g., "February").
        budget_per_week (float): The weekly budget amount (default: 200).
        file_path (str): Path to the JSON file storing main costs.
        file_path_other_costs (str): Path to the JSON file storing other costs.
        records (dict): Loaded main cost records.
        records_other (dict): Loaded other cost records.
    """

    def __init__(self):
        """
        Initialize a new BudgetPerWeek instance.

        Sets up the current date information, loads the default weekly budget amount,
        defines file paths for storing cost data, and loads existing records from
        the JSON files if they exist.

        No parameters are required as all values are determined at runtime or
        set to default values.
        """
        self.current_week = str(datetime.now().isocalendar().week)
        self.current_day = datetime.now().strftime("%A").lower()
        self.current_month = datetime.now().strftime("%B").lower()
        self.budget_per_week = BUDGET_PER_WEEK
        self.file_path = "budget_per_week.json"
        self.file_path_other_costs = "budget_per_week_other_costs.json"
        self.records = self.load_records()
        self.records_other = self.load_records(other_costs=True)

    def get_records(self, other_costs=False):
        """Get the appropriate records based on other_costs parameter."""
        return self.records_other if other_costs else self.records

    def get_file_path(self, other_costs=False):
        """Get the appropriate file path based on other_costs parameter."""
        return self.file_path_other_costs if other_costs else self.file_path

    def load_records(self, other_costs=False) -> dict:
        """Load budget records from the appropriate JSON file based on the other_costs parameter."""
        filename = self.get_file_path(other_costs)
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_records(self, other_costs=False):
        """Save records atomically to avoid corrupting JSON if something crashes mid-write."""
        fd, temp_path = tempfile.mkstemp()
        records = self.get_records(other_costs)
        file_path = self.get_file_path(other_costs)
        with os.fdopen(fd, "w") as tmp:
            json.dump(records, tmp, indent=2)

        os.replace(temp_path, file_path)

    def get_total_for_month(self, other_costs=False):
        """Calculate the total spend for current month."""
        records = self.get_records(other_costs)

        if self.current_month not in records:
            return 0

        current_month_records = records[self.current_month]

        total = 0

        for week_no in current_month_records:
            week_records = current_month_records[week_no]
            for day in week_records.values():
                for cost in day:
                    total += cost["cost"]

        return round(total, 2)

    def get_total_for_week(self, week: str = None, other_costs: bool = False) -> int:
        """Calculate the total spend for current week."""
        records = self.get_records(other_costs)

        if self.current_month not in records:
            return 0

        current_month_records = records[self.current_month]

        week = str(week) if week else self.current_week

        if week not in current_month_records:
            return 0

        total = 0

        for day in current_month_records[week].values():
            for cost in day:
                total += cost["cost"]

        return round(total, 2)

    def get_total_for_day(self, other_costs=False) -> int:
        """Calculate the total spending for a specified day within a week."""
        records = self.get_records(other_costs)

        month_data = records.get(self.current_month, {})
        week_data = month_data.get(self.current_week, {})
        day_records = week_data.get(self.current_day, [])
        total = sum(item.get("cost", 0) for item in day_records)
        return round(total, 2)

    def get_remaining_for_week(self, week: int = None) -> int:
        """Calculate the remaining budget for the specified week."""
        return round(self.budget_per_week - self.get_total_for_week(), 2)

    def add_cost(
        self,
        cost_name: str,
        cost_price: float,
        other_costs: bool = False,
        cost_is_debt: bool = False,
    ):
        """
        Add a cost entry for the current week and day.

        Parameters:
            cost_name (str): The name of the cost.
            cost_price (Any): The value of the cost. Should be a float
            manual_select_day (bool): If True, use manual_day instead of today's day.
            manual_day (str): Day name to assign the cost to (e.g. "Monday").
            other_costs (bool): If True, add to other costs that don't affect weekly budget.
            cost_is_debt (bool): If True, add a debt cost (money you was owed). These are - values

        Example:
            budget.add_cost("Coffee", 4)
            budget.add_cost("Lunch", 12, manual_select_day=True, manual_day="Monday")

        Output:
            {
              9: {
                "friday": [
                  {"name": "Coffee", "cost": 4}
                ],
                "monday": [
                  {"name": "Lunch", "cost": 12}
                ]
              }
            }
        """
        records = self.get_records(other_costs)

        if self.current_month not in records:
            records[self.current_month] = {}

        current_month_records = records[self.current_month]

        if self.current_week not in current_month_records:
            current_month_records[self.current_week] = {}

        current_weeks_records = current_month_records[self.current_week]

        if self.current_day not in current_weeks_records:
            current_weeks_records[self.current_day] = []

        current_day_records = current_weeks_records[self.current_day]

        if cost_is_debt:
            # cost_price should always be negative is cost_is_debt
            # if user inputs negative value in tool, it does not do * -1 transformation
            if cost_price > 0:
                cost_price = cost_price * -1

        current_day_records.append({"name": cost_name, "cost": cost_price})

        self.save_records(other_costs=other_costs)

        print(
            f"{'debt' if cost_is_debt else 'cost'} '{cost_name}' -> £{cost_price} "
            f"added to {self.current_month}/{self.current_week}/{self.current_day} records"
        )

        if other_costs:
            print(
                f"your total other spend for today is {self.get_total_for_day(other_costs=True)}, "
                f"your total other spend for the week is {self.get_total_for_week(other_costs=True)}"
            )
        else:
            print(
                f"your total spend for today is {self.get_total_for_day()}, "
                f"your remaining spend for the week is {self.get_remaining_for_week()}"
            )

        return self.get_records(other_costs)

    def run(self):
        """
        Run the budget tracker application with cost type selection.

        User first selects between tracking main costs (affecting weekly budget)
        or other costs (not affecting weekly budget).
        """
        print(
            f"your current weekly budget is £{self.budget_per_week}, "
            f"you have £{self.get_remaining_for_week()} left. "
            f"There are {7 - datetime.now().isoweekday()} day(s) left"
        )

        # First level menu - select cost type
        cost_type_options = [
            "Track main costs (affects weekly budget)",
            "Track other costs (bills, etc. - does not affect weekly budget)",
            "Quit",
        ]

        cost_type_menu = TerminalMenu(cost_type_options)

        while True:
            cost_type_choice = cost_type_menu.show()

            # Quit
            if cost_type_choice == 2:
                break

            # Set other_costs flag based on selection
            other_costs = cost_type_choice == 1
            cost_type_label = "Other costs" if other_costs else "Main costs"

            # Second level menu - operations for the selected cost type
            options = [
                f"Add a {cost_type_label.lower().rstrip('s')}",
                "Add a debt (this is money you are owed)",
                "Show remaining budget"
                if not other_costs
                else f"Show remaining budget (not applicable for {cost_type_label.lower()})",
                f"Show total {cost_type_label.lower()} this week",
                f"Show total {cost_type_label.lower()} this month",
                f"Show all {cost_type_label.lower()} records",
                "Back to cost type selection",
            ]

            menu = TerminalMenu(options)

            while True:
                print(f"\nCurrently tracking: {cost_type_label}")
                choice = menu.show()

                if choice in (0, 1):  # Add cost or a debt
                    cost_type_label = (
                        cost_type_label.rstrip("s") if choice == 0 else "debt"
                    )
                    name = prompt(f"{cost_type_label} name: ")

                    while True:
                        price_str = prompt(f"{cost_type_label} price: ")
                        try:
                            price = float(price_str)
                            break
                        except ValueError:
                            print("Please enter a valid number")

                    self.add_cost(
                        name, price, other_costs=other_costs
                    ) if choice == 0 else self.add_cost(
                        name, price, other_costs=other_costs, cost_is_debt=True
                    )

                elif choice == 2:  # Show remaining budget
                    if not other_costs:
                        print(f"Remaining budget: £{self.get_remaining_for_week()}")
                    else:
                        print("Remaining budget not applicable for other costs.")

                elif choice == 3:  # Show total week
                    total = self.get_total_for_week(other_costs=other_costs)
                    print(f"Total {cost_type_label.lower()} this week: £{total}")

                elif choice == 4:  # Show total month
                    total = self.get_total_for_month(other_costs=other_costs)
                    print(f"Total {cost_type_label.lower()} this month: £{total}")

                elif choice == 5:  # Show records
                    records = self.get_records(other_costs)
                    print(json.dumps(records, indent=2))

                elif choice == 6:  # Back
                    break


if __name__ == "__main__":
    BudgetPerWeek().run()
