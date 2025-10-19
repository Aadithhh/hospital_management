from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'secret123'  # needed for sessions

# ---------- DATABASE CONFIG ----------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # add your password if needed
app.config['MYSQL_DB'] = 'hospital_db'

mysql = MySQL(app)

# ---------- LOGIN ROUTES ----------


@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM Admin WHERE username=%s AND password=%s", (username, password))
        admin = cur.fetchone()
        cur.close()

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

# ---------- LOGIN PROTECTION ----------


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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patients")
    data = cur.fetchall()
    cur.close()
    return render_template('patients.html', patients=data)


@app.route('/add_patient', methods=['POST'])
@login_required
def add_patient():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Patients (name, age, gender, address, phone) VALUES (%s, %s, %s, %s, %s)",
                (name, age, gender, address, phone))
    mysql.connection.commit()
    cur.close()
    return redirect('/patients')

# ---------- DOCTORS ----------


@app.route('/doctors')
@login_required
def doctors():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Doctors")
    data = cur.fetchall()
    cur.close()
    return render_template('doctors.html', doctors=data)


@app.route('/add_doctor', methods=['POST'])
@login_required
def add_doctor():
    name = request.form['name']
    specialization = request.form['specialization']
    phone = request.form['phone']
    email = request.form['email']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Doctors (name, specialization, phone, email) VALUES (%s, %s, %s, %s)",
                (name, specialization, phone, email))
    mysql.connection.commit()
    cur.close()
    return redirect('/doctors')

# ---------- APPOINTMENTS ----------


@app.route('/appointments')
@login_required
def appointments():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT a.appointment_id, p.name, d.name, a.appointment_date, a.appointment_time, a.status
                   FROM Appointments a
                   JOIN Patients p ON a.patient_id = p.patient_id
                   JOIN Doctors d ON a.doctor_id = d.doctor_id""")
    data = cur.fetchall()
    cur.execute("SELECT patient_id, name FROM Patients")
    patients = cur.fetchall()
    cur.execute("SELECT doctor_id, name FROM Doctors")
    doctors = cur.fetchall()
    cur.close()
    return render_template('appointments.html', appointments=data, patients=patients, doctors=doctors)


@app.route('/add_appointment', methods=['POST'])
@login_required
def add_appointment():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    date = request.form['appointment_date']
    time = request.form['appointment_time']
    status = request.form['status']
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO Appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
                   VALUES (%s, %s, %s, %s, %s)""",
                (patient_id, doctor_id, date, time, status))
    mysql.connection.commit()
    cur.close()
    return redirect('/appointments')

# ---------- STAFF ----------


@app.route('/staff')
@login_required
def staff():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Staff")
    data = cur.fetchall()
    cur.close()
    return render_template('staff.html', staff=data)


@app.route('/add_staff', methods=['POST'])
@login_required
def add_staff():
    name = request.form['name']
    role = request.form['role']
    phone = request.form['phone']
    salary = request.form['salary']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Staff (name, role, phone, salary) VALUES (%s, %s, %s, %s)",
                (name, role, phone, salary))
    mysql.connection.commit()
    cur.close()
    return redirect('/staff')


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
