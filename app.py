import sqlite3

DB = "library.db"


# =========================================================
# Alexis's functions: Item / Copy / Loan / Fine / PotentialItem
# =========================================================

# Find an item in the library
def find_item(title):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = 'SELECT itemID, title, publisher, language, publicationYear, itemType, availability FROM item WHERE title LIKE ?'
    search = f"%{title}%"
    try:
        cursor.execute(query, (search,))
        results = cursor.fetchall()
        if not results:
            print("No matching records.")
            return []
        for row in results:
            print(row)
        return results
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# Borrow an item from the library
def borrow_item(memberID, itemID):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = """SELECT copyNumber from Copy
                WHERE itemID = ?
                AND copyNumber NOT IN (SELECT copyNumber FROM Loan WHERE itemID = ? AND returnDate IS NULL)
                ORDER BY copyNumber
                LIMIT 1"""
    try:
        # business rule: members with unpaid fines may be restricted from borrowing
        cursor.execute(
            """SELECT COUNT(*) FROM Fine f
               JOIN Loan l ON f.loanID = l.loanID
               WHERE l.memberID = ? AND f.paymentStatus = 'Unpaid'""",
            (memberID,)
        )
        unpaid = cursor.fetchone()[0]
        if unpaid > 0:
            print(f"Member {memberID} has {unpaid} unpaid fine(s) and cannot borrow until they are paid.")
            return []

        cursor.execute(query, (itemID, itemID))
        results = cursor.fetchone()
        if not results:
            print("No copies available.")
            return []

        copyNumber = results[0]
        cursor.execute(
            "INSERT INTO Loan (memberID, itemID, copyNumber, dueDate) "
            "VALUES (?, ?, ?, date('now', '+14 days'))",
            (memberID, itemID, copyNumber)
        )
        conn.commit()
        loanID = cursor.lastrowid
        print(f"Borrowed item {itemID} (copy {copyNumber}) for member {memberID}. "
              f"Loan ID {loanID}, due in 14 days.")
        return loanID
    except sqlite3.IntegrityError as e:
        print(f"Could not complete loan: {e}")
        return []
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# Return borrowed item
def return_item(loanID):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = 'SELECT itemID, returnDate FROM Loan WHERE loanID = ?'
    try:
        cursor.execute(query, (loanID,))
        results = cursor.fetchone()
        if not results:
            print("No loan found.")
            return []

        itemID, returnDate = results
        if returnDate is not None:
            print(f"Loan {loanID} was already returned on {returnDate}.")
            return []

        cursor.execute(
            "UPDATE Loan SET returnDate = date('now') WHERE loanID = ?",
            (loanID,)
        )
        conn.commit()

        cursor.execute("SELECT amount FROM Fine WHERE loanID = ?", (loanID,))
        fine = cursor.fetchone()
        if fine:
            print(f"Loan {loanID} returned late. Fine assessed: ${fine[0]:.2f}")
        else:
            print(f"Loan {loanID} returned on time. No fine.")
        return loanID
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# Donate an item to the library
def donate_item(title, publisher, language, publicationYear, itemType, shelfLocation=None):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    valid_types = ["PrintBook", "OnlineBook", "Magazine", "ScientificJournal", "Record"]
    if itemType not in valid_types:
        print(f"Invalid itemType. Must be: {valid_types}")
        conn.close()
        return []
    if itemType != "OnlineBook" and not shelfLocation:
        print("Physical items require a shelfLocation.")
        conn.close()
        return []
    try:
        cursor.execute(
            "INSERT INTO Item (title, publisher, language, publicationYear, itemType) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, publisher, language, publicationYear, itemType)
        )
        itemID = cursor.lastrowid
        cursor.execute(f"INSERT INTO {itemType} (itemID) VALUES (?)", (itemID,))
        if itemType != "OnlineBook":
            cursor.execute(
                "INSERT INTO Copy (itemID, copyNumber, condition) VALUES (?, 1, 'New')",
                (itemID,)
            )
            cursor.execute(
                "INSERT INTO ItemShelf (itemID, shelfLocation) VALUES (?, ?)",
                (itemID, shelfLocation)
            )
        conn.commit()
        print(f"Donated '{title}' as {itemType}. New itemID: {itemID}.")
        return itemID
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Could not complete donation: {e}")
        return []
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# =========================================================
# Hala's functions: Event / Room / AudienceType / Employee
# =========================================================

