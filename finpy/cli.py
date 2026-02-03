import argparse
from finpy.db import init_db, add_entry, get_summary, list_entries, monthly_report, yearly_report

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

    summary.set_defaults(func=get_summary)

    # List
    lst = subparsers.add_parser(
        "list",
        help="List all transactions"
    )

    lst.set_defaults(func=list_entries)

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

    # Parse
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()