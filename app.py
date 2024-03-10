from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define the Clinic class and its functionalities
class Clinic:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Create tables for users, patients, and appointments
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,  -- Add user_id column
                            name TEXT NOT NULL,
                            email TEXT NOT NULL UNIQUE,
                            phone TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id)
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                            id INTEGER PRIMARY KEY,
                            patient_id INTEGER,
                            service TEXT NOT NULL,
                            datetime TEXT NOT NULL,
                            FOREIGN KEY (patient_id) REFERENCES patients(id)
                        )''')
        self.conn.commit()


    # Function to register a new user
    def register_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        user_id = cursor.lastrowid
        self.conn.commit()
        return user_id

    # Function to login a user
    def login_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            return user[0]
        else:
            return None

    # Function to retrieve user profile
    def get_user_profile(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE user_id=?", (user_id,))
        return cursor.fetchone()

    # Function to update user profile
    def update_user_profile(self, user_id, name, email, phone):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE patients SET name=?, email=?, phone=? WHERE user_id=?", (name, email, phone, user_id))
        print("Coming here")
        self.conn.commit()

    # Function to schedule an appointment
    def schedule_appointment(self, patient_id, service, datetime):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO appointments (patient_id, service, datetime) VALUES (?, ?, ?)",
                       (patient_id, service, datetime))
        self.conn.commit()
        return True, "Appointment scheduled successfully."

# Initialize the Clinic object with the database file
clinic = Clinic('clinic.db')

# Define routes and their functionalities
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = clinic.register_user(username, password)
        session['user_id'] = user_id
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = clinic.login_user(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('profile'))
        else:
            print("user not registered")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login')) 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        clinic.update_user_profile(session['user_id'], name, email, phone)
        return redirect(url_for('schedule'))
    profile_data = clinic.get_user_profile(session['user_id'])
    return render_template('profile.html', profile_data=profile_data)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        service = request.form['service']
        appointment_datetime = request.form['datetime']
        patient_id = session['user_id']  # Using session['user_id'] directly as patient_id
        success, message = clinic.schedule_appointment(patient_id, service, appointment_datetime)
        return render_template('result.html', success=success, message=message)
    return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True)
