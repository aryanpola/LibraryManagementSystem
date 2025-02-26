import pymysql

db_connection = pymysql.connect(
    host="localhost",
    user="root",
    password="agera9118JEE",
    cursorclass=pymysql.cursors.DictCursor
)

# Create a cursor object to interact with the database
cursor = db_connection.cursor()

# Create the Library database
cursor.execute("CREATE DATABASE IF NOT EXISTS Library")

# Use the Library database
cursor.execute("USE Library")

# Create tables
tables_queries = [
    # Create Employee table
    """CREATE TABLE IF NOT EXISTS Employee (
        emp_ID CHAR(10) PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        joining_date DATE,
        manager CHAR(10),
        job_desc VARCHAR(500),
        FOREIGN KEY (manager) REFERENCES Employee(emp_ID)
    )""",
    # Create Member table
    """CREATE TABLE IF NOT EXISTS Member (
        member_ID CHAR(10) PRIMARY KEY,
        assigned_emp CHAR(10),
        family_members INT,
        city VARCHAR(50),
        mobile_no CHAR(10),
        joining_date DATE,
        fine INT,
        expiry DATE,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        FOREIGN KEY (assigned_emp) REFERENCES Employee(emp_ID)
    )""",
    # Create book_copies table
    """CREATE TABLE IF NOT EXISTS book_copies (
        copy_ID CHAR(5) PRIMARY KEY,
        book_ID CHAR(5),
        edition INT,
        available VARCHAR(3),
        book_rack INT
    )""",
    # Create Issues table
    """CREATE TABLE IF NOT EXISTS Issues (
        issue_ID CHAR(10) PRIMARY KEY,
        copy_ID CHAR(5),
        member_ID CHAR(10),
        borrow_date DATE,
        return_date DATE,
        fine INT,
        FOREIGN KEY (member_ID) REFERENCES Member(member_ID),
        FOREIGN KEY (copy_ID) REFERENCES book_copies(copy_ID)
    )""",
    # Create Borrowed_by table
    """CREATE TABLE IF NOT EXISTS Borrowed_by (
        issue_id CHAR(10),
        member_id CHAR(10),
        FOREIGN KEY (issue_id) REFERENCES Issues(issue_ID),
        FOREIGN KEY (member_id) REFERENCES Member(member_ID),
        PRIMARY KEY (issue_id, member_id)
    )""",
    # Create Publisher table
    """CREATE TABLE IF NOT EXISTS Publisher (
        pub_ID CHAR(10) PRIMARY KEY,
        address VARCHAR(300),
        name VARCHAR(100)
    )""",
    # Create Supplier table
    """CREATE TABLE IF NOT EXISTS Supplier (
        supplier_ID CHAR(10) PRIMARY KEY,
        name VARCHAR(50),
        address VARCHAR(300)
    )""",
    # Create Books table
    """CREATE TABLE IF NOT EXISTS Books (
        book_ID CHAR(5),
        author VARCHAR(50),
        pub_ID CHAR(10),
        title VARCHAR(200),
        genre VARCHAR(50),
        supplier_ID CHAR(10),
        FOREIGN KEY (pub_ID) REFERENCES Publisher(pub_ID),
        FOREIGN KEY (supplier_ID) REFERENCES Supplier(supplier_ID),
        PRIMARY KEY (book_ID)
    )"""
]

# Execute table creation queries
for query in tables_queries:
    cursor.execute(query)

# Commit changes and close connection
db_connection.commit()
db_connection.close()
