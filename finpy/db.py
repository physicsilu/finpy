import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table

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