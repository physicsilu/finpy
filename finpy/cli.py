import argparse
from finpy.db import (
    init_db, 
    add_transaction, 
    get_summary_data, 
    get_all_transactions, 
    get_monthly_report_data, 
    get_yearly_report_data, 
    get_report_data, 
    get_transaction_by_id,
    delete_transaction_by_id,
    update_transaction_by_id,
)

from rich.table import Table
from rich.console import Console

from .utils import render_chart

console = Console()

def summary_cmd(_):
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

def list_cmd(_):
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

def montly_cmd(args):
    """
    Generates monthly report (CLI layer)
    """

    data = get_monthly_report_data(args.month, args.year)
    total_expense = data["total"]
    rows = data['by_category']

    if not rows:
        console.print("No transactions found for this month.", style="yellow")
        return
    
    console.print(f"Total Expense: ₹{total_expense:.2f}", style="green")

    table = Table(title=f"Monthly Report - {args.month}/{args.year}")

    table.add_column("Category")
    table.add_column("Amount", justify="right")

    table_data = {}

    for cat, amt in rows:
        table.add_row(cat, f"₹{amt:.2f}")
        table_data[cat] = amt

    console.print(table)

    if args.plot and table_data:
        render_chart(
            data=table_data,
            title=f"Expense Distribution - {args.month}/{args.year}",
            kind="doughnut"
        )   

def yearly_cmd(args):
    """
    Generates yearly report (CLI layer)
    """

    data = get_yearly_report_data(args.year)

    total_expense = data["total"]
    by_category = data["by_category"]
    by_month = data["by_month"]

    if not total_expense:
        console.print("No transactions found for this year.", style="yellow")
        return
    
    console.print(f"Total Expense: ₹{total_expense:.2f}", style="green")

    if args.cat and by_category:
        cat_table = Table(title=f"Yearly Report - {args.year} (Category-wise)")

        cat_table.add_column("Category")
        cat_table.add_column("Amount", justify="right")

        cat_data = {}

        for cat, amt in by_category:
            cat_table.add_row(cat, f"₹{amt:.2f}")
            cat_data[cat] = amt

        console.print(cat_table)

        if args.plot and cat_data:
            render_chart(
                data=cat_data,
                title=f"Expense Distribution - {args.year}",
                kind="doughnut"
            )

    if args.monthly and by_month:
        month_map = {
            "01": "Jan", "02": "Feb", "03": "Mar",
            "04": "Apr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Aug", "09": "Sep",
            "10": "Oct", "11": "Nov", "12": "Dec"
        }

        month_table = Table(title=f"Yearly Report - {args.year} (Month-wise)")
        month_table.add_column("Month")
        month_table.add_column("Amount", justify="right")
        month_data = {}

        for month, amt in by_month:
            month_name = month_map.get(month, month)
            month_table.add_row(month_name, f"₹{amt:.2f}")
            month_data[month_name] = amt
        console.print(month_table)
        if args.plot and month_data:
            render_chart(
                data=month_data,
                title=f"Monthly Expense Distribution - {args.year}",
                kind="bar"
            )

def report_cmd(args):
    """
    Generates expense report for a date range (CLI layer)
    """

    try:
        data = get_report_data(args.start, args.end)
    except ValueError as e:
        console.print(str(e), style="bold red")
        return

    total_expense = data["total"]
    all_transactions = data["all_transactions"]
    by_category = data["by_category"]

    if not total_expense:
        console.print("No transactions found for this date range.", style="yellow")
        return
    
    console.print(f"Total Expense: ₹{total_expense:.2f}", style="green")

    if all_transactions:
        title = f"Transactions from {args.start} to {args.end}"
        table = Table(title=title)
        table.add_column("ID", justify="right")
        table.add_column("Date")
        table.add_column("Type")
        table.add_column("Amount", justify="right")
        table.add_column("Category")
        table.add_column("Note")
        for entry in all_transactions:
            table.add_row(
                str(entry[0]),
                entry[1],
                entry[2],
                f"₹{entry[3]:.2f}",
                entry[4],
                entry[5] or ""
            )
        console.print(table)

    if args.cat and by_category:
        cat_table = Table(title=f"Expense by Category from {args.start} to {args.end}")
        cat_table.add_column("Category")
        cat_table.add_column("Amount", justify="right")
        cat_data = {}
        for cat, amt in by_category:
            cat_table.add_row(cat, f"₹{amt:.2f}")
            cat_data[cat] = amt
        console.print(cat_table)

        if args.plot and cat_data:
            render_chart(
                data=cat_data,
                title=f"Expense Distribution from {args.start} to {args.end}",
                kind="doughnut"
            )

def delete_cmd(args):

    tx_id = args.id

    row = get_transaction_by_id(tx_id)

    if not row:
        console.print(
            f"Transaction ID {tx_id} not found.",
            style="bold red"
        )
        return

    console.print("Transaction to delete:", style="bold yellow")
    console.print(row)

    confirm = input("Confirm deletion (y/n): ")

    if confirm.lower() != "y":
        console.print("Deletion cancelled.", style="yellow")
        return

    success = delete_transaction_by_id(tx_id)

    if success:
        console.print(
            f"Transaction {tx_id} deleted.",
            style="bold green"
        )

def update_cmd(args):

    tx_id = args.id

    note_text = None
    if args.note:
        note_text = " ".join(args.note)

    success = update_transaction_by_id(
        tx_id,
        amount=args.amount,
        category=args.category,
        note=note_text
    )

    if not success:
        console.print(
            f"Transaction ID {tx_id} not found.",
            style="bold red"
        )
        return

    console.print("Transaction updated successfully.", style="bold green")

def add_cmd(args):
    """
    CLI layer for adding transaction
    """

    note_text = ""

    if args.note:
        note_text = " ".join(args.note)

    success = add_transaction(
        tx_type=args.type,
        amount=args.amount,
        category=args.category,
        note=note_text
    )

    if success:
        console.print("Transaction added successfully.", style="bold green")


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

    # Parse
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()