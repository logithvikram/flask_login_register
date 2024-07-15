from flask import Flask, request, session, redirect, url_for, jsonify
import psycopg2
import bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_cors import CORS
# import os


app = Flask(__name__)
CORS(app)
app.secret_key = 'kbajsdifgbijdbfkabibkabsi'  

# DATABASE_URL1 = os.environ.get('DATABASE_URL', 'postgres://logith:loki@db:5432/flask_db')
conn = psycopg2.connect('postgres://logith:loki@db:5432/flask_db') 

cursor = conn.cursor()

def create_users_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(120) NOT NULL
        )
    ''')
    conn.commit()

create_users_table()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'logithvikram.krishnamoorthy@vexternal.com'  
app.config['MAIL_PASSWORD'] = 'mixyzpgmfwbfqtnb'  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({'message': 'Username or email already exists'}), 400
        
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password.decode('utf-8')))
        conn.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/secure', methods=['GET'])
def secure():
    if 'username' in session:
        return jsonify({'message': 'You are logged in!', 'username': session['username']}), 200
    else:
        return jsonify({'message': 'Unauthorized'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/reset_request', methods=['POST'])
def reset_request():
    data = request.get_json()
    email = data['email']
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if user:
        token = s.dumps(email, salt='password-reset-salt')
        link = url_for('reset_token', token=token, _external=True)
        
        msg = Message('Password Reset Request', sender='logithvikram.krishnamoorthy@vexternal.com', recipients=[email])
        msg.body = f'{link}'
        mail.send(msg)
        
        return jsonify({'message': 'Password reset link sent'}), 200
    return jsonify({'message': 'Email not found'}), 404

@app.route('/reset_token/<token>', methods=['POST'])
def reset_token(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({'message': 'Token expired'}), 400
    except BadTimeSignature:
        return jsonify({'message': 'Invalid token'}), 400
    
    data = request.get_json()
    password = data['password']
    hashed_password = hash_password(password)
    
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password.decode('utf-8'), email))
    conn.commit()
    
    return jsonify({'message': 'Password reset successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)
