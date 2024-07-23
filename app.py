from flask import Flask, render_template, request, jsonify
import os
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = os.urandom(24)

# A simple in-memory store for users (replace with a database for production)
users = {}

# Serializer for password reset tokens
serializer = URLSafeTimedSerializer(app.secret_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            return render_template('gpa_calculator.html')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        users[email] = {'email': email, 'password': password}
        return render_template('login.html')
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            # In a real app, you would send the reset_url to the user's email
            return f'Password reset link: {reset_url}'
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        return 'Invalid or expired token'
    if request.method == 'POST':
        password = generate_password_hash(request.form['password'])
        users[email]['password'] = password
        return render_template('login.html')
    return render_template('reset_password.html')

@app.route('/calculate_gpa', methods=['POST'])
def calculate_gpa():
    data = request.get_json()
    marks = data.get('marks', [])
    if not marks:
        return jsonify({'gpa': 0.0})
    gpa = sum(marks) / len(marks)
    return jsonify({'gpa': gpa})

if __name__ == '_main_':
    app.run(port=5000, debug=True)