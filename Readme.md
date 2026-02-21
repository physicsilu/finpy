# finpy

A personal finance CLI tool built in Python for tracking your income and expenses directly from the terminal.

## Features
- Add income, expense and investment entries
- View financial summary
- List all transactions
- List recent `n` transactions
- Local storage using SQLite
- Terminal output using `rich`
- Delete/Update particular transactions
- Monthly and Yearly reports
- Reports for a given date range

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/physicsilu/finpy.git
cd finpy
```

### 2. Install in development mode
```bash
pip install -e .
```

## Usage

### Add Income/Expense/Investment
```bash
finpy add --type <income/expense/investment> 
          --amount <amount> 
          --category <category> 
          --note <note...>
```

### Show Summary
```bash
finpy summary # for overall financial summary

finpy summary --from <start_date> --to <end_date> # for financial summary over a period
```

### List All Transactions
```bash
finpy list
```

### Delete a Particular Transaction
```bash
finpy delete <transaction_id>
```

### Update a Particular Transaction
```bash
finpy update <transaction_id> --amount <new_amount> # for updating amount
                              --category <new_category> # for updating category
                              --note <new_note> # for updating note  
```

### Get Monthly Reports
```bash
finpy monthly --month <month>
                 --year  <year>
```
Use `--plot` flag at the end for visualizing using a pie chart grouped by categories.

### Get Yearly Reports
```bash
finpy yearly --year <year>
```
Use `--cat` flag for grouping by category and `--monthly` flag for grouping by month. As usual `--plot` flag for visualization.

### Get Reports for a Date Range
```bash
finpy report --from <start_date> --to <end_date>
```
Use `--cat` flag for grouping by category and `--plot` for visualization.

### Get Recent `n` Transactions
```bash
finpy recent --n <number_of_transactions>
```
The default value is *5* transactions. 

## Data Storage
All data is stored locally in SQLite database file: `finpy.db`. Deleting this file will remove all the stored data.

## Tech Stack
- Python3
- argparse (CLI)
- SQLite (DB)
- rich (Terminal UI)
- termcharts

## Project Status
This is an early-stage hobby project. More features will be added over time. Planned features:
- Making a TUI
- Budget tracking
- Data backup

I am open to all kinds of suggestions!