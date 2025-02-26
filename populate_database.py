import pymysql
import random
from faker import Faker
from datetime import timedelta, datetime

fake = Faker()

def random_date(start, end):
    """Generate a random date between `start` and `end`."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def connect_db():
    """Establishes a connection to the database."""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="agera9118JEE",
        db="Library",
        cursorclass=pymysql.cursors.DictCursor
    )

def populate_employees(cursor, num=10):
    """Populates the Employee table."""
    for _ in range(num):
        emp_id = fake.unique.bothify(text='EMP######')
        first_name = fake.first_name()
        last_name = fake.last_name()
        joining_date = fake.date_between(start_date='-5y', end_date='today')
        # Assign a manager randomly from existing employees or None
        cursor.execute("SELECT emp_ID FROM Employee")
        existing_employees = [item['emp_ID'] for item in cursor.fetchall()]
        manager_id = random.choice(existing_employees) if existing_employees and random.choice([True, False]) else None
        job_desc = fake.sentence(nb_words=6)
        cursor.execute("""
            INSERT INTO Employee (emp_ID, first_name, last_name, joining_date, manager, job_desc)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (emp_id, first_name, last_name, joining_date, manager_id, job_desc))

def populate_members(cursor, num=10):
    """Populates the Member table."""
    cursor.execute("SELECT emp_ID FROM Employee")
    employee_ids = [item['emp_ID'] for item in cursor.fetchall()]
    for _ in range(num):
        member_id = fake.unique.bothify(text='MEM######')
        assigned_emp = random.choice(employee_ids)
        family_members = random.randint(1, 5)
        city = fake.city()
        mobile_no = fake.unique.bothify(text='##########')  # Assuming 10-digit mobile number
        joining_date = fake.date_between(start_date='-5y', end_date='today')
        fine = random.randint(0, 50)
        expiry = random_date(joining_date, joining_date + timedelta(days=365))
        first_name = fake.first_name()
        last_name = fake.last_name()
        cursor.execute("""
            INSERT INTO Member (member_ID, assigned_emp, family_members, city, mobile_no, joining_date, fine, expiry, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (member_id, assigned_emp, family_members, city, mobile_no, joining_date, fine, expiry, first_name, last_name))

def populate_publishers(cursor, num=5):
    """Populates the Publisher table."""
    for _ in range(num):
        pub_id = fake.unique.bothify(text='PUB######')
        address = fake.address().replace('\n', ', ')
        name = fake.company()
        cursor.execute("""
            INSERT INTO Publisher (pub_ID, address, name)
            VALUES (%s, %s, %s)
        """, (pub_id, address, name))

def populate_suppliers(cursor, num=5):
    """Populates the Supplier table."""
    for _ in range(num):
        supplier_id = fake.unique.bothify(text='SUP######')
        name = fake.company()
        address = fake.address().replace('\n', ', ')
        cursor.execute("""
            INSERT INTO Supplier (supplier_ID, name, address)
            VALUES (%s, %s, %s)
        """, (supplier_id, name, address))

def populate_books(cursor, num=20):
    """Populates the Books table."""
    cursor.execute("SELECT pub_ID FROM Publisher")
    publisher_ids = [item['pub_ID'] for item in cursor.fetchall()]
    cursor.execute("SELECT supplier_ID FROM Supplier")
    supplier_ids = [item['supplier_ID'] for item in cursor.fetchall()]
    for _ in range(num):
        book_id = fake.unique.bothify(text='BK###')
        author = fake.name()
        pub_id = random.choice(publisher_ids)
        title = fake.sentence(nb_words=4).rstrip('.')
        genre = random.choice(['Fiction', 'Non-fiction', 'Science', 'History', 'Biography'])
        supplier_id = random.choice(supplier_ids)
        cursor.execute("""
            INSERT INTO Books (book_ID, author, pub_ID, title, genre, supplier_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (book_id, author, pub_id, title, genre, supplier_id))

def populate_book_copies(cursor, num=50):
    """Populates the book_copies table."""
    cursor.execute("SELECT book_ID FROM Books")
    book_ids = [item['book_ID'] for item in cursor.fetchall()]
    for _ in range(num):
        copy_id = fake.unique.bothify(text='CP###')
        book_id = random.choice(book_ids)
        edition = random.randint(1, 5)
        available = 'YES'
        book_rack = random.randint(1, 20)
        cursor.execute("""
            INSERT INTO book_copies (copy_ID, book_ID, edition, available, book_rack)
            VALUES (%s, %s, %s, %s, %s)
        """, (copy_id, book_id, edition, available, book_rack))

def populate_issues(cursor, num=20):
    """Populates the Issues table."""
    cursor.execute("SELECT member_ID FROM Member")
    member_ids = [item['member_ID'] for item in cursor.fetchall()]
    cursor.execute("SELECT copy_ID FROM book_copies WHERE available = 'YES'")
    available_copies = [item['copy_ID'] for item in cursor.fetchall()]
    for _ in range(num):
        if not available_copies:
            break  # No available copies to issue
        issue_id = fake.unique.bothify(text='ISD######')
        copy_id = random.choice(available_copies)
        member_id = random.choice(member_ids)
        borrow_date = fake.date_between(start_date='-1y', end_date='today')
        return_date = borrow_date + timedelta(days=30)
        fine = 0
        cursor.execute("""
            INSERT INTO Issues (issue_ID, copy_ID, member_ID, borrow_date, return_date, fine)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (issue_id, copy_id, member_id, borrow_date, return_date, fine))
        # Update availability
        cursor.execute("UPDATE book_copies SET available = 'NO' WHERE copy_ID = %s", (copy_id,))
        available_copies.remove(copy_id)

def populate_borrowed_by(cursor):
    """Populates the Borrowed_by table based on existing Issues."""
    cursor.execute("SELECT issue_ID, member_ID FROM Issues")
    issues = cursor.fetchall()
    for issue in issues:
        issue_id = issue['issue_ID']
        member_id = issue['member_ID']
        cursor.execute("""
            INSERT INTO Borrowed_by (issue_id, member_id)
            VALUES (%s, %s)
        """, (issue_id, member_id))

def main():
    db_conn = connect_db()
    cursor = db_conn.cursor()
    try:
        populate_employees(cursor, num=10)
        populate_members(cursor, num=15)
        populate_publishers(cursor, num=5)
        populate_suppliers(cursor, num=5)
        populate_books(cursor, num=20)
        populate_book_copies(cursor, num=50)
        populate_issues(cursor, num=20)
        populate_borrowed_by(cursor)  # Populate Borrowed_by after Issues
        db_conn.commit()
        print("Database populated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db_conn.rollback()
    finally:
        cursor.close()
        db_conn.close()

if __name__ == "__main__":
    main()
