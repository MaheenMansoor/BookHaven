from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# File to store book data
DATA_FILE = 'books.json'

# Load existing books from file
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        try:
            books = json.load(f)
        except json.JSONDecodeError:
            books = []
else:
    books = []

def save_books():
    with open(DATA_FILE, 'w') as f:
        json.dump(books, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/library', methods=['GET', 'POST'])
def library():
    if request.method == 'POST':
        # Clear all books
        books.clear()
        save_books()
        flash("All books have been deleted.", "info")
        return redirect(url_for('library'))
    
    return render_template('library.html', books=books)

@app.route('/add', methods=['POST'])
def add_book():
    book_name = request.form['book_name'].strip()
    author_name = request.form['author_name'].strip()

    # Search if the book already exists in the list
    book_exists = False
    for book in books:
        if isinstance(book, dict) and book['book_name'] == book_name and book['author_name'] == author_name:
            book['quantity'] += 1  # If it exists, increase quantity
            book_exists = True
            break

    if not book_exists:
        # Add a new book as a dictionary if it doesn't exist
        books.append({'book_name': book_name, 'author_name': author_name, 'quantity': 1})

    save_books()
    flash("Book added successfully!", "success")
    return redirect(url_for('library'))

@app.route('/delete', methods=['POST'])
def delete_book():
    book_name = request.form['book_name'].strip()
    author_name = request.form['author_name'].strip()

    # Find the book in the list and decrease quantity
    for book in books:
        if isinstance(book, dict) and book['book_name'] == book_name and book['author_name'] == author_name:
            book['quantity'] -= 1
            if book['quantity'] <= 0:
                books.remove(book)  # Remove the book from the list if quantity is 0
            break

    save_books()
    flash("Book deleted successfully!", "success")
    return redirect(url_for('library'))

@app.route('/rent', methods=['GET', 'POST'])
def rent():
    book_name = ""
    author_name =""
    success_message = None
    available = False

    if request.method == 'POST':
        if 'student_name' in request.form:  # Renting
            book_name = request.form['book_name'].strip()
            author_name = request.form['author_name'].strip()

            # Find the book in the list
            for book in books:
                if isinstance(book, dict) and book['book_name'] == book_name and book['author_name'] == author_name:
                    if book['quantity'] > 0:
                        book['quantity'] -= 1
                        save_books()
                        success_message = "Book rented successfully!"
                        break
                    else:
                        flash("Book is not available now. Please choose another book.", "error")
                    break
        else:
            book_name = request.form['book_name'].strip()
            author_name = request.form['author_name'].strip()

            # Check if the book is available
            for book in books:
                if isinstance(book, dict) and book['book_name'] == book_name and book['author_name'] == author_name:
                    if book['quantity'] > 0:
                        available = True
                    else:
                        flash("Book is not available now. Please choose another book.", "error")
                    break

    return render_template('rent.html', book_name=book_name, author_name=author_name, success_message=success_message, available=available)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term'].strip().lower()
        search_results = {i: book for i, book in enumerate(books) if search_term in book['book_name'].lower()}
        return render_template('search.html', results=search_results)
    return render_template('search.html', results={})

if __name__ == '__main__':
    app.run(debug=True)