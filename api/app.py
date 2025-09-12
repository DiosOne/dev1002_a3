from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "library_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", ""),
        port=os.getenv("DB_PORT", 5432),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )
    return conn


# --- ROUTES ---


@app.route('/')
def home():
    return jsonify({"message": "Library API is running. Try /books"})

# Read all books
@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Books;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)


# Read one book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Books WHERE BookID = %s;', (book_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Book not found"}), 404


# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    title = data.get('title')
    isbn = data.get('isbn')
    genre = data.get('genre')
    year = data.get('yearpublished')
    authorid = data.get('authorid')

    if not title or not isbn:
        return jsonify({"error": "Title and ISBN are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            '''
            INSERT INTO Books (Title, ISBN, Genre, YearPublished, AuthorID)
            VALUES (%s, %s, %s, %s, %s) RETURNING BookID;
            ''',
            (title, isbn, genre, year, authorid)
        )
        row = cur.fetchone()
        new_id = row[0] if row else None
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

    if new_id:
        return jsonify({"BookID": new_id, "message": "Book created successfully"}), 201
    else:
        return jsonify({"error": "Insert failed"}), 400



# Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    title = data.get('title')
    genre = data.get('genre')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE Books SET Title = %s, Genre = %s WHERE BookID = %s;',
                (title, genre, book_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Book updated successfully"})


# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Books WHERE BookID = %s;', (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Book deleted successfully"})


if __name__ == '__main__':
    # Use port from environment variable for deployed platforms
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

# AUTHORS ENDPOINTS

# Get all authors
@app.route('/authors', methods=['GET'])
def get_authors():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Authors;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# Get one author by ID
@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Authors WHERE AuthorID = %s;', (author_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Author not found"}), 404

# Create an author
@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    name = data.get('name')
    birth_year = data.get('birth_year')

    if not name:
        return jsonify({"error": "Author name is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO Authors (Name, BirthYear) VALUES (%s, %s) RETURNING AuthorID;',
            (name, birth_year)
        )
        row = cur.fetchone()
        new_id = row[0] if row else None
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

    if new_id:
        return jsonify({"AuthorID": new_id, "message": "Author created successfully"}), 201
    else:
        return jsonify({"error": "Insert failed"}), 400

# Update an author
@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    data = request.get_json()
    name = data.get('name')
    birth_year = data.get('birth_year')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE Authors SET Name=%s, BirthYear=%s WHERE AuthorID=%s;',
                (name, birth_year, author_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Author updated successfully"})

# Delete an author
@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Authors WHERE AuthorID=%s;', (author_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Author deleted successfully"})


# MEMBERS ENDPOINTS


# Get all members
@app.route('/members', methods=['GET'])
def get_members():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Members;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# Get one member by ID
@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Members WHERE MemberID=%s;', (member_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Member not found"}), 404

# Create a member
@app.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO Members (Name, Email) VALUES (%s, %s) RETURNING MemberID;',
            (name, email)
        )
        row = cur.fetchone()
        new_id = row[0] if row else None
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

    if new_id:
        return jsonify({"MemberID": new_id, "message": "Member created successfully"}), 201
    else:
        return jsonify({"error": "Insert failed"}), 400

# Update a member
@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE Members SET Name=%s, Email=%s WHERE MemberID=%s;',
                (name, email, member_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Member updated successfully"})

# Delete a member
@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Members WHERE MemberID=%s;', (member_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Member deleted successfully"})


# LOANS / BORROWINGS ENDPOINTS


# Get all loans
@app.route('/loans', methods=['GET'])
def get_loans():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Loans;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# Get one loan by ID
@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Loans WHERE LoanID=%s;', (loan_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Loan not found"}), 404

# Create a loan
@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    book_id = data.get('bookid')
    member_id = data.get('memberid')
    loan_date = data.get('loandate')
    return_date = data.get('returndate')

    if not book_id or not member_id or not loan_date:
        return jsonify({"error": "BookID, MemberID, and LoanDate are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            '''
            INSERT INTO Loans (BookID, MemberID, LoanDate, ReturnDate)
            VALUES (%s, %s, %s, %s) RETURNING LoanID;
            ''',
            (book_id, member_id, loan_date, return_date)
        )
        row = cur.fetchone()
        new_id = row[0] if row else None
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

    if new_id:
        return jsonify({"LoanID": new_id, "message": "Loan created successfully"}), 201
    else:
        return jsonify({"error": "Insert failed"}), 400

# Update a loan
@app.route('/loans/<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    data = request.get_json()
    return_date = data.get('returndate')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE Loans SET ReturnDate=%s WHERE LoanID=%s;',
                (return_date, loan_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Loan updated successfully"})

# Delete a loan
@app.route('/loans/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Loans WHERE LoanID=%s;', (loan_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Loan deleted successfully"})
