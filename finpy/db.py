import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table
import termcharts

DB = "finpy.db"
console = Console()

def connect_db():
    """
    Connect to the SQLite database.
    """
    return sqlite3.connect(DB)

def init_db():
    """
    Initialize the database with required tables.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY,
            date TEXT,
            type TEXT,
            amount REAL,
            category TEXT,
            note TEXT
        )
        """
    )

    conn.commit()
    conn.close()

def add_entry(args):
    """
    Add a new financial entry to the database.
    """
    conn = connect_db()
    cur = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        """
        INSERT INTO transactions
        VALUES (NULL, ?, ?, ?, ?, ?)
        """, (date, args.type, args.amount, args.category, " ".join(args.note))
    )

    conn.commit()
    conn.close()

    console.print("Added!", style= "green")

def get_summary(_):
    """
    Get a summary of financial data.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT SUM(amount) 
        FROM transactions
        WHERE type='income'
        """
    )

    income = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT SUM(amount) 
        FROM transactions
        WHERE type='expense'
        """
    )

    expense = cur.fetchone()[0] or 0

    savings = income - expense

    table = Table(title="Financial Summary")

    table.add_column("Metric")
    table.add_column("Amount")

    table.add_row("Total Income", f"{income:.2f}")
    table.add_row("Total Expense", f"{expense:.2f}")
    table.add_row("Savings", f"{savings:.2f}")

    console.print(table)

    conn.close()

def list_entries(_):
    """
    List all financial entries.
    """

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT date, type, amount, category, note
        FROM transactions
        """
    )

    rows = cur.fetchall()

    table = Table(title="Financial Entries")

    cols = ["Date", "Type", "Amount", "Category", "Note"]
    for col in cols:
        table.add_column(col)

    for row in rows:
        table.add_row(*[str(item) for item in row])
    
    console.print(table)
    conn.close()

def fetch_expenses(cur, year=None, month=None, group_by=None):
    """
    Fetch aggregated expense data.

    group_by:
        None        -> total
        "category"  -> by category
        "month"     -> by month
    """

    query = """
        SELECT {select_clause}
        FROM transactions
        WHERE type='expense'
    """

    params = []

    # Year filter
    if year is not None:
        query += " AND strftime('%Y', date)=?"
        params.append(str(year))

    # Month filter
    if month is not None:
        query += " AND strftime('%m', date)=?"
        params.append(f"{month:02d}")

    # Grouping
    if group_by == "category":
        select_clause = "category, SUM(amount)"
        query += " GROUP BY category ORDER BY SUM(amount) DESC"

    elif group_by == "month":
        select_clause = "strftime('%m', date), SUM(amount)"
        query += " GROUP BY strftime('%m', date) ORDER BY strftime('%m', date)"

    else:
        select_clause = "SUM(amount)"

    query = query.format(select_clause=select_clause)

    cur.execute(query, params)

    return cur.fetchall()

def render_table(title, headers, rows, plot=False, chart_title=None):

    table = Table(title=title)

    for col in headers:
        table.add_column(col, justify="right" if col == "Amount" else "left")

    data = {}

    for k, v in rows:
        table.add_row(str(k), f"₹{v:.2f}")
        data[str(k)] = v

    console.print(table)

    if plot and data:

        chart = termcharts.doughnut(
            data,
            title=chart_title or title,
            rich=True
        )

        console.print(chart)


def monthly_report(args):
    """
    Generate monthly expense report
    """

    conn = connect_db()
    cur = conn.cursor()

    year = args.year
    month = args.month
    plot_graph = args.plot

    console.print(
        f"\n Monthly Report - {month:02d}/{year}\n",
        style="bold cyan"
    )

    # Total Expense
    total = fetch_expenses(
        cur,
        year=year,
        month=month
    )[0][0] or 0

    console.print(
        f"Total Expense: ₹{total:.2f}\n",
        style="bold green"
    )

    # Category-wise Breakdown
    rows = fetch_expenses(
        cur,
        year=year,
        month=month,
        group_by="category"
    )

    if rows:

        render_table(
            title="Category-wise Breakdown",
            headers=["Category", "Amount"],
            rows=rows,
            plot=plot_graph,
            chart_title=f"Expenses {month:02d}/{year}"
        )

    else:
        console.print(" No data found for this month.")

    conn.close()


def yearly_report(args):
    """
    Generate yearly expense report
    """

    conn = connect_db()
    cur = conn.cursor()

    year = args.year
    show_cat = args.cat
    show_monthly = args.monthly
    plot_graph = args.plot

    console.print(f"\nYearly Report - {year}\n", style="bold cyan")

    # Total Expense
    res = fetch_expenses(cur, year=year)
    total = res[0][0] if res and res[0][0] else 0

    console.print(f"Total Expense: ₹{total:.2f}\n", style="bold green")

    # Category-wise Breakdown
    if show_cat:

        rows = fetch_expenses(
            cur,
            year=year,
            group_by="category"
        )

        if rows:
            render_table(
                title="Category-wise Breakdown",
                headers=["Category", "Amount"],
                rows=rows,
                plot=plot_graph,
                chart_title=f"Category Expenses - {year}"
            )


    # Monthly Breakdown
    if show_monthly:
        rows = fetch_expenses(
            cur,
            year=year,
            group_by="month"
        )

        month_map = {
            "01": "Jan", "02": "Feb", "03": "Mar",
            "04": "Apr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Aug", "09": "Sep",
            "10": "Oct", "11": "Nov", "12": "Dec"
        }

        rows = [
            (month_map[m], amt) for m, amt in rows
        ]

        if rows:
            render_table(
                title="Month-wise Breakdown",
                headers=["Month", "Amount"],
                rows=rows,
                plot=plot_graph,
                chart_title=f"Monthly Expenses - {year}"
            )


    conn.close()
