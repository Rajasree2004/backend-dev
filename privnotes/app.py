from flask import Flask, request, render_template, redirect, url_for, jsonify
import sqlite3
import random
import string
from cryptography.fernet import Fernet, InvalidToken


app = Flask(__name__)
DATABASE = 'notes.db'

# Encryption key - should be securely stored in a production environment
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS notes
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         content TEXT NOT NULL,
                         code TEXT NOT NULL UNIQUE)''')
        conn.commit()

# Generate a random code for each note
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Encrypt the note content
def encrypt_content(content):
    return cipher.encrypt(content.encode()).decode()

# Decrypt the note content
def decrypt_content(encrypted_content):
    try:
        return cipher.decrypt(encrypted_content.encode()).decode()
    except InvalidToken:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_note():
    content = request.form['content']
    if not content:
        return jsonify({"error": "Content cannot be empty"}), 400

    code = generate_code()
    encrypted_content = encrypt_content(content)
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (content, code) VALUES (?, ?)", (encrypted_content, code))
            conn.commit()
        return render_template('note_created.html', code=code)
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    if request.method == 'POST':
        code = request.form['code']
        if not code:
            return jsonify({"error": "Code cannot be empty"}), 400
        return redirect(url_for('view_note', code=code))
    return render_template('retrieve.html')

@app.route('/note/<code>', methods=['GET'])
def view_note(code):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM notes WHERE code = ?", (code,))
            note = cursor.fetchone()
            if note:
                decrypted_content = decrypt_content(note[0])
                if decrypted_content:
                    cursor.execute("DELETE FROM notes WHERE code = ?", (code,))
                    conn.commit()
                    return render_template('view_note.html', note=decrypted_content)
                else:
                    return jsonify({"error": "Failed to decrypt the note"}), 500
            else:
                return jsonify({"error": "Invalid code or note not found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="Internal Server Error"), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
