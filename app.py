from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB = "database.db"

# ------------------ Database setup ------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Students table
    c.execute("""CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                dob TEXT,
                email TEXT,
                phone TEXT,
                branch TEXT,
                semester TEXT,
                address TEXT
                )""")
    # Admin table
    c.execute("""CREATE TABLE IF NOT EXISTS admin(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                )""")
    # Default admin
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admin(username,password) VALUES (?,?)", ("admin","admin123"))
    conn.commit()
    conn.close()

init_db()

# ------------------ Routes ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin = c.fetchone()
        conn.close()
        if admin:
            session["admin"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Credentials ❌", "danger")
            return redirect(url_for("login"))
    return render_template("index.html", title="Admin Login")

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", admin=session["admin"], title="Dashboard")

@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "admin" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        reg_no = request.form["reg_no"].strip()
        name = request.form["name"].strip()
        dob = request.form["dob"]
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        branch = request.form["branch"].strip()
        semester = request.form["semester"].strip()
        address = request.form["address"].strip()
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("""INSERT INTO students(reg_no,name,dob,email,phone,branch,semester,address)
                         VALUES (?,?,?,?,?,?,?,?)""",
                      (reg_no,name,dob,email,phone,branch,semester,address))
            conn.commit()
            conn.close()
            flash("Student added successfully ✅", "success")
            return redirect(url_for("student_list"))
        except sqlite3.IntegrityError as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for("add_student"))
    return render_template("add.html", title="Add Student")

@app.route("/student_list")
def student_list():
    if "admin" not in session:
        return redirect(url_for("login"))
    search = request.args.get("search")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if search:
        c.execute("SELECT * FROM students WHERE reg_no LIKE ?", ('%'+search+'%',))
    else:
        c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return render_template("list.html", students=students, search=search, title="Student List")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == "POST":
        reg_no = request.form["reg_no"].strip()
        name = request.form["name"].strip()
        dob = request.form["dob"]
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        branch = request.form["branch"].strip()
        semester = request.form["semester"].strip()
        address = request.form["address"].strip()
        c.execute("""UPDATE students SET reg_no=?, name=?, dob=?, email=?, phone=?, branch=?, semester=?, address=? 
                     WHERE id=?""",
                  (reg_no,name,dob,email,phone,branch,semester,address,id))
        conn.commit()
        conn.close()
        flash("Student updated successfully ✅", "success")
        return redirect(url_for("student_list"))
    else:
        c.execute("SELECT * FROM students WHERE id=?", (id,))
        student = c.fetchone()
        conn.close()
        return render_template("edit.html", student=student, title="Edit Student")

@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully ✅", "success")
    return redirect(url_for("student_list"))

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)