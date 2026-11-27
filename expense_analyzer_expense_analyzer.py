"""
Personal Expense and Budget Analyzer (Single-File Standalone Edition)
Course : Computational Thinking and Programming (2026CSAE100)
Team   : Rudransh Kaushik, Divyank Chaudhary, Akshat Aggarwal

A self-contained menu-driven program that stores expenses in a CSV file,
summarises spending by month / category / date range, compares it with a budget,
and raises a rule-based alert — all within a single flat directory.
"""
import csv
import json
import os
from collections import defaultdict
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "expenses.csv")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
REPORT_DIR = BASE_DIR
FIELDS = ["date", "category", "description", "amount"]

DEFAULT_CONFIG = {
    "monthly_budget": 6000.0,
    "warning_threshold": 80.0,   # % of budget at which a warning starts
    "categories": ["Food", "Transport", "Education", "Entertainment",
                   "Shopping", "Other"],
}

SAMPLE_EXPENSES = [
    ("2026-09-01", "Food", "Breakfast at canteen", 120),
    ("2026-09-02", "Transport", "Metro card recharge", 200),
    ("2026-09-03", "Education", "Python reference book", 500),
    ("2026-09-04", "Education", "Stationery", 150),
    ("2026-09-05", "Shopping", "Sports shoes", 1899),
    ("2026-09-06", "Entertainment", "Movie ticket", 350),
    ("2026-09-08", "Food", "Lunch with friends", 280),
    ("2026-09-10", "Education", "Online course subscription", 570),
    ("2026-09-12", "Shopping", "T-shirt", 751),
    ("2026-09-13", "Shopping", "Phone cover", 99),
    ("2026-09-14", "Food", "Groceries", 400),
    ("2026-09-16", "Transport", "Cab fare", 200),
    ("2026-09-18", "Entertainment", "Gaming subscription", 400),
    ("2026-09-20", "Food", "Dinner", 280),
    ("2026-09-22", "Entertainment", "Concert pass", 300),
    ("2026-10-02", "Food", "Groceries", 520),
    ("2026-10-04", "Transport", "Metro card recharge", 250),
    ("2026-10-09", "Shopping", "Headphones", 1500),
    ("2026-10-15", "Education", "Notebooks", 230),
    ("2026-10-20", "Entertainment", "OTT subscription", 299),
]


