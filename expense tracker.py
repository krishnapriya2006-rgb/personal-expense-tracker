
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from pathlib import Path
from datetime import date
from collections import defaultdict

FILE = Path(__file__).with_name("expenses.csv")
BUDGET = 5000

# Load existing expenses
def load_expenses():
    if not FILE.exists():
        return []

    with open(FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = []

        for row in reader:
            records.append({
                "Name": row.get("Name", row.get("Expense Name", "")),
                "Amount": row.get("Amount", "0"),
                "Category": row.get("Category", ""),
                "Date": row.get("Date", "")
            })

        return records


expenses = load_expenses()


# Save expenses to CSV
def save_expenses():
    with open(FILE, "w", newline="", encoding="utf-8") as f:
        fields = ["Name", "Amount", "Category", "Date"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(expenses)


# Refresh table and summary
def refresh():
    for item in table.get_children():
        table.delete(item)

    search_text = search_entry.get().lower().strip()

    for index, expense in enumerate(expenses):
        text = (
            expense["Name"] + " " +
            expense["Category"] + " " +
            expense["Date"]
        ).lower()

        if search_text and search_text not in text:
            continue

        table.insert(
            "",
            "end",
            iid=str(index),
            values=(
                expense["Name"],
                expense["Amount"],
                expense["Category"],
                expense["Date"]
            )
        )

    today_month = date.today().strftime("%Y-%m")

    monthly_total = sum(
        float(e["Amount"])
        for e in expenses
        if e["Date"].startswith(today_month)
    )

    remaining = BUDGET - monthly_total

    monthly_label.config(
        text=f"Monthly Expenses: ₹{monthly_total:.2f}"
    )

    budget_label.config(
        text=f"Remaining Budget: ₹{remaining:.2f}",
        fg="green" if remaining >= 0 else "red"
    )


# Add expense

def add_expense():
    name = name_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_box.get().strip()

    if not name or not amount or not category:
        messagebox.showwarning("Warning", "Please fill all fields!")
        return

    try:
        value = float(amount)
        if value <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Amount", "Enter a valid positive amount!")
        return

    expenses.append({
        "Name": name,
        "Amount": str(value),
        "Category": category,
        "Date": date.today().strftime("%Y-%m-%d")
    })

    save_expenses()

    name_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_box.set("")

    refresh()

    messagebox.showinfo("Success", "Expense added successfully!")

    today_month = date.today().strftime("%Y-%m")

    monthly_total = sum(
        float(e["Amount"])
        for e in expenses
        if e["Date"].startswith(today_month)
    )

    if monthly_total >= BUDGET:
        messagebox.showwarning(
            "Budget Alert",
            "Warning! Your monthly budget has been reached or exceeded!"
        )


# Delete selected expense
def delete_expense():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Please select an expense first!"
        )
        return

    index = int(selected[0])

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this expense?"
    )

    if confirm:
        expenses.pop(index)
        save_expenses()
        refresh()

        messagebox.showinfo(
            "Deleted",
            "Expense deleted successfully!"
        )


# Search expenses
def search_expense(event=None):
    refresh()


