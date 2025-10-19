from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'  # needed for sessions

DB_FILE = 'hospital.db'

# ---------- DATABASE HELPER ----------


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don’t exist"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        address TEXT,
        phone TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        phone TEXT,
        email TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date TEXT,
        appointment_time TEXT,
        status TEXT,
        FOREIGN KEY(patient_id) REFERENCES Patients(patient_id),
        FOREIGN KEY(doctor_id) REFERENCES Doctors(doctor_id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        phone TEXT,
        salary REAL
    )''')

    # Insert default admin if not exists
    cur.execute("SELECT * FROM Admin WHERE username='admin'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO Admin (username, password) VALUES ('admin', 'admin123')")

    conn.commit()
    conn.close()


# ---------- LOGIN ROUTES ----------
@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Admin WHERE username=? AND password=?", (username, password))
        admin = cur.fetchone()
        conn.close()

        if admin:
            session['username'] = username
            flash('Login Successful', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid Username or Password', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect('/login')


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('index.html')
    else:
        flash('Login required!', 'warning')
        return redirect('/login')


# ---------- LOGIN PROTECTION DECORATOR ----------
def login_required(route_func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Please login first.', 'warning')
            return redirect('/login')
        return route_func(*args, **kwargs)
    wrapper.__name__ = route_func.__name__
    return wrapper


# ---------- PATIENTS ----------
@app.route('/patients')
@login_required
def patients():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM Patients").fetchall()
    conn.close()
    return render_template('patients.html', patients=data)


@app.route('/add_patient', methods=['POST'])
@login_required
def add_patient():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']

    conn = get_db_connection()
    conn.execute("INSERT INTO Patients (name, age, gender, address, phone) VALUES (?, ?, ?, ?, ?)",
                 (name, age, gender, address, phone))
    conn.commit()
    conn.close()
    return redirect('/patients')


# ---------- DOCTORS ----------
@app.route('/doctors')
@login_required
def doctors():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM Doctors").fetchall()
    conn.close()
    return render_template('doctors.html', doctors=data)


@app.route('/add_doctor', methods=['POST'])
@login_required
def add_doctor():
    name = request.form['name']
    specialization = request.form['specialization']
    phone = request.form['phone']
    email = request.form['email']

    conn = get_db_connection()
    conn.execute("INSERT INTO Doctors (name, specialization, phone, email) VALUES (?, ?, ?, ?)",
                 (name, specialization, phone, email))
    conn.commit()
    conn.close()
    return redirect('/doctors')


# ---------- APPOINTMENTS ----------
@app.route('/appointments')
@login_required
def appointments():
    conn = get_db_connection()
    data = conn.execute('''
        SELECT a.appointment_id, p.name AS patient_name, d.name AS doctor_name,
               a.appointment_date, a.appointment_time, a.status
        FROM Appointments a
        JOIN Patients p ON a.patient_id = p.patient_id
        JOIN Doctors d ON a.doctor_id = d.doctor_id
    ''').fetchall()

    patients = conn.execute("SELECT patient_id, name FROM Patients").fetchall()
    doctors = conn.execute("SELECT doctor_id, name FROM Doctors").fetchall()
    conn.close()
    return render_template('appointments.html', appointments=data, patients=patients, doctors=doctors)


@app.route('/add_appointment', methods=['POST'])
@login_required
def add_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    date = request.form['appointment_date']
    time = request.form['appointment_time']
    status = request.form['status']

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (patient_id, doctor_id, date, time, status))
    conn.commit()
    conn.close()
    return redirect('/appointments')


# ---------- STAFF ----------
@app.route('/staff')
@login_required
def staff():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM Staff").fetchall()
    conn.close()
    return render_template('staff.html', staff=data)


@app.route('/add_staff', methods=['POST'])
@login_required
def add_staff():
    name = request.form['name']
    role = request.form['role']
    phone = request.form['phone']
    salary = request.form['salary']

    conn = get_db_connection()
    conn.execute("INSERT INTO Staff (name, role, phone, salary) VALUES (?, ?, ?, ?)",
                 (name, role, phone, salary))
    conn.commit()
    conn.close()
    return redirect('/staff')


# ---------- RUN ----------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
