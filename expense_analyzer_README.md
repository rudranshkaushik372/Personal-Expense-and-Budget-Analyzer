# Personal Expense and Budget Analyzer
Course: Computational Thinking and Programming (2026CSAE100), Bennett University

Team:
- Rudransh Kaushik (S26CSEU2230)
- Divyank Chaudhary (S26CSEU2227)
- Akshat Aggarwal (S26CSEU2221)

GitHub: https://github.com/rudranshkaushik372/Personal-Expense-and-Budget-Analyzer

## Overview
A single-folder, self-contained Python CLI application that records personal expenses, analyses spending by month, category, and date range, compares total expenditure against a configurable monthly budget, and triggers rule-based alerts (`WITHIN BUDGET`, `WARNING`, `OVER BUDGET`).

## Folder Structure
```text
expense_analyzer/
├── expense_analyzer.py   # Complete standalone application (auto-initializes sample data)
├── PROJECT_DOCS.docx     # Complete project documentation, architecture, sample outputs & screenshots
└── README.md             # Quick-start guide and overview
```

## How to Run
```bash
python expense_analyzer.py
```
Optional (for bar chart export in Option 8):
```bash
pip install matplotlib
```

## Key Features
1. **Auto-Initialized Dataset**: Automatically generates `expenses.csv` with 20 sample transactions (Sept & Oct 2026) on first run if no CSV exists.
2. **Menu-Driven CLI (Options 0–9)**: Add expense, view all expenses, monthly report, category analysis, rule-based budget alert, date-range filter, month-wise comparison, export `.txt` report + `.png` chart, and update budget/threshold settings.
3. **Rule-Based Alert Engine**:
   - `< 80%` used: `WITHIN BUDGET`
   - `80% – 99.9%` used: `WARNING`
   - `>= 100%` used: `OVER BUDGET`
