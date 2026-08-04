# CMPT354_LibraryDatabase

CMPT 371 A3 Socket Programming Connect-4

Course: CMPT 354 - Database Systems I
Instructor: Ouldooz Baghban Karimi
Semester: Summer 2026

# Project Overview & Description
A library management database built in SQLite, developed through a full six-step pipeline: requirements specification, ER modeling, BCNF/3NF normalization, SQL schema design, sample data population, and a Python CLI application. The schema uses supertype/subtype tables (Item + PrintBook/OnlineBook/Magazine/ScientificJournal/Record) with triggers enforcing type consistency, preventing double-loans, and automatically calculating late fines on return.

The Python application supports:
- **Find** an item in the library by title
- **Borrow** an item (finds an available copy and creates a loan)
- **Return** a borrowed item (closes the loan and assesses a fine if late)
- **Donate** an item to the library (adds it to the catalog and creates a physical copy)
  
# Prerequisites (Fresh Environment)

To run this project, you need:
- Python 3.10 or higher
- Jupyter Notebook or JupyterLab
- No external pip installations required (uses standard `sqlite3` library)

# Step-by-Step Run Guide
Step 1. Clone the repository and open `library.ipynb` in Jupyter.

Step 2. Run the cells in order from the top — this creates `library.db`, builds the schema (tables, constraints, triggers), and populates it with sample data.

Step 3. Once the schema/data cells have run, scroll to the "Build Your Database Application" section and run the `find_item`, `borrow_item`, `return_item`, and `donate_item` function definitions.

Step 4. Call the functions directly in a notebook cell, e.g.:
```python
   find_item("dune")
   borrow_item(memberID=1, itemID=3)
   return_item(loanID=1)
   donate_item("The Fraud", "Ingram", "English", 2023, "PrintBook")

