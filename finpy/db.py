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

def report(args):
    """
    Generate expense report for a date range
    """

    conn = connect_db()
    cur = conn.cursor()

    try:

        # -----------------------
        # Parse Dates
        # -----------------------
        try:
            start = datetime.strptime(args.start, "%Y-%m-%d").date()
            end = datetime.strptime(args.end, "%Y-%m-%d").date()
        except ValueError:
            console.print(
                " Invalid date format. Use YYYY-MM-DD",
                style="bold red"
            )
            return

        if start > end:
            console.print(
                " Start date must be before end date",
                style="bold red"
            )
            return

        console.print(
            f"\n Expense Report: {start} → {end}\n",
            style="bold cyan"
        )

        # -----------------------
        # TOTAL
        # -----------------------
        cur.execute(
            """
            SELECT SUM(amount)
            FROM transactions
            WHERE type='expense'
            AND date BETWEEN ? AND ?
            """,
            (start.isoformat(), end.isoformat())
        )

        res = cur.fetchone()
        total = res[0] if res and res[0] else 0

        console.print(
            f" Total Expense: ₹{total:.2f}\n",
            style="bold green"
        )

        # Transactions list
        cur.execute(
            """
            SELECT id, date, type, amount, category, note
            FROM transactions
            WHERE date BETWEEN ? AND ?
            """,
            (start.isoformat(), end.isoformat())
        )

        rows = cur.fetchall()
        table = Table(title="Financial Entries")

        cols = ["ID","Date", "Type", "Amount", "Category", "Note"]
        for col in cols:
            table.add_column(col)

        for row in rows:
            table.add_row(*[str(item) for item in row])
        
        console.print(table)

        # -----------------------
        # CATEGORY BREAKDOWN
        # -----------------------
        if args.cat:

            cur.execute(
                """
                SELECT category, SUM(amount)
                FROM transactions
                WHERE type='expense'
                AND date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY SUM(amount) DESC
                """,
                (start.isoformat(), end.isoformat())
            )

            rows = cur.fetchall()

            if rows:

                render_table(
                    title="Category-wise Breakdown",
                    headers=["Category", "Amount"],
                    rows=rows,
                    plot=args.plot,
                    chart_title=f"Expenses ({start} → {end})"
                )

            else:
                console.print(" No category data found.")

    finally:
        conn.close()

def delete_transaction(args):
    """
    Delete a transaction by ID
    """

    conn = connect_db()
    cur = conn.cursor()

    tx_id = args.id

    try:
        cur.execute(
            """
            SELECT * FROM transactions WHERE id=?
            """, (tx_id,)
        )

        row = cur.fetchone()
        if not row:
            console.print(f"Transaction ID {tx_id} not found.", style="bold red")
            return
        
        console.print("Transaction to delete:", style="bold yellow")
        console.print(row)
        
        confirm = input("Confirm deletion (y/n): ")
        if confirm.lower() != 'y':
            console.print("Deletion cancelled.", style="bold red")
            return

        cur.execute(
            """
            DELETE FROM transactions WHERE id=?
            """, (tx_id,)
        )

        conn.commit()
        console.print(f"Transaction ID {tx_id} deleted.", style="bold green")

    finally:
        conn.close()

def update_transaction(args):
    """
    Update a transaction by ID
    """

    conn = connect_db()
    cur = conn.cursor()

    tx_id = args.id

    try:
        cur.execute(
            "SELECT * FROM transactions WHERE id=?",
            (tx_id,)
        )

        row = cur.fetchone()

        if not row:
            console.print(
                f"Transaction ID {tx_id} not found.", 
                style="bold red"
            )

            return
        
        if args.amount is not None:
            cur.execute(
                """
                UPDATE transactions
                SET amount = ?
                WHERE id = ?
                """, (args.amount, tx_id)
            )

            console.print(f"Updated the amount to {args.amount}", style="bold green")
        
        if args.category is not None:
            cur.execute(
                """
                UPDATE transactions
                SET category = ?
                WHERE id = ?
                """, (args.category, tx_id)
            )

            console.print(f"Updated the category to {args.category}", style="bold green") 

        if args.note is not None:
            cur.execute(
                """
                UPDATE transactions
                SET note = ?
                WHERE id = ?
                """, (" ".join(args.note), tx_id)
            )

            note_text = " ".join(args.note)

            console.print(f"Updated the note to {note_text}", style="bold green")

        conn.commit()

    finally:
        conn.close()


def get_summary_data():
    """
    Return total income, expense and savings.

    input: None
    output: {
        "income": float,
        "expense": float,
        "savings": float
    }
    output type: dict
    """

    conn = connect_db()
    cur = conn.cursor()

    # Total income
    cur.execute(
        """
        SELECT SUM(amount)
        FROM transactions
        WHERE type='income'
        """
    )

    income = cur.fetchone()[0] or 0

    # Total Expense
    cur.execute(
        """
        SELECT SUM(amount)
        FROM transactions
        WHERE type='expense'
        """
    )

    expense = cur.fetchone()[0] or 0

    conn.close()

    savings = income - expense

    return{
        "income": income,
        "expense": expense,
        "savings": savings
    }

def get_all_transactions():
    """
    Fetch all transactions from the database.

    Returns:
        List of tuples: Each tuple contains (id, date, type, amount, category, note)
    """

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, date, type, amount, category, note
        FROM transactions
        ORDER BY date DESC
        """
    )

    rows = cur.fetchall()
    conn.close()

    return rows