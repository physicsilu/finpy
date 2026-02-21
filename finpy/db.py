import sqlite3
from datetime import datetime
from rich.console import Console
from finpy.utils import fetch_expenses

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

def get_summary_between(start_date=None, end_date=None):
    """
    Return total income, expense and investment for a date range.
    input: start_date (str, optional), end_date (str, optional) in YYYY-MM-DD format
    output: {
        "income": float,
        "expense": float,
        "investment": float
    }
    output type: dict
    """

    conn = connect_db()
    cur = conn.cursor()

    query = """
        SELECT
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END),
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),
            SUM(CASE WHEN type='investment' THEN amount ELSE 0 END)
        FROM transactions
    """

    params = []

    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    cur.execute(query, params)
    income, expense, investment = cur.fetchone()
    conn.close()

    income = income or 0
    expense = expense or 0
    investment = investment or 0

    return {
        "income": income,
        "expense": expense,
        "investment": investment
    }

def get_summary_data():
    """
    Return total income, expense and investment.

    input: None
    output: {
        "income": float,
        "expense": float,
        "investment": float
    }
    output type: dict
    """

    return get_summary_between()

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

def get_monthly_report_data(month, year):
    """
    Fetch total expense and category-wise breakdown for a given month and year.

    Returns:
        {
            "total": float,
            "by_category": List of tuples (category, amount)
        }
    """

    conn = connect_db()
    cur = conn.cursor()

    # Total Expense
    res = fetch_expenses(
        cur=cur,
        year=year,
        month=month
    )
    total = res[0][0] if res and res[0][0] else 0

    # Category-wise Breakdown
    by_category = fetch_expenses(
        cur=cur,
        year=year,
        month=month,
        group_by="category"
    )

    conn.close()

    return {
        "total": total,
        "by_category": by_category
    }

def get_yearly_report_data(year):
    """
    Fetch total expense, category-wise breakdown and month-wise breakdown for a given year.

    Returns:
        {
            "total": float,
            "by_category": List of tuples (category, amount),
            "by_month": List of tuples (month, amount)
        }
    """

    conn = connect_db()
    cur = conn.cursor()

    # Total Expense
    res = fetch_expenses(
        cur=cur,
        year=year
    )
    total = res[0][0] if res and res[0][0] else 0

    # Category-wise Breakdown
    by_category = fetch_expenses(
        cur,
        year=year,
        group_by="category"
    )

    # Monthly Breakdown
    by_month = fetch_expenses(
        cur,
        year=year,
        group_by="month"
    )

    conn.close()

    return {
        "total": total,
        "by_category": by_category,
        "by_month": by_month
    }

def get_report_data(start, end):
    """
    Fetch total expense and category-wise breakdown for a given date range.

    Returns:
        {
            "total": float,
            "all_transactions": List of tuples (id, date, type, amount, category, note),
            "by_category": List of tuples (category, amount)
        }
    """
    conn = connect_db()
    cur = conn.cursor()

    try:

        # -----------------------
        # Parse Dates
        # -----------------------
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        if start_date > end_date:
            raise ValueError("Start date cannot be after end date.")

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
            (start_date.isoformat(), end_date.isoformat())
        )

        res = cur.fetchone()
        total = res[0] if res and res[0] else 0

        # Transactions list
        cur.execute(
            """
            SELECT id, date, type, amount, category, note
            FROM transactions
            WHERE date BETWEEN ? AND ?
            """,
            (start_date.isoformat(), end_date.isoformat())
        )

        all_transactions = cur.fetchall()
        

        # -----------------------
        # CATEGORY BREAKDOWN
        # -----------------------
        cur.execute(
                """
                SELECT category, SUM(amount)
                FROM transactions
                WHERE type='expense'
                AND date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY SUM(amount) DESC
                """,
                (start_date.isoformat(), end_date.isoformat())
            )

        by_category = cur.fetchall()

    finally:
        conn.close()

    return {
        "total": total,
        "all_transactions": all_transactions,
        "by_category": by_category
    }

def get_transaction_by_id(tx_id):
    """
    Fetch a transaction by its ID.

    Returns:
        Tuple: (id, date, type, amount, category, note) or None if not found
    """

    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT *
            FROM transactions
            WHERE id=?
            """, (tx_id,)
        )

        row = cur.fetchone()
        return row

    finally:
        conn.close()

def delete_transaction_by_id(tx_id):
    """
    Delete a transaction by its ID.

    Returns:
        bool: True if deleted, False if not found
    """

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM transactions
        WHERE id=?
        """, (tx_id,)
    )

    deleted = cur.rowcount > 0

    conn.commit()
    conn.close()

    return deleted

def update_transaction_by_id(tx_id, amount=None, category=None, note=None):
    """
    Update a transaction by its ID.

    Returns:
        bool: True if updated, False if not found
    """

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id FROM transactions WHERE id=?
        """, (tx_id,)
    )

    if not cur.fetchone():
        conn.close()
        return False
    
    if amount is not None:
        cur.execute(
            """
            UPDATE transactions
            SET amount = ?
            WHERE id = ?
            """, (amount, tx_id)
        )

    if category is not None:
        cur.execute(
            """
            UPDATE transactions
            SET category = ?
            WHERE id = ?
            """, (category, tx_id)
        )

    if note is not None:
        cur.execute(
            """
            UPDATE transactions
            SET note = ?
            WHERE id = ?
            """, (note, tx_id)
        )

    conn.commit()
    conn.close()

    return True

def add_transaction(tx_type, amount, category, note):
    """
    Add a new transaction to the database.
    Returns:
        bool: True if added successfully
    """

    conn = connect_db()
    cur = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    cur.execute(
        """
        INSERT INTO transactions
        VALUES (NULL, ?, ?, ?, ?, ?)
        """, (date, tx_type, amount, category, note)
    )

    conn.commit()
    conn.close()

    return True

def get_recent_transactions(limit=5):
    """
    Fetch recent transactions.

    Returns:
        List: Each tuple contains (id, date, type, amount, category, note)
    """

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, date, type, amount, category, note
        FROM transactions
        ORDER BY date DESC, id DESC
        LIMIT ?
        """, (limit,)
    )

    rows = cur.fetchall()
    conn.close()

    return rows

def get_mon_summary_data(month, year):
    """
    Fetch total income, expense and investment for a given month and year.

    Returns:
        {
            "income": float,
            "expense": float,
            "investment": float
        }
    """

    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-31"
    return get_summary_between(start_date, end_date)

def get_yr_summary_data(year):
    """
    Fetch total income, expense and investment for a given year.

    Returns:
        {
            "income": float,
            "expense": float,
            "investment": float
        }
    """
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    return get_summary_between(start_date, end_date)