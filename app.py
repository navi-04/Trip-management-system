from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'j^2vehiclemanagement'

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        contact TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        capacity INTEGER NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        experience INTEGER NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        vehicle_id INTEGER NOT NULL,
        driver_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        pickup_point TEXT NOT NULL,
        end_point TEXT NOT NULL,
        status TEXT DEFAULT 'booked',
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
        FOREIGN KEY (driver_id) REFERENCES drivers (id)
    )
    ''')
    
    # Add sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO vehicles (name, model, capacity) VALUES ('Toyota Innova', '2022', 7)")
        cursor.execute("INSERT INTO vehicles (name, model, capacity) VALUES ('Honda City', '2021', 5)")
        cursor.execute("INSERT INTO vehicles (name, model, capacity) VALUES ('Maruti Swift', '2023', 5)")
    
    cursor.execute("SELECT COUNT(*) FROM drivers")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO drivers (name, experience) VALUES ('John Doe', 5)")
        cursor.execute("INSERT INTO drivers (name, experience) VALUES ('Jane Smith', 3)")
        cursor.execute("INSERT INTO drivers (name, experience) VALUES ('Michael Johnson', 8)")
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    contact = request.form.get('contact')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ? AND contact = ?", (username, contact))
    user = cursor.fetchone()
    
    if user is None:
        # Create a new user
        cursor.execute("INSERT INTO users (username, contact) VALUES (?, ?)", (username, contact))
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = user[0]
        
    conn.close()
    
    # Store user_id in session
    session['user_id'] = user_id
    session['username'] = username
    
    return redirect(url_for('trip_details'))

@app.route('/trip_details')
def trip_details():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, model, capacity FROM vehicles")
    vehicles = cursor.fetchall()
    
    cursor.execute("SELECT id, name, experience FROM drivers")
    drivers = cursor.fetchall()
    
    conn.close()
    
    return render_template('trip_details.html', vehicles=vehicles, drivers=drivers, username=session['username'])

@app.route('/book_trip', methods=['POST'])
def book_trip():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    vehicle_id = request.form.get('vehicle')
    driver_id = request.form.get('driver')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    pickup_point = request.form.get('pickup_point')
    end_point = request.form.get('end_point')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO trips (user_id, vehicle_id, driver_id, start_date, end_date, pickup_point, end_point)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], vehicle_id, driver_id, start_date, end_date, pickup_point, end_point))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('trip_history'))

@app.route('/trip_history')
def trip_history():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT t.id, v.name as vehicle_name, d.name as driver_name, t.start_date, t.end_date, 
           t.pickup_point, t.end_point, t.status
    FROM trips t
    JOIN vehicles v ON t.vehicle_id = v.id
    JOIN drivers d ON t.driver_id = d.id
    WHERE t.user_id = ?
    ORDER BY t.id DESC
    ''', (session['user_id'],))
    
    trips = cursor.fetchall()
    conn.close()
    
    return render_template('trip_history.html', trips=trips, username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Hardcoded admin credentials for simplicity
    if username == 'admin' and password == 'admin123':
        session['admin'] = True
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('admin'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT t.id, u.username, u.contact, v.name as vehicle_name, d.name as driver_name, 
           t.start_date, t.end_date, t.pickup_point, t.end_point, t.status
    FROM trips t
    JOIN users u ON t.user_id = u.id
    JOIN vehicles v ON t.vehicle_id = v.id
    JOIN drivers d ON t.driver_id = d.id
    ORDER BY t.id DESC
    ''')
    
    trips = cursor.fetchall()
    
    cursor.execute("SELECT id, name, model, capacity FROM vehicles")
    vehicles = cursor.fetchall()
    
    cursor.execute("SELECT id, name, experience FROM drivers")
    drivers = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin.html', trips=trips, vehicles=vehicles, drivers=drivers, dashboard=True)

@app.route('/admin/add_vehicle', methods=['POST'])
def add_vehicle():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    name = request.form.get('name')
    model = request.form.get('model')
    capacity = request.form.get('capacity')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO vehicles (name, model, capacity) VALUES (?, ?, ?)", (name, model, capacity))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_driver', methods=['POST'])
def add_driver():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    name = request.form.get('name')
    experience = request.form.get('experience')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO drivers (name, experience) VALUES (?, ?)", (name, experience))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_vehicle/<int:vehicle_id>', methods=['POST'])
def delete_vehicle(vehicle_id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if vehicle is used in any trip
    cursor.execute("SELECT COUNT(*) FROM trips WHERE vehicle_id = ?", (vehicle_id,))
    if cursor.fetchone()[0] > 0:
        # Vehicle is in use, just return to dashboard
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_driver/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if driver is assigned to any trip
    cursor.execute("SELECT COUNT(*) FROM trips WHERE driver_id = ?", (driver_id,))
    if cursor.fetchone()[0] > 0:
        # Driver is assigned, just return to dashboard
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    cursor.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/cancel_trip/<int:trip_id>', methods=['POST'])
def admin_cancel_trip(trip_id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("UPDATE trips SET status = 'cancelled' WHERE id = ?", (trip_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/cancel_trip/<int:trip_id>', methods=['POST'])
def cancel_trip(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Ensure the trip belongs to the current user
    cursor.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
    trip = cursor.fetchone()
    
    if trip and trip[0] == session['user_id']:
        cursor.execute("UPDATE trips SET status = 'cancelled' WHERE id = ?", (trip_id,))
        conn.commit()
    
    conn.close()
    
    return redirect(url_for('trip_history'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
