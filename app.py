from flask import Flask, render_template, request, redirect, url_for, flash ,   get_flashed_messages
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configure MySQL Connection
db = pymysql.connect(host='localhost',
                             user='root',
                             password='*****',
                             db='user_registration',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define User Model
class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

# Login Required
@login_manager.user_loader
def load_user(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    if row:
        user = User(id=row['id'], username=row['username'], email=row['email'], password=row['password'])
        return user
    else:
        return None
    
@app.route('/front')
def front():
    return render_template('front.html')

# Login View
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        row = cursor.fetchone()
        if row and check_password_hash(row['password'], password):
            user = User(id=row['id'], username=row['username'], email=row['email'], password=row['password'])
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('front'))
        else:
            flash('Invalid email or password.', 'error')
    messages = get_flashed_messages(with_categories=True)
    return render_template('login.html', messages=messages)
   

# Logout View
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

# Protected View
@app.route('/')
def index():
    return render_template('index1.html')


# Registration View
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # check if email is in valid format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.', 'error')
            return redirect(url_for('register'))
        password = request.form['password']
        password_hash = generate_password_hash(password)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password_hash))
        db.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')


# Contacts View
@app.route('/view_contacts')
@login_required
def view_contacts():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM contacts WHERE user_id=%s", (current_user.id,))
    contacts = cursor.fetchall()
    return render_template('view_contacts.html', contacts=contacts)




# Create Contact View
@app.route('/create_contact', methods=['GET', 'POST'])
@login_required
def create_contact():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone']
        email = request.form['email']
        notes = request.form['notes']
        group = request.form['group']
        cursor = db.cursor()
        cursor.execute("INSERT INTO contacts (user_id, name, phone_number, email, notes, `group`) VALUES (%s, %s, %s, %s, %s, %s)", (current_user.id, name, phone_number, email, notes, group))
        db.commit()
        return redirect(url_for('view_contacts'))
    return render_template('create_contact.html')

# Edit Contact View
@app.route('/edit_contact/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id=%s AND user_id=%s", (id, current_user.id))
    contact = cursor.fetchone()
    if not contact:
        return redirect(url_for('view_contacts'))
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        notes = request.form['notes']
        group = request.form['group']
        cursor = db.cursor()
        cursor.execute("UPDATE contacts SET name=%s, phone_number=%s, email=%s, notes=%s, `group`=%s WHERE id=%s AND user_id=%s", (name, phone_number, email, notes, group, id, current_user.id))

        db.commit()
        return redirect(url_for('view_contacts'))
    return render_template('edit_contact.html', contact=contact)

# Delete Contact View
@app.route('/delete_contact/<int:id>', methods=['POST'])
@login_required
def delete_contact(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=%s AND user_id=%s", (id, current_user.id))
    db.commit()
    return redirect(url_for('view_contacts'))

@app.route('/search_contacts', methods=['GET', 'POST'])
@login_required
def search_contacts():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        cursor = db.cursor()
        if category:
            cursor.execute("SELECT * FROM contacts WHERE user_id=%s AND name LIKE %s AND `group`=%s", (current_user.id, f'%{name}%', category))
        else:
            cursor.execute("SELECT * FROM contacts WHERE user_id=%s AND name LIKE %s", (current_user.id, f'%{name}%'))
        contacts = cursor.fetchall()
        return render_template('view_contacts.html', contacts=contacts)
    return render_template('view_contacts.html', contacts=contacts)


if __name__ == '__main__':
    app.run(debug=True)



