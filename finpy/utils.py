import termcharts
from rich.console import Console

console = Console()

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

def render_chart(data, title, kind="doughnut"):
    """
    Renders a chart using termcharts.
    data: list of tuples (label, value)
    kind: "doughnut" or "bar" or "pie"
    """
    if kind == "doughnut":
        chart = termcharts.doughnut(
            data= data,
            title=title,
            rich=True
        )

        console.print(chart)
    elif kind == "bar":
        chart = termcharts.bar(
            data=data,
            title=title,
            rich=True
        )

        console.print(chart)
    elif kind == "pie":
        chart = termcharts.pie(
            data=data,
            title=title,
            rich=True
        )

        console.print(chart)
    else:
        console.print(f"Unsupported chart type: {kind}", style="bold red")