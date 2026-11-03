
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# ---------------- DATABASE ----------------

conn = sqlite3.connect("expenses.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    expense_date TEXT NOT NULL,
    expense_time TEXT NOT NULL
)
""")

conn.commit()


# ---------------- FUNCTIONS ----------------

def add_expense(amount, category, description):

    now = datetime.now()

    cursor.execute("""
    INSERT INTO expenses
    (amount, category, description, expense_date, expense_time)
    VALUES (?, ?, ?, ?, ?)
    """, (
        amount,
        category,
        description,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S")
    ))

    conn.commit()


def get_expenses():

    return pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY id DESC",
        conn
    )


def get_daily_total():

    today = date.today().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT SUM(amount) FROM expenses
    WHERE expense_date = ?
    """, (today,))

    return cursor.fetchone()[0] or 0


def get_monthly_total():

    month = date.today().strftime("%Y-%m")

    cursor.execute("""
    SELECT SUM(amount) FROM expenses
    WHERE expense_date LIKE ?
    """, (month + "%",))

    return cursor.fetchone()[0] or 0


def delete_expense(expense_id):

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()


# ---------------- INTERFACE ----------------

st.set_page_config(
    page_title="Daily Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Daily Expense Tracker")
st.caption("Track your money. Understand your spending.")

# Dashboard

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Today's Expenses",
        f"Rs. {get_daily_total():,.2f}"
    )

with col2:
    st.metric(
        "This Month",
        f"Rs. {get_monthly_total():,.2f}"
    )

st.divider()


# ---------------- ADD EXPENSE ----------------

st.subheader("➕ Add New Expense")

with st.form("expense_form"):

    amount = st.number_input(
        "Amount (Rs.)",
        min_value=1.0,
        step=50.0
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Education",
            "Shopping",
            "Entertainment",
            "Bills",
            "Health",
            "Other"
        ]
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch at university"
    )

    submitted = st.form_submit_button(
        "Save Expense"
    )

    if submitted:

        add_expense(
            amount,
            category,
            description
        )

        st.success("Expense saved successfully!")
        st.rerun()


st.divider()


# ---------------- EXPENSE HISTORY ----------------

st.subheader("📜 Expense History")

df = get_expenses()

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Expense History (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="expense_history.csv",
        mime="text/csv"
    )

else:

    st.info("No expenses recorded yet.")


st.divider()


# ---------------- CATEGORY ANALYSIS ----------------

st.subheader("📊 Spending Analysis")

if not df.empty:

    category_data = df.groupby(
        "category"
    )["amount"].sum()

    st.bar_chart(category_data)

    st.subheader("Category-wise Spending")

    st.dataframe(
        category_data.reset_index(),
        use_container_width=True,
        hide_index=True
    )


# ---------------- DELETE EXPENSE ----------------

st.divider()

st.subheader("🗑️ Delete Expense")

if not df.empty:

    selected_id = st.selectbox(
        "Select Expense ID",
        df["id"].tolist()
    )

    if st.button("Delete Selected Expense"):

        delete_expense(selected_id)

        st.success("Expense deleted successfully!")
        st.rerun()

else:

    st.info("There are no expenses to delete.")
