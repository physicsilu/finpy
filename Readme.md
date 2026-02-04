# finpy

A personal finance CLI tool built in Python for tracking your income and expenses directly from the terminal.

## Features
- Add income and expense entries
- View financial summary
- List all transactions
- Local storage using SQLite
- Terminal output using `rich`
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

### Add Income/Expense
```bash
finpy add <income/expense> <amount> <category> <note>
```

### Show Summary
```bash
finpy summary
```

### List All Transactions
```bash
finpy list
```

### Get Monthly Reports
```bash
finpy mon_report <month> <year>
```
Use `--plot` flag at the end for visualizing using a pie chart grouped by categories.

### Get Yearly Reports
```bash
finpy yr_report <year>
```
Use `--cat` flag for grouping by category and `--monthly` flag for grouping by month. As usual `--plot` flag for visualization.

### Get Reports for a Date Range
```bash
finpy report --from <start_date> --to <end_date>
```
Use `--cat` flag for grouping by category and `--plot` for visualization.

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
- Budget tracking
- Data backup

I am open to all kinds of suggestions!