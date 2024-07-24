from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

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
        remember = 'remember' in request.form

        if email in users and check_password_hash(users[email]['password'], password):
            flash('Logged in successfully.', 'success')
            # Set session or cookie logic here
            if remember:
                # Logic to remember the user (e.g., using cookies)
                pass
            return redirect(url_for('gpa_calculator'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        users[email] = {'email': email, 'password': password}
        flash('You have successfully registered! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if email in users:
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            # In a real app, you would send the reset_url to the user's email
            flash(f'Password reset link has been sent to your email: {reset_url}', 'info')
        else:
            flash('Email not found', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = generate_password_hash(request.form['password'])
        users[email]['password'] = new_password
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/gpa_calculator', methods=['GET', 'POST'])
def gpa_calculator():
    if request.method == 'POST':
        # Logic for GPA calculation
        pass
    return render_template('gpa_calculator.html')

# Serving static files like CSS
@app.route('/static/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

if __name__ == '_main_':
    app.run(debug=True)