from flask import Flask, request, jsonify
import pymysql.cursors
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_cors import CORS
app = Flask(__name__)
CORS
# Database connection function
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='agera9118JEE',
        db='Library',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Create stored procedures and triggers
def create_procedures_and_triggers():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Create Procedures
        cursor.execute("DROP PROCEDURE IF EXISTS AddNewMember;")
        cursor.execute("""
        CREATE PROCEDURE AddNewMember(
            IN memID CHAR(10), 
            IN fName VARCHAR(50), 
            IN lName VARCHAR(50), 
            IN cty VARCHAR(50)
        )
        BEGIN
            INSERT INTO Member (member_ID, first_name, last_name, city)
            VALUES (memID, fName, lName, cty);
        END;
        """)

        cursor.execute("DROP PROCEDURE IF EXISTS AddNewBook;")
        cursor.execute("""
        CREATE PROCEDURE AddNewBook(
            IN bID CHAR(5),
            IN auth VARCHAR(50), 
            IN ttl VARCHAR(200), 
            IN gnr VARCHAR(50)
        )
        BEGIN
            INSERT INTO Books (book_ID, author, title, genre)
            VALUES (bID, auth, ttl, gnr);
        END;
        """)


        # Create Triggers
        cursor.execute("DROP TRIGGER IF EXISTS check_book_availability;")
        cursor.execute("""
        CREATE TRIGGER check_book_availability               
        BEFORE INSERT ON Issues
        FOR EACH ROW
        BEGIN
            DECLARE available_status VARCHAR(3);
            SELECT available INTO available_status FROM book_copies WHERE copy_ID = NEW.copy_ID;
            IF available_status != 'YES' THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This book is not available for issuing.';
            END IF;
        END;
        """)

        cursor.execute("DROP TRIGGER IF EXISTS check_fines_before_issue;")
        cursor.execute("""
        CREATE TRIGGER check_fines_before_issue
        BEFORE INSERT ON Issues
        FOR EACH ROW
        BEGIN
            DECLARE outstanding_fines INT;
            SELECT fine INTO outstanding_fines FROM Member WHERE member_ID = NEW.member_ID;
            IF outstanding_fines > 0 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This member has outstanding fines.';
            END IF;
        END;
        """)

        cursor.execute("DROP TRIGGER IF EXISTS update_availability_after_issue;")
        cursor.execute("""
        CREATE TRIGGER update_availability_after_issue
        AFTER INSERT ON Issues
        FOR EACH ROW
        BEGIN
            UPDATE book_copies
            SET available = 'NO'
            WHERE copy_ID = NEW.copy_ID;
        END;
        """)

        connection.commit()
        print("Procedures and triggers created successfully.")
    except Exception as e:
        print("Error creating procedures and triggers:", e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

create_procedures_and_triggers()

# API Routes

@app.route("/issue_book", methods=['POST'])
def issue_book():
    data = request.json
    member_id = data.get('member_id')
    copy_id = data.get('copy_id')

    if not member_id or not copy_id:
        return {"message": "Missing member_id or copy_id"}, 400

    current_date = datetime.now()
    borrow_date = current_date.strftime('%Y-%m-%d')
    return_date = (current_date + relativedelta(months=+1)).strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the book copy is available
        cursor.execute("SELECT available FROM book_copies WHERE copy_ID = %s", (copy_id,))
        availability = cursor.fetchone()

        if availability and availability['available'] == 'YES':
            # Generate a new issue_ID
            cursor.execute("SELECT COUNT(*) AS count FROM Issues")
            count = cursor.fetchone()['count'] + 1
            new_issue_id = f"ISD{count:07d}"  # e.g., ISD0000001

            # Insert into Issues table using triggers
            cursor.execute("""
                INSERT INTO Issues (issue_ID, copy_ID, member_ID, borrow_date, return_date, fine)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, (new_issue_id, copy_id, member_id, borrow_date, return_date))

            conn.commit()
            return {"message": "Book issued successfully"}, 201
        else:
            return {"message": "Book not available"}, 400
    except pymysql.err.InternalError as ie:
        # This captures the SIGNAL from triggers
        return {"message": ie.args[1]}, 400
    except Exception as e:
        print("Error issuing book:", e)
        return {"message": "An error occurred"}, 500
    finally:
        cursor.close()
        conn.close()

@app.route("/members", methods=['GET'])
def get_members():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Member")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"members": members})

@app.route("/members", methods=['POST'])
def add_member():
    new_member = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('AddNewMember', [
            new_member['member_ID'], 
            new_member['first_name'], 
            new_member['last_name'], 
            new_member['city']
        ])
        conn.commit()
        return {"message": "Member added successfully"}, 201
    except Exception as e:
        print("Error adding member:", e)
        return {"message": "An error occurred"}, 500
    finally:
        cursor.close()
        conn.close()

@app.route("/books", methods=['POST'])
def add_book():
    new_book = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('AddNewBook', [
            new_book['book_ID'], 
            new_book['author'], 
            new_book['title'], 
            new_book['genre']
        ])
        conn.commit()
        return {"message": "Book added successfully"}, 201
    except Exception as e:
        print("Error adding book:", e)
        return {"message": "An error occurred"}, 500
    finally:
        cursor.close()
        conn.close()

@app.route("/books", methods=['GET'])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"books": books})

@app.route("/members/books/<member_id>", methods=['GET'])
def get_member_books(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT b.title, b.author, i.borrow_date, i.return_date
        FROM Books b
        JOIN book_copies bc ON b.book_ID = bc.book_ID
        JOIN Issues i ON bc.copy_ID = i.copy_ID
        WHERE i.member_ID = %s
        """, (member_id,))
        books = cursor.fetchall()
        return jsonify({"books": books})
    except Exception as e:
        print("Error fetching member books:", e)
        return {"message": "An error occurred"}, 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