def ensure_sample_data(path=DATA_FILE):
    """Auto-create expenses.csv with sample records if it does not exist yet."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)
            writer.writerows(SAMPLE_EXPENSES)


# ----------------------------------------------------------------- config
def load_config(path=CONFIG_FILE):
    """Load settings from JSON; fall back to defaults if missing/corrupt."""
    config = dict(DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print("Warning: config file is corrupt. Using default settings.")
    return config


def save_config(config, path=CONFIG_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


# ------------------------------------------------------------ data module
def parse_date(text):
    """Return a datetime.date for 'YYYY-MM-DD', or raise ValueError."""
    return datetime.strptime(text.strip(), "%Y-%m-%d").date()


def load_expenses(path=DATA_FILE):
    """Read and validate expenses. Returns (records, error_messages)."""
    records, errors = [], []
    try:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or set(FIELDS) - set(reader.fieldnames):
                return [], [f"CSV must contain columns: {', '.join(FIELDS)}"]
            for line_no, row in enumerate(reader, start=2):
                try:
                    date = parse_date(row["date"])
                    amount = float(row["amount"])
                    if amount < 0:
                        raise ValueError("amount cannot be negative")
                    category = row["category"].strip().title()
                    if not category:
                        raise ValueError("category is empty")
                    records.append({
                        "date": date,
                        "category": category,
                        "description": row["description"].strip(),
                        "amount": amount,
                    })
                except (ValueError, TypeError, KeyError) as err:
                    errors.append(f"Line {line_no}: skipped ({err})")
    except FileNotFoundError:
        return [], [f"File not found: {path}"]
    return records, errors


def add_expense(date_text, category, description, amount_text, path=DATA_FILE):
    """Validate one new expense and append it to the CSV. Returns (ok, msg)."""
    try:
        date = parse_date(date_text)
        amount = float(amount_text)
    except ValueError:
        return False, "Invalid date (use YYYY-MM-DD) or amount (must be a number)."
    if amount <= 0:
        return False, "Amount must be greater than zero."
    if not category.strip():
        return False, "Category cannot be empty."
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(FIELDS)
        writer.writerow([
            date.isoformat(),
            category.strip().title(),
            description.strip(),
            f"{amount:g}",
        ])
    return True, "Expense added successfully."


# -------------------------------------------------------- analysis module
def filter_by_month(records, month):
    """month is 'YYYY-MM'."""
    return [r for r in records if r["date"].strftime("%Y-%m") == month]


def filter_by_range(records, start, end):
    return [r for r in records if start <= r["date"] <= end]


def total_spent(records):
    return sum(r["amount"] for r in records)


def category_totals(records):
    totals = defaultdict(float)
    for r in records:
        totals[r["category"]] += r["amount"]
    return dict(totals)


def highest_category(totals):
    if not totals:
        return None, 0.0
    name = max(totals, key=totals.get)
    return name, totals[name]


def budget_usage(spent, budget):
    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")
    return spent / budget * 100


def budget_status(usage, warning_threshold=80.0):
    """Rule: <80% Within Budget, 80%..<100% Warning, >=100% Over Budget."""
    if usage >= 100:
        return "OVER BUDGET"
    if usage >= warning_threshold:
        return "WARNING"
    return "WITHIN BUDGET"


def monthly_comparison(records):
    """Return {month: total} sorted by month."""
    totals = defaultdict(float)
    for r in records:
        totals[r["date"].strftime("%Y-%m")] += r["amount"]
    return dict(sorted(totals.items()))


# ------------------------------------------------------- reporting module
def build_report(records, month, config):
    month_records = filter_by_month(records, month)
    spent = total_spent(month_records)
    budget = config["monthly_budget"]
    usage = budget_usage(spent, budget)
    status = budget_status(usage, config["warning_threshold"])
    top, _ = highest_category(category_totals(month_records))
    lines = [
        "PERSONAL EXPENSE & BUDGET ANALYZER",
        "-" * 42,
        f"Month: {month}",
        f"Transactions: {len(month_records)}",
        f"Total expenditure: Rs. {spent:.2f}",
        f"Budget: Rs. {budget:.2f}",
        f"Budget status: {status} ({usage:.1f}% used)",
        f"Highest spending category: {top if top else 'N/A'}",
    ]
    return "\n".join(lines)


def build_category_table(records, month):
    month_records = filter_by_month(records, month)
    totals = category_totals(month_records)
    spent = total_spent(month_records)
    lines = [
        f"CATEGORY-WISE EXPENDITURE ({month})",
        "-" * 42,
        f"{'Category':<16}{'Amount (Rs.)':>14}{'Share':>9}",
    ]
    for cat, amt in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        share = amt / spent * 100 if spent else 0
        lines.append(f"{cat:<16}{amt:>14.2f}{share:>8.1f}%")
    lines.append("-" * 42)
    lines.append(f"{'TOTAL':<16}{spent:>14.2f}{'100.0%':>9}")
    return "\n".join(lines)


def build_alert(records, month, config):
    spent = total_spent(filter_by_month(records, month))
    budget = config["monthly_budget"]
    usage = budget_usage(spent, budget)
    status = budget_status(usage, config["warning_threshold"])
    lines = [
        "RULE-BASED BUDGET ALERT",
        "-" * 42,
        f"Monthly budget: Rs. {budget:.2f}",
        f"Actual expenditure: Rs. {spent:.2f}",
        f"Budget usage: {usage:.1f}%",
    ]
    if status == "OVER BUDGET":
        lines += [
            "ALERT: Spending has exceeded the configured budget.",
            f"Overspent by: Rs. {spent - budget:.2f}",
            "Action: Review the highest spending category before",
            "making additional discretionary purchases.",
        ]
    elif status == "WARNING":
        lines += [
            "WARNING: Spending is close to the budget limit.",
            f"Remaining: Rs. {budget - spent:.2f}",
        ]
    else:
        lines += [
            "OK: Spending is within the planned budget.",
            f"Remaining: Rs. {budget - spent:.2f}",
        ]
    return "\n".join(lines)


def export_report(records, month, config, folder=REPORT_DIR):
    """Write the full report to a text file and return its path."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"report_{month}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_report(records, month, config) + "\n\n")
        f.write(build_category_table(records, month) + "\n\n")
        f.write(build_alert(records, month, config) + "\n")
    return path


