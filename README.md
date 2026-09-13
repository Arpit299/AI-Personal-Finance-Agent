# AI Personal Finance Agent

AI Personal Finance Agent is a Python-based financial analytics tool that analyzes transaction data, tracks budgets and financial goals, identifies recurring expenses and unusual spending patterns, and generates structured financial reports.

## Features

* Income and expense analysis
* Spending category analysis
* Savings-rate calculation
* Recurring expense detection
* Spending anomaly detection
* Budget monitoring
* Financial goal tracking
* Top merchant analysis
* CSV and JSON support
* JSON report generation
* Built-in demo dataset
* Command-line interface

## Tech Stack

**Python | Data Analysis | Statistics | CSV | JSON | CLI**

## DSA Used

**Dictionary | Counter | defaultdict | List | Sorting | Hash-based Grouping**

## Usage

Run interactively:

```bash id="9s5q1h"
python ai_personal_finance_agent.py
```

Run the demo:

```bash id="lxx6cx"
python ai_personal_finance_agent.py --demo
```

Analyze a dataset:

```bash id="wt2l4q"
python ai_personal_finance_agent.py transactions.csv
```

Add budgets:

```bash id="dk4y84"
python ai_personal_finance_agent.py transactions.csv --budget Housing=50000 --budget Food=10000
```

Add a financial goal:

```bash id="ccvyl4"
python ai_personal_finance_agent.py transactions.csv --goal EmergencyFund:100000:25000
```

Generate a report:

```bash id="o7igoe"
python ai_personal_finance_agent.py transactions.csv --json finance_report.json
```

## Architecture

```text
Transactions
     ↓
Data Normalization
     ↓
Income / Expense Analysis
     ↓
Category Analysis
     ↓
Recurring Detection
     ↓
Anomaly Detection
     ↓
Budget Analysis
     ↓
Goal Tracking
     ↓
Financial Report
```

## Purpose

Designed to demonstrate Python-based financial data processing, statistical anomaly detection, transaction grouping, budget analysis, and personal finance automation.


