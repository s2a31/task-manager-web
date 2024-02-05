from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_bcrypt import Bcrypt
import mysql.connector
import config

# Configure Flask application
app = Flask(__name__)

# Initialize Flask-Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Configure session to use the filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database configuration
db_config = {
    'user': config.MYSQL_DATABASE_USER,
    'password': config.MYSQL_DATABASE_PASSWORD,
    'host': config.MYSQL_DATABASE_HOST,
    'database': config.MYSQL_DATABASE_DB
}

# Function to connect to the SQLite database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Function to add headers to responses to prevent caching
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    # Redirect to login if user is not logged in
    if not session.get("user_id"):
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == "POST":
            # Retrieve form data for new task
            tname = request.form.get("tname")
            description = request.form.get("description")
            date = request.form.get("date")
            status = request.form.get("status")

            # Check if all form fields are filled
            if not tname or not description or not date or not status:
                flash("All fields are required.")
                return redirect("/")

            # Check if status is valid
            valid_statuses = ['Pending', 'In Progress', 'Completed']
            if status not in valid_statuses:
                flash("Invalid status.")
                return redirect("/")

            # Insert new task into the database
            cursor.execute("INSERT INTO tasks (user_id, tname, description, date, status) VALUES (%s, %s, %s, %s, %s)",
                           (session['user_id'], tname, description, date, status))
            conn.commit()
            return redirect("/")
        else:
            is_main_route = True
            # Fetch username for the logged-in user
            cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            username = user['username'] if user else 'Unknown User'
            # Fetch tasks for the logged-in user
            cursor.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY CASE status WHEN 'Pending' THEN 1 WHEN 'In Progress' THEN 2 WHEN 'Completed' THEN 3 END", (session['user_id'],))
            tasks = cursor.fetchall()

            return render_template("index.html", tasks=tasks, username=username, is_main_route=is_main_route)
    except mysql.connector.Error as e:
        flash(f"Database error: {e}")
        return redirect("/")
    finally:
        cursor.close()
        conn.close()

# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Retrieve registration form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Hash the user's password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if the username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                flash("Username already taken. Please choose another one.")
                return redirect("/register")

            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
        except mysql.connector.Error as e:
            flash(f"Database error: {e}")
            return redirect("/register")
        finally:
            cursor.close()
            conn.close()
        return redirect("/login")
    return render_template("register.html")

# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Retrieve login form data
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch the user record from the database
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            # Check password and set session if valid
            if user and bcrypt.check_password_hash(user['password'], password):
                session["user_id"] = user['id']
                return redirect("/")
            else:
                flash("Invalid username or password")
        except mysql.connector.Error as e:
            flash(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    return render_template("login.html")

# Route for user logout
@app.route("/logout")
def logout():
    # Clear the user session
    session.clear()
    return redirect("/login")

# Route to update an existing task
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_task(id):
    if not session.get("user_id"):
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == "POST":
            # Retrieve form data for task update
            tname = request.form.get("tname")
            description = request.form.get("description")
            date = request.form.get("date")
            status = request.form.get("status")

            if not tname or not description or not date or not status:
                flash("All fields are required.")
                return redirect(f"/update/{id}")

            # Update task in the database
            cursor.execute("UPDATE tasks SET tname=%s, description=%s, date=%s, status=%s WHERE id=%s AND user_id=%s",
                           (tname, description, date, status, id, session['user_id']))
            conn.commit()
            return redirect("/")
        else:
            is_update_route = True
            # Retrieve the username of the logged-in user
            cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            username = user['username'] if user else 'Unknown User'

            # Fetch task details for the given task ID
            cursor.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (id, session['user_id']))
            task = cursor.fetchone()

            if task is None:
                flash("Task not found or you do not have permission to edit this task.")
                return redirect("/")

            return render_template("update.html", task=task, username=username, is_update_route=is_update_route)
    except mysql.connector.Error as e:
        flash(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()
    return redirect("/")

@app.route("/update_task_status", methods=["POST"])
def update_task_status():
    data = request.get_json()
    task_id = data['id']
    new_status = data['status']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
        conn.commit()
        return jsonify({"status": "success"})
    except mysql.connector.Error as e:
        flash(f"Database error: {e}")
        return jsonify({"status": "error"})
    finally:
        cursor.close()
        conn.close()

@app.route("/delete/<int:id>", methods=["POST"])
def delete_task(id):
    if not session.get("user_id"):
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (id, session['user_id']))
        conn.commit()
    except mysql.connector.Error as e:
        flash(f"Database error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"status": "success", "message": "Task deleted"})

@app.route("/delete_all_tasks", methods=["POST"])
def delete_all_tasks():
    if not session.get("user_id"):
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM tasks WHERE user_id = %s", (session['user_id'],))
        conn.commit()
        return jsonify({"status": "success", "message": "All tasks deleted"})
    except mysql.connector.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/delete_account", methods=["POST"])
def delete_account():
    if not session.get("user_id"):
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Delete user's tasks
        cursor.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))
        # Delete user account
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        session.clear()
        return jsonify({"status": "success", "message": "Account deleted"})
    except mysql.connector.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/about")
def about():
    is_about_route = True
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Retrieve the username of the logged-in user
        cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        username = user['username'] if user else 'Unknown User'
        return render_template("about.html", username=username, is_about_route=is_about_route)
    except mysql.connector.Error as e:
        flash(f"Database error: {e}")
        return redirect("/")
    finally:
        cursor.close()
        conn.close()