def plot_categories(records, month, folder=REPORT_DIR):
    """Save a bar chart of category spending (needs matplotlib)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None, "matplotlib is not installed (pip install matplotlib)."
    totals = category_totals(filter_by_month(records, month))
    if not totals:
        return None, "No data for that month."
    items = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    os.makedirs(folder, exist_ok=True)
    plt.figure(figsize=(7, 4))
    plt.bar([k for k, _ in items], [v for _, v in items])
    plt.title(f"{month} - Category-wise Expenditure")
    plt.ylabel("Amount (Rs.)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    path = os.path.join(folder, f"chart_{month}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path, "Chart saved."


# ------------------------------------------------------------ menu / UI
def ask_month(records):
    months = sorted({r["date"].strftime("%Y-%m") for r in records})
    print("Available months:", ", ".join(months) if months else "none")
    month = input("Enter month (YYYY-MM): ").strip()
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month format.")
        return None
    return month


def menu():
    print("\n===== PERSONAL EXPENSE & BUDGET ANALYZER =====")
    print("1. Add expense")
    print("2. View all expenses")
    print("3. Monthly report")
    print("4. Category analysis")
    print("5. Budget alert")
    print("6. Filter by date range")
    print("7. Month-wise comparison")
    print("8. Export report + chart")
    print("9. Change budget / threshold")
    print("0. Exit")
    return input("Choose an option: ").strip()


def main():
    ensure_sample_data()
    config = load_config()
    while True:
        choice = menu()
        if choice == "0":
            print("Goodbye!")
            break
        if choice == "1":
            print("Categories:", ", ".join(config["categories"]))
            ok, msg = add_expense(
                input("Date (YYYY-MM-DD): "),
                input("Category: "),
                input("Description: "),
                input("Amount (Rs.): "),
            )
            print(msg)
            continue

        records, errors = load_expenses()
        for e in errors:
            print("Data warning:", e)
        if not records:
            print("No valid expense records available.")
            continue

        if choice == "2":
            for r in sorted(records, key=lambda x: x["date"]):
                print(
                    f"{r['date']}  {r['category']:<14}{r['description']:<28}"
                    f"Rs. {r['amount']:.2f}"
                )
        elif choice in {"3", "4", "5", "8"}:
            month = ask_month(records)
            if not month:
                continue
            if choice == "3":
                print(build_report(records, month, config))
            elif choice == "4":
                print(build_category_table(records, month))
            elif choice == "5":
                print(build_alert(records, month, config))
            else:
                print("Report saved to", export_report(records, month, config))
                path, msg = plot_categories(records, month)
                print(msg, path or "")
        elif choice == "6":
            try:
                s = parse_date(input("Start (YYYY-MM-DD): "))
                e = parse_date(input("End (YYYY-MM-DD): "))
            except ValueError:
                print("Invalid date.")
                continue
            sel = filter_by_range(records, s, e)
            print(f"{len(sel)} transactions, total Rs. {total_spent(sel):.2f}")
            for cat, amt in category_totals(sel).items():
                print(f"  {cat:<14}Rs. {amt:.2f}")
        elif choice == "7":
            for m, t in monthly_comparison(records).items():
                status = budget_status(
                    budget_usage(t, config["monthly_budget"]),
                    config["warning_threshold"],
                )
                print(f"{m}: Rs. {t:.2f}  ({status})")
        elif choice == "9":
            try:
                config["monthly_budget"] = float(input("New monthly budget (Rs.): "))
                config["warning_threshold"] = float(input("Warning threshold % (e.g. 80): "))
                if config["monthly_budget"] <= 0 or not 0 < config["warning_threshold"] < 100:
                    raise ValueError
                save_config(config)
                print("Settings saved.")
            except ValueError:
                print("Invalid values. Settings unchanged.")
                config = load_config()
        else:
            print("Invalid choice. Please enter 0-9.")


if __name__ == "__main__":
    main()
