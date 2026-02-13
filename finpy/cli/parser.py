import argparse
from finpy.db import init_db
from finpy.cli.commands import (
    summary_cmd,
    list_cmd,
    add_cmd,
    montly_cmd,
    yearly_cmd,
    report_cmd,
    delete_cmd,
    update_cmd,
    recent_cmd
)

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

    add.set_defaults(func=add_cmd)

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

    mon_report.set_defaults(func=montly_cmd)

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

    yr_report.set_defaults(func=yearly_cmd)

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

    range_report.set_defaults(func=report_cmd)

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

    delete.set_defaults(func=delete_cmd)

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

    update.set_defaults(func=update_cmd)

    # Recent
    recent_parser = subparsers.add_parser(
        "recent",
        help="Show recent transactions"
    )

    recent_parser.add_argument(
        "--n",
        dest="n",
        type=int,
        default=5,
        help="Number of recent transactions (default: 5)"
    )

    recent_parser.set_defaults(func=recent_cmd)


    # Parse
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()