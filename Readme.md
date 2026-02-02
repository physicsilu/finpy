# finpy

A personal finance CLI tool built in Python for tracking your income and expenses directly from the terminal.

## Features
- Add income and expense entries
- View financial summary
- List all transactions
- Local storage using SQLite
- Terminal output using `rich`

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

### Add Income
```bash
finpy add income 9000 salary main
```

### Add Expense
```bash
finpy add expense 200 food masala dosa
```

### Show Summary
```bash
finpy summary
```

### List All Transactions
```bash
finpy list
```

## Data Storage
All data is stored locally in SQLite database file: `finpy.db`. Deleting this file will remove all the stored data.

## Tech Stack
- Python3
- argparse (CLI)
- SQLite (DB)
- rich (Terminal UI)

## Project Status
This is an early-stage hobby project. More features will be added over time. Planned features:
- Monthly reports
- Budget tracking
- Data backup
- Graphs and visualizations

I am open to all kinds of suggestions!