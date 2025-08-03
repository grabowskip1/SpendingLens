# 💸 SpendingLens – Polish Bank Expense Analyzer

SpendingLens is a full-featured desktop application written in Python that analyzes your expenses based on your Santander Bank Polska transaction history (CSV export).

It categorizes your transactions using Polish keyword matching (store names, services, etc.), calculates summaries, and presents your data in a clean, interactive interface.

---

## Features

- Visualizes your expenses by category using a bar chart
- Automatically detects and classifies merchants (Żabka, Biedronka, Bolt, Rossmann, etc.)
- Lets you inspect each category in detail with individual transaction history
- Dual language support: English 🇬🇧 / Polish 🇵🇱
- Sorts categories by spending amount
- Balance summary: total income, total expenses, and net balance
- Modern fullscreen GUI using `customtkinter`
- Fully offline — your financial data never leaves your machine

---

## Requirements

- Python 3.10+
- Required libraries:
  - `pandas`
  - `matplotlib`
  - `customtkinter`

---

## How to Use

1. Export your transaction history as a CSV file from **Santander Bank Polska**
2. Run the application:
3. Upload your CSV file when prompted
4. View breakdown by category, inspect your spending, and track your balance

---

## ❗ Important Note

> This app is tailored for **Polish bank data** and specifically supports **Santander Bank Polska CSV exports**.  
> It uses Polish-specific merchant keywords, so results may be inaccurate or empty with other banks or countries.

---

## Interface Overview

- Bar chart showing categorized spending
- Income, Expenses, and Balance displayed on the left
- Legend with totals for each category on the right
- “Show Details” button to view a breakdown of each category's transactions
- Optional sorting from highest to lowest category spend
- Language switch in the top left

---

## File Structure

```

SpendingLens/
├── app.py              # Main application logic
├── categories.py       # Category definitions and keyword mappings
├── translations.py     # Language translations (EN/PL)

```
## Privacy & Security

SpendingLens processes data **entirely offline**.  
No third-party services, no data collection — **100% local** analysis.

---

## Known Issues

- On rare occasions, closing the app might trigger background Tkinter errors in the console.
  This does **not** affect functionality or data.
