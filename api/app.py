from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Database connection ---
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

def query_db(query, params=None, one=False, commit=False):
    """
    Run a DB query safely.
    - one=True returns a single row
    - commit=True commits changes
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params or ())
        if commit:
            conn.commit()
        if one:
            return cur.fetchone()
        return cur.fetchall()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# --- Helpers ---
def clean_str(value: str | None) -> str | None:
    return value.strip() if value else None

def rows_to_dicts(cursor):
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def row_to_dict(cursor, row):
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row)) if row else None

def validate_book_data(data, require_all=False):
    """
    Validate book data for POST/PUT.
    Returns a list of errors (empty if no errors).
    if require_all=True, all fields must vbe completed
    """
    errors = []

    # Safely get and strip string fields
    title = (data.get("title") or "").strip()
    isbn = (data.get("isbn") or "").strip()
    genre = (data.get("genre") or "").strip()
    year = data.get("yearpublished")
    authorid = data.get("authorid")

    #if require_all, all fields must exist.
    if require_all:
        if not all([title, isbn, genre, year, authorid]):
            errors.append("All fields must be provided; title, isbn, genre, yearpublished, authorId.")
            
    # Title validation
    if not title:
        errors.append("Title is required.")
    elif len(title) > 255:
        errors.append("Title too long (max 255 chars).")

    # ISBN validation
    if not isbn:
        errors.append("ISBN is required.")
    elif len(isbn) > 13:
        errors.append("ISBN too long (max 13 chars).")

    # YearPublished validation
    if year is not None:
        try:
            year = int(year)
            if year < 0 or year > 2100:
                errors.append("YearPublished must be a valid year.")
        except ValueError:
            errors.append("YearPublished must be an integer.")

    # AuthorID validation
    if authorid is not None:
        try:
            int(authorid)
        except ValueError:
            errors.append("AuthorID must be an integer.")

    return errors





# --- ROUTES ---
@app.route('/')
def home():
    return jsonify({"message": "Library API is running. Try /books, /authors, /loans, /members"})

# --- BOOKS ---
@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Books;')
    rows = rows_to_dicts(cur)
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Books WHERE BookID = %s;', (book_id,))
    row = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Book not found"}), 404

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()

    errors = validate_book_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        row = query_db(
            '''
            INSERT INTO Books (Title, ISBN, Genre, YearPublished, AuthorID)
            VALUES (%s, %s, %s, %s, %s) RETURNING BookID;
            ''',
            (data.get("title"), data.get("isbn"), data.get("genre"),
             data.get("yearpublished"), data.get("authorid")),
            one=True, commit=True
        )
        new_id = row[0] if row else None
        return jsonify({"BookID": new_id, "message": "Book created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()

    # Require all fields for PUT
    errors = validate_book_data(data, require_all=True)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        query_db(
            '''
            UPDATE Books
            SET Title=%s, ISBN=%s, Genre=%s, YearPublished=%s, AuthorID=%s
            WHERE BookID=%s;
            ''',
            (data["title"], data["isbn"], data["genre"], data["yearpublished"], data["authorid"], book_id),
            commit=True
        )
        return jsonify({"message": f"Book {book_id} updated successfully"})
    except Exception as e:
        app.logger.error(f"Internal error updating book {book_id}: {str(e)}")  # internal log
        return jsonify({"error": "An internal error occurred"}), 500


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        query_db('DELETE FROM Books WHERE BookID = %s;', (book_id,), commit=True)
        return jsonify({"message": f"Book {book_id} deleted successfully"})
    except Exception as e:
        app.logger.error(f"Internal error deleting book {book_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400


# --- AUTHORS ---
@app.route('/authors', methods=['GET'])
def get_authors():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Authors;')
    rows = rows_to_dicts(cur)
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Authors WHERE AuthorID = %s;', (author_id,))
    row = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Author not found"}), 404

@app.route('/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    name = clean_str(data.get('name'))
    birth_year = data.get('birth_year')

    if not name:
        return jsonify({"error": "Author name is required"}), 400

    
    try:
        row = query_db(
            'INSERT INTO Authors (Name, BirthYear) VALUES (%s, %s) RETURNING AuthorID;',
            (name, birth_year),
            one=True, commit=True
        )
        new_id = row[0] if row else None
        return jsonify({"AuthorID": new_id, "message": f"Author {new_id} added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    data = request.get_json()
    name = clean_str(data.get('name'))
    birth_year = data.get('birth_year')

    if not name or birth_year is None:
        return jsonify({"error": "Please input all information"}), 400

    try:
        row = query_db(
            'UPDATE Authors SET Name=%s, BirthYear=%s WHERE AuthorID=%s RETURNING AuthorID;',
            (name, birth_year, author_id),
            one=True, commit=True
        )
        if row:
            return jsonify({"message": f"Author {author_id} updated successfully"})
        return jsonify({"error": "Author not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    try:
        row = query_db(
            'DELETE FROM Authors WHERE AuthorID=%s RETURNING AuthorID;',
            (author_id,), one=True, commit=True
        )
        if row:
            return jsonify({"message": f"Author {author_id} deleted successfully"})
        return jsonify({"error": "Author not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- MEMBERS ---
@app.route('/members', methods=['GET'])
def get_members():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Members;')
    rows = rows_to_dicts(cur)
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Members WHERE MemberID=%s;', (member_id,))
    row = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Member not found"}), 404

@app.route('/members', methods=['POST'])
def create_member():
    data = request.get_json()
    name = clean_str(data.get('name'))
    email = clean_str(data.get('email'))

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    try:
        row = query_db(
            'INSERT INTO Members (Name, Email) VALUES (%s, %s) RETURNING MemberID;',
            (name, email), one=True, commit=True
        )
        new_id = row[0] if row else None
        return jsonify({"MemberID": new_id, "message": f"Member {new_id} added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    name = clean_str(data.get('name'))
    email = clean_str(data.get('email'))

    try:
        row = query_db(
            'UPDATE Members SET Name=%s, Email=%s WHERE MemberID=%s RETURNING MemberID;',
            (name, email, member_id), one=True, commit=True
        )
        if row:
            return jsonify({"message": f"Member {member_id} updated successfully"})
        return jsonify({"error": "Member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        row = query_db(
            'DELETE FROM Members WHERE MemberID=%s RETURNING MemberID;',
            (member_id,), one=True, commit=True
        )
        if row:
            return jsonify({"message": f"Member {member_id} deleted successfully"})
        return jsonify({"error": "Member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- LOANS ---
@app.route('/loans', methods=['GET'])
def get_loans():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Loans;')
    rows = rows_to_dicts(cur)
    cur.close()
    conn.close()
    
    if not rows:
        return jsonify({"message": "No current loans"}), 200
    
    return jsonify(rows)

@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Loans WHERE LoanID=%s;', (loan_id,))
    row = row_to_dict(cur, cur.fetchone())
    cur.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Loan not found"}), 404

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    book_id = data.get('bookid')
    member_id = data.get('memberid')
    loan_date = data.get('loandate')
    return_date = data.get('returndate')

    if not book_id or not member_id or not loan_date:
        return jsonify({"error": "BookID, MemberID, and LoanDate are required"}), 400

    try:
        row = query_db(
            'INSERT INTO Loans (BookID, MemberID, LoanDate, ReturnDate) VALUES (%s, %s, %s, %s) RETURNING LoanID;',
            (book_id, member_id, loan_date, return_date), one=True, commit=True
        )
        new_id = row[0] if row else None
        return jsonify({"LoanID": new_id, "message": f"Loan {new_id} added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/loans/<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    data = request.get_json()
    return_date = data.get('returndate')

    if not return_date:
        return jsonify({"error": "Please input all information"}), 400

    try:
        row = query_db(
            'UPDATE Loans SET ReturnDate=%s WHERE LoanID=%s RETURNING LoanID;',
            (return_date, loan_id), one=True, commit=True
        )
        if row:
            return jsonify({"message": f"Loan {loan_id} updated successfully"})
        return jsonify({"error": "Loan not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/loans/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    try:
        row = query_db(
            'DELETE FROM Loans WHERE LoanID=%s RETURNING LoanID;',
            (loan_id,), one=True, commit=True
        )
        if row:
            return jsonify({"message": f"Loan {loan_id} deleted successfully"})
        return jsonify({"error": "Loan not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- GLOBAL ERROR HANDLING ---

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({
        "error": "Resource not found",
        "message": "The requested URL or resource does not exist."
    }), 404


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500

# --- MAIN ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False") == "True"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
