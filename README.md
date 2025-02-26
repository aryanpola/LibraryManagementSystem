
# Library Management System

A comprehensive database-driven application for managing a library's operations, including member management, book inventory, borrowing, and employee tracking.

## Overview

This Library Management System provides a complete solution for libraries to:
- Manage book inventory and copies
- Track member information and borrowing history
- Handle employee records and assignments
- Process book issues and returns
- Manage publishers and suppliers

## System Requirements

- Python 3.7+
- MySQL Server
- Web browser (for future frontend integration)

## Installation and Setup

1. **Clone the repository**

```bash
git clone https://github.com/aryanpola/library-management-system.git
cd library-management-system
```

2. **Install required dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up the database**

Update the database credentials in create_database.py, populate_database.py, and sever.py if needed:

```python
host="localhost"
user="root"
password="your-password"
```

4. **Create database schema**

```bash
python create_database.py
```

5. **Populate the database with sample data**

```bash
python populate_database.py
```

6. **Start the Flask server**

```bash
python sever.py
```

The API server will start on http://localhost:5000

## Database Structure

The system uses the following tables:

- **Employee**: Staff information and hierarchy
- **Member**: Library members and their details
- **Books**: Book catalog information
- **book_copies**: Individual copies of each book
- **Publisher**: Book publisher information
- **Supplier**: Book supplier details
- **Issues**: Book borrowing records
- **Borrowed_by**: Relationship between members and issued books

## API Endpoints

### Members
- `GET /members` - List all members
- `POST /members` - Add a new member
- `GET /members/books/<member_id>` - Get books issued to a member

### Books
- `GET /books` - List all books
- `POST /books` - Add a new book

### Issues
- `POST /issue_book` - Issue a book to a member

## Project Structure

- create_database.py: Creates the MySQL database and tables
- populate_database.py: Seeds the database with sample data using Faker
- sever.py: Flask API server with endpoints
- requirements.txt: Python package dependencies

## Database Features

The system implements:
- Stored procedures for common operations
- Triggers to:
  - Check book availability before issuance
  - Verify member has no outstanding fines
  - Update book availability status automatically

## Usage Examples

### Adding a new member
```bash
curl -X POST http://localhost:5000/members \
  -H "Content-Type: application/json" \
  -d '{"member_ID":"MEM123456","first_name":"John","last_name":"Doe","city":"New York"}'
```

### Issuing a book
```bash
curl -X POST http://localhost:5000/issue_book \
  -H "Content-Type: application/json" \
  -d '{"member_id":"MEM123456","copy_id":"CP123"}'
```

## Future Enhancements

- Frontend user interface
- Book return functionality
- Fine calculation and payment system
- Search functionality
- Reports and analytics dashboard

---

*This project was created as a database management system demonstration.*
