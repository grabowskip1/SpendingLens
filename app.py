from customtkinter import *
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import categories
from translations import translations

set_appearance_mode("System")
set_default_color_theme("blue")

app = CTk()
app.attributes("-fullscreen", True)
app.title("SpendingLens")

current_language = StringVar(value="EN")

button_frame = CTkFrame(app, fg_color="transparent")
button_frame.place(relx=1.0, rely=0.0, anchor="ne")

exit_button = CTkButton(button_frame, text="✕", width=40, command=app.destroy, fg_color="#383838", hover_color="#282828")
exit_button.grid(row=0, column=1, padx=(0, 10), pady=10)

minimize_button = CTkButton(button_frame, text="—", width=40, command=app.iconify, fg_color="#383838", hover_color="#282828")
minimize_button.grid(row=0, column=0, padx=(0, 5), pady=10)

title_label = CTkLabel(app, text="SpendingLens", font=("Arial", 24))
title_label.pack(pady=20)

current_language = StringVar(master=app)
current_language.set("EN")
sort_descending = BooleanVar(value=False)

df_loaded = None

ORDERED_CATEGORIES = [
    "Groceries", "Food & Drink", "Online Shopping", "Fuel", "Mobile Top-ups",
    "Utilities", "Subscriptions", "Bank Fees", "Fees & Charges", "Health",
    "Peer Transfer", "Bank Transfer", "ATM Withdrawal", "Investments",
    "Transport", "Travel", "Clothing", "Other"
]

GENERIC_TERMS = ["BLIK", "PAYMENT", "ZAPŁATA", "PRZELEW", "OPŁATA", "TRANSAKCJA", "PŁATNOŚĆ", "ZAKUP"]

def t(key):
    return translations[current_language.get()].get(key, key)

def t_cat(key):
    return translations[current_language.get()]["categories"].get(key, key)

def classify_transaction(title):
    title = str(title).upper()
    matches = []

    for category, keywords in categories.CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.upper() in title:
                matches.append((category, keyword))

    if matches:
        for cat, kw in matches:
            if not any(generic in kw.upper() for generic in GENERIC_TERMS):
                return cat
        return matches[0][0]

    return "Other"

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not filepath:
        return

    try:
        df = pd.read_csv(filepath, header=None, sep=",", encoding="utf-8", decimal=",")
    except Exception as e:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("1.0", t("error_loading") + str(e))
        text_box.configure(state="disabled")
        return

    if df.shape[1] < 8:
        text_box.configure(state="normal")
        text_box.delete("1.0", "end")
        text_box.insert("1.0", t("error_columns"))
        text_box.configure(state="disabled")
        return

    columns = ["_", "Date", "Title", "Recipient", "Account", "Amount", "Balance", "Operation"]
    if df.shape[1] > len(columns):
        columns += [f"Extra{i+1}" for i in range(df.shape[1] - len(columns))]
    df.columns = columns
    df.drop(columns=[col for col in df.columns if col.startswith("_") or col.startswith("Extra")], inplace=True, errors="ignore")

    df["Amount"] = df["Amount"].astype(float)
    df["Category"] = df["Title"].apply(classify_transaction)
    df["Type"] = df["Amount"].apply(lambda x: "Income" if x > 0 else "Expense")

    global df_loaded
    df_loaded = df
    update_summary()

def show_category_details():
    if df_loaded is None:
        return

    def open_details():
        translated_to_original = {t_cat(cat): cat for cat in ORDERED_CATEGORIES}
        selected_display = cat_var.get()
        selected = translated_to_original.get(selected_display, selected_display)
        filtered = df_loaded[(df_loaded["Category"] == selected) & (df_loaded["Amount"] < 0)]

        win = CTkToplevel(app)
        win.geometry("800x500")
        win.title(f"{t('details_title')}: {selected_display}")

        box = CTkTextbox(win)
        box.pack(fill="both", expand=True, padx=10, pady=10)

        if filtered.empty:
            box.insert("1.0", "No transactions found.")
        else:
            for _, row in filtered.iterrows():
                box.insert("end", f"{row['Date']} | {row['Amount']} PLN | {row['Title']}\n")

    popup = CTkToplevel(app)
    popup.geometry("300x150")
    popup.title(t("details_title"))

    display_names = [t_cat(cat) for cat in ORDERED_CATEGORIES]
    cat_var = StringVar(value=display_names[0])
    CTkLabel(popup, text=t("details_category_label")).pack(pady=10)
    CTkOptionMenu(popup, values=display_names, variable=cat_var).pack()
    CTkButton(popup, text=t("details_show_button"), command=open_details).pack(pady=10)