# Find an event in the library
def find_event(keyword):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = """SELECT eventID, title, eventDate, startTime, endTime, eventType, roomID
               FROM Event WHERE title LIKE ? ORDER BY eventDate, startTime"""
    search = f"%{keyword}%"
    try:
        cursor.execute(query, (search,))
        results = cursor.fetchall()
        if not results:
            print("No matching events.")
            return []
        for row in results:
            print(row)
        return results
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# Register for an event in the library
def register_for_event(memberID, eventID):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT r.capacity FROM Event e
               JOIN Room r ON e.roomID = r.roomID
               WHERE e.eventID = ?""",
            (eventID,)
        )
        room = cursor.fetchone()
        if not room:
            print("No such event.")
            return []
        capacity = room[0]

        cursor.execute(
            "SELECT COUNT(*) FROM EventRegistration WHERE eventID = ?",
            (eventID,)
        )
        current = cursor.fetchone()[0]
        if current >= capacity:
            print("This event is full.")
            return []

        cursor.execute(
            "INSERT INTO EventRegistration (memberID, eventID) VALUES (?, ?)",
            (memberID, eventID)
        )
        conn.commit()
        print(f"Member {memberID} registered for event {eventID}.")
        return (memberID, eventID)
    except sqlite3.IntegrityError as e:
        print(f"Could not complete registration: {e}")
        return []
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# Volunteer for the library
def volunteer_for_library(memberID, interestArea, availability):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Volunteer (
                volunteerID INTEGER PRIMARY KEY AUTOINCREMENT,
                memberID INTEGER NOT NULL,
                interestArea TEXT,
                availability TEXT,
                applicationDate TEXT NOT NULL DEFAULT (date('now')),
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK (status IN ('Pending','Approved','Rejected')),
                FOREIGN KEY (memberID) REFERENCES Member(memberID)
                ON UPDATE CASCADE ON DELETE CASCADE
            )
        """)
        cursor.execute(
            "INSERT INTO Volunteer (memberID, interestArea, availability) VALUES (?, ?, ?)",
            (memberID, interestArea, availability)
        )
        conn.commit()
        volunteerID = cursor.lastrowid
        print(f"Volunteer application submitted (ID {volunteerID}) for member {memberID}.")
        return volunteerID
    except sqlite3.IntegrityError as e:
        print(f"Could not submit volunteer application: {e}")
        return []
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# Ask for help from a librarian
def ask_librarian():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = """SELECT firstName, lastName, email, phone, position
               FROM Employee WHERE position LIKE '%Librarian%'"""
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if not results:
            print("No librarians are currently on staff.")
            return []
        print("You can reach one of the following librarians for help:")
        for row in results:
            print(row)
        return results
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()


# =========================================================
# Menu-driven CLI
# =========================================================

MENU = """
==============================
   Library Database Application
==============================
1. Find an item
2. Borrow an item
3. Return a borrowed item
4. Donate an item
5. Find an event
6. Register for an event
7. Volunteer for the library
8. Ask for help from a librarian
0. Exit
"""


def prompt(label, cast=str, required=True):
    while True:
        val = input(f"{label}: ").strip()
        if not val and not required:
            return None
        if not val and required:
            print("This field is required.")
            continue
        try:
            return cast(val)
        except ValueError:
            print(f"Please enter a valid {cast.__name__}.")


def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            title = prompt("Search by title (partial match ok)")
            find_item(title)

        elif choice == "2":
            memberID = prompt("Member ID", int)
            itemID = prompt("Item ID", int)
            borrow_item(memberID, itemID)

        elif choice == "3":
            loanID = prompt("Loan ID", int)
            return_item(loanID)

        elif choice == "4":
            title = prompt("Title")
            publisher = prompt("Publisher", required=False)
            language = prompt("Language", required=False) or "English"
            year = prompt("Publication year", int, required=False)
            itemType = prompt("Item type (PrintBook/OnlineBook/Magazine/ScientificJournal/Record)")
            shelf = None
            if itemType != "OnlineBook":
                shelf = prompt("Shelf location (e.g. A1-01)")
            donate_item(title, publisher, language, year, itemType, shelf)

        elif choice == "5":
            keyword = prompt("Search by event title (partial match ok)")
            find_event(keyword)

        elif choice == "6":
            memberID = prompt("Member ID", int)
            eventID = prompt("Event ID", int)
            register_for_event(memberID, eventID)

        elif choice == "7":
            memberID = prompt("Member ID", int)
            interestArea = prompt("Interest area (e.g. Children's programs)", required=False)
            availability = prompt("Availability (e.g. Weekday evenings)", required=False)
            volunteer_for_library(memberID, interestArea, availability)

        elif choice == "8":
            ask_librarian()

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option, please choose again.")


if __name__ == "__main__":
    main()