# Show category-wise pie chart
def show_chart():
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    except ImportError:
        messagebox.showerror(
            "Missing Library",
            "Please install matplotlib using: pip install matplotlib"
        )
        return

    today_month = date.today().strftime("%Y-%m")

    category_totals = defaultdict(float)

    for expense in expenses:
        if expense["Date"].startswith(today_month):
            category_totals[expense["Category"]] += float(
                expense["Amount"]
            )

    if not category_totals:
        messagebox.showinfo(
            "No Data",
            "No expenses recorded this month!"
        )
        return

    chart_window = tk.Toplevel(root)
    chart_window.title("Monthly Expense Pie Chart")
    chart_window.geometry("650x550")

    chart_window.configure(bg="white")

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.pie(
        category_totals.values(),
        labels=category_totals.keys(),
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Monthly Expenses by Category")
    ax.axis("equal")

    canvas = FigureCanvasTkAgg(
        fig,
        master=chart_window
    )

    canvas.draw()
    canvas.get_tk_widget().pack(
        fill=tk.BOTH,
        expand=True
    )

    plt.close(fig)
    
def show_bar_chart():
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    today_month = date.today().strftime("%Y-%m")

    category_totals = defaultdict(float)

    for expense in expenses:
        if expense["Date"].startswith(today_month):
            category_totals[expense["Category"]] += float(
                expense["Amount"]
            )

    if not category_totals:
        messagebox.showinfo(
            "No Data",
            "No expenses recorded this month!"
        )
        return

    chart_window = tk.Toplevel(root)
    chart_window.title("Monthly Expense Bar Chart")
    chart_window.geometry("700x550")

    fig, ax = plt.subplots(figsize=(8, 5))

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    ax.bar(categories, amounts)

    ax.set_title("Monthly Expenses by Category")
    ax.set_xlabel("Expense Categories")
    ax.set_ylabel("Amount (₹)")

    plt.xticks(rotation=30)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(
        fig,
        master=chart_window
    )

    canvas.draw()
    canvas.get_tk_widget().pack(
        fill=tk.BOTH,
        expand=True
    )

    plt.close(fig)



# Main window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("1000x700")
root.configure(bg="#f0f2f5")


# Heading
heading = tk.Label(
    root,
    text="EXPENSE TRACKER",
    font=("Arial", 24, "bold"),
    bg="#f0f2f5",
    fg="#172554"
)
heading.pack(pady=15)


# Input frame
input_frame = tk.Frame(
    root,
    bg="white",
    padx=20,
    pady=15
)
input_frame.pack(fill="x", padx=30, pady=10)


tk.Label(
    input_frame,
    text="Expense Name",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(row=0, column=0, padx=10, pady=5)

tk.Label(
    input_frame,
    text="Amount (₹)",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(row=0, column=1, padx=10, pady=5)

tk.Label(
    input_frame,
    text="Category",
    font=("Arial", 11, "bold"),
    bg="white"
).grid(row=0, column=2, padx=10, pady=5)


name_entry = tk.Entry(
    input_frame,
    width=22,
    font=("Arial", 11)
)
name_entry.grid(row=1, column=0, padx=10, pady=5)


amount_entry = tk.Entry(
    input_frame,
    width=18,
    font=("Arial", 11)
)
amount_entry.grid(row=1, column=1, padx=10, pady=5)


categories = [
    "Food",
    "Transport",
    "Education",
    "Shopping",
    "Entertainment",
    "Medical",
    "Other"
]

category_box = ttk.Combobox(
    input_frame,
    values=categories,
    width=18,
    state="readonly",
    font=("Arial", 11)
)
category_box.grid(row=1, column=2, padx=10, pady=5)


# Buttons
button_frame = tk.Frame(
    input_frame,
    bg="white"
)
button_frame.grid(
    row=2,
    column=0,
    columnspan=3,
    pady=15
)


tk.Button(
    button_frame,
    text="Add Expense",
    command=add_expense,
    bg="#2563eb",
    fg="white",
    font=("Arial", 11, "bold"),
    width=15
).pack(side=tk.LEFT, padx=10)


tk.Button(
    button_frame,
    text="Delete Selected",
    command=delete_expense,
    bg="#dc2626",
    fg="white",
    font=("Arial", 11, "bold"),
    width=17
).pack(side=tk.LEFT, padx=10)


tk.Button(
    button_frame,
    text="View Pie Chart",
    command=show_chart,
    bg="#15803d",
    fg="white",
    font=("Arial", 11, "bold"),
    width=15
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text="View Bar Chart",
    command=show_bar_chart,
    bg="#7c3aed",
    fg="white",
    font=("Arial", 11, "bold"),
    width=15
).pack(side=tk.LEFT, padx=10)


# Search frame
search_frame = tk.Frame(
    root,
    bg="#f0f2f5"
)
search_frame.pack(pady=10)


tk.Label(
    search_frame,
    text="Search:",
    font=("Arial", 12, "bold"),
    bg="#f0f2f5"
).pack(side=tk.LEFT, padx=5)


search_entry = tk.Entry(
    search_frame,
    width=35,
    font=("Arial", 11)
)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind("<KeyRelease>", search_expense)


# Expense table
table_frame = tk.Frame(root)
table_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=10
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical"
)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


table = ttk.Treeview(
    table_frame,
    columns=("Name", "Amount", "Category", "Date"),
    show="headings",
    yscrollcommand=scrollbar.set
)

scrollbar.config(command=table.yview)


table.heading("Name", text="Name")
table.heading("Amount", text="Amount")
table.heading("Category", text="Category")
table.heading("Date", text="Date")


table.column("Name", width=220)
table.column("Amount", width=150)
table.column("Category", width=180)
table.column("Date", width=180)


table.pack(fill="both", expand=True)


# Monthly summary
monthly_label = tk.Label(
    root,
    text="Monthly Expenses: ₹0.00",
    font=("Arial", 16, "bold"),
    bg="#f0f2f5",
    fg="#172554"
)
monthly_label.pack(pady=8)


budget_label = tk.Label(
    root,
    text="Remaining Budget: ₹5000.00",
    font=("Arial", 16, "bold"),
    bg="#f0f2f5",
    fg="green"
)
budget_label.pack(pady=8)


# Display existing records
refresh()


# Run application
root.mainloop()