def update_summary():
    if df_loaded is None:
        return
    df = df_loaded.copy()

    expenses = df[df["Amount"] < 0].groupby("Category")["Amount"].sum().abs()
    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expense = abs(df[df["Amount"] < 0]["Amount"].sum())
    balance = total_income - total_expense

    filtered_expenses = expenses[expenses > 0]
    if sort_descending.get():
        sorted_expenses = filtered_expenses.sort_values(ascending=False)
    else:
        sorted_expenses = filtered_expenses.reindex(ORDERED_CATEGORIES, fill_value=0)
    sorted_expenses = sorted_expenses[sorted_expenses > 0]

    fig, ax = plt.subplots(figsize=(12, 6))
    translated = [t_cat(cat) for cat in sorted_expenses.index]
    ax.bar(translated, sorted_expenses.values)
    ax.set_title(t("chart_title"))
    ax.set_ylabel(t("chart_y"))
    ax.set_xlabel(t("chart_x"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    for widget in chart_frame.winfo_children():
        widget.destroy()

    top_buttons = CTkFrame(master=chart_frame)
    top_buttons.pack(pady=(0, 5))
    CTkButton(master=top_buttons, text=t("sort_button"), command=toggle_sort).pack(side="left", padx=5)
    CTkButton(master=top_buttons, text=t("details_button"), command=show_category_details).pack(side="left", padx=5)

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    income_label.configure(text=f"{t('income')}: {total_income:.2f} PLN", text_color="green")
    expense_label.configure(text=f"{t('expenses')}: {total_expense:.2f} PLN", text_color="red")
    balance_label.configure(
        text=f"{t('balance')}: {balance:.2f} PLN",
        text_color="green" if balance >= 0 else "red"
    )

    legend = ""
    for cat, val in zip(sorted_expenses.index, sorted_expenses.values):
        legend += f"{t_cat(cat)}: {val:.2f} PLN\n"

    text_box.configure(state="normal")
    text_box.delete("1.0", "end")
    text_box.insert("1.0", legend)
    text_box.configure(state="disabled")

def toggle_sort():
    sort_descending.set(not sort_descending.get())
    update_summary()

def update_ui_labels():
    title_label.configure(text=t("title"))
    upload_button.configure(text=t("upload_button"))
    language_label.configure(text=t("language_label"))
    update_summary()

def safe_exit():
    try:
        app.quit()
        app.destroy()
    except:
        pass
    sys.exit(0)

frame = CTkFrame(master=app)
frame.pack(pady=10, padx=10, fill="both", expand=True)

language_label = CTkLabel(master=frame, text=t("language_label"))
language_label.place(x=20, y=5)

lang_menu = CTkOptionMenu(master=frame, values=["EN", "PL"], variable=current_language, command=lambda _: update_ui_labels())
lang_menu.place(x=20, y=30)

title_label = CTkLabel(master=frame, text=t("title"), font=("Arial", 20))
title_label.pack(pady=(60, 10))

upload_button = CTkButton(master=frame, text=t("upload_button"), command=load_file)
upload_button.pack(pady=10)

content_frame = CTkFrame(master=frame)
content_frame.pack(fill="both", expand=True, padx=20, pady=10)
content_frame.grid_rowconfigure(0, weight=1)
content_frame.grid_columnconfigure(0, weight=1)
content_frame.grid_columnconfigure(1, weight=4)
content_frame.grid_columnconfigure(2, weight=1)

summary_frame = CTkFrame(master=content_frame)
summary_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)

income_label = CTkLabel(master=summary_frame, text="", font=("Arial", 14), anchor="w")
income_label.pack(anchor="w", fill="x")

expense_label = CTkLabel(master=summary_frame, text="", font=("Arial", 14), anchor="w")
expense_label.pack(anchor="w", fill="x")

balance_label = CTkLabel(master=summary_frame, text="", font=("Arial", 14), anchor="w")
balance_label.pack(anchor="w", fill="x")

chart_frame = CTkFrame(master=content_frame)
chart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

legend_frame = CTkFrame(master=content_frame)
legend_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 10), pady=10)

text_box = CTkTextbox(master=legend_frame, wrap="none")
text_box.pack(fill="both", expand=True)
text_box.configure(state="disabled")

app.protocol("WM_DELETE_WINDOW", safe_exit)
app.mainloop()
sys.exit(0)