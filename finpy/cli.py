import argparse
from finpy.db import (
    init_db, 
    add_entry, 
    get_summary_data, 
    get_all_transactions, 
    monthly_report, 
    yearly_report, 
    report, 
    delete_transaction, 
    update_transaction
    )

from rich.table import Table
from rich.console import Console

console = Console()

def summary_cmd(args):
    """
    Shows financial summary (CLI layer)
    """

    data = get_summary_data()

    table = Table(title="Financial Summary")

    table.add_column("Metric")
    table.add_column("Amount", justify="right")

    table.add_row("Total Income", f"₹{data['income']:.2f}")
    table.add_row("Total Expense", f"₹{data['expense']:.2f}")
    table.add_row("Savings", f"₹{data['savings']:.2f}")

    console.print(table)

def list_cmd(args):
    """
    Lists all transactions (CLI layer)
    """

    entries = get_all_transactions()

    if not entries:
        console.print("No transactions found.", style="yellow")
        return

    table = Table(title="All Transactions")

    table.add_column("ID", justify="right")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Amount", justify="right")
    table.add_column("Category")
    table.add_column("Note")

    for entry in entries:
        table.add_row(
            str(entry[0]),
            entry[1],
            entry[2],
            f"₹{entry[3]:.2f}",
            entry[4],
            entry[5] or ""
        )

    console.print(table)

def main():
    init_db()

    parser = argparse.ArgumentParser(
        prog="finpy",
        description="Personal Finance CLI Tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Add
    add = subparsers.add_parser(
            "add",
            help="Add income/expense" 
        )
    
    add.add_argument(
        "type",
        choices=["income", "expense"],
        help="Transaction type"
    )

    add.add_argument(
        "amount",
        type=float,
        help="Amount in rupees"
    )

    add.add_argument(
        "category",
        help="Category (food, rent, etc)"
    )

    add.add_argument(
        "note",
        nargs="*",
        help="Short note"
    )

    add.set_defaults(func=add_entry)

    # Summary
    summary = subparsers.add_parser(
        "summary",
        help="Show financial summary"
    )

    summary.set_defaults(func=summary_cmd)

    # List
    lst = subparsers.add_parser(
        "list",
        help="List all transactions"
    )

    lst.set_defaults(func=list_cmd)

    # Monthly Report
    mon_report = subparsers.add_parser(
        "mon_report",
        help="Generate monthly report"
    )

    mon_report.add_argument(
        "month",
        type=int,
        help="Month (1-12)"
    )

    mon_report.add_argument(
        "year",
        type=int,
        help="Year (e.g., 2024)"
    )

    mon_report.add_argument(
        "--plot",
        action="store_true",
        help="True or False for graph"
    )

    mon_report.set_defaults(func=monthly_report)

    # Yearly Report
    yr_report = subparsers.add_parser(
        "yr_report",
        help="Generate yearly report"
    )

    yr_report.add_argument(
        "year",
        type=int,
        help="Year (e.g., 2024)"
    )

    yr_report.add_argument(
        "--cat",
        action="store_true",
        help="Show category-wise summary"
    )

    yr_report.add_argument(
        "--monthly",
        action="store_true",
        help="Show month-wise breakdown"
    )

    yr_report.add_argument(
        "--plot",
        action="store_true",
        help="Show graphs"
    )

    yr_report.set_defaults(func=yearly_report)

    # Report
    range_report = subparsers.add_parser(
        "report",
        help="Generate expense report for a date range"
    )

    range_report.add_argument(
        "--from",
        dest="start",
        required=True,
        help="Start date (YYYY-MM-DD)"
    )

    range_report.add_argument(
        "--to",
        dest="end",
        required=True,
        help="End date (YYYY-MM-DD)"
    )

    range_report.add_argument(
        "--cat",
        action="store_true",
        help="Show category-wise breakdown"
    )

    range_report.add_argument(
        "--plot",
        action="store_true",
        help="Show expense chart"
    )

    range_report.set_defaults(func=report)

    # Delete
    delete = subparsers.add_parser(
        "delete",
        help="Delete a transaction by ID"
    )

    delete.add_argument(
        "id",
        type=int,
        help="Transaction ID to delete"
    )

    delete.set_defaults(func=delete_transaction)

    # Update
    update = subparsers.add_parser(
        "update",
        help="Update a transaction by ID"
    )

    update.add_argument(
        "id",
        type=int,
        help="Transaction ID to update"
    )

    update.add_argument(
        "--amount",
        dest="amount",
        type=float,
        help="Updated amount"
    )

    update.add_argument(
        "--category",
        dest="category",
        type=str,
        help="Updated category"
    )

    update.add_argument(
        "--note",
        dest="note",
        nargs="*",
        help="Updated note"
    )

    update.set_defaults(func=update_transaction)

    # Parse
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()