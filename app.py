from flask import Flask, render_template, request, redirect, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from cs50 import SQL
from datetime import datetime, timedelta, date


app = Flask(__name__)
app.secret_key = "xtestj*4-709894jaw,fo49451e"  # Replace with a strong secret key


db = SQL("sqlite:///database.db")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "landing"  # Redirect unauthorized users to /login


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.pasword_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    user_row = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if user_row:
        user_data = user_row[0]
        return User(user_data["id"], user_data["username"], user_data["password_hash"])
    return None

@app.route("/landing")
def landing():
    return render_template("landing.html")
# ...existing code...

@app.route('/')
def index():
    return render_template('index.html')

# ...existing code...
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("register.html", error="All fields are required.")
        
        if password != confirmation:
            return render_template("register.html", error="Passwords do not match.")
        
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            return render_template("register.html", error="Username already taken.")
        
        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, password_hash)
        
        return redirect("/login")  # only after successful registration
    
    # GET request → show the registration form
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="Username and password required.")
        
        user_row = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not user_row:
            return render_template("/login.html", error="Invalid username or password.")
        user_data = user_row[0]

        if not check_password_hash(user_data["password_hash"], password):
            return render_template("login.html", error="Invalid username or password.")
        
        user = User(user_data["id"], user_data["username"], user_data["password_hash"])
        login_user(user)
        return redirect("/")
    
    return render_template("/login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/add_habit", methods=["GET", "POST"])
@login_required
def add_habit():
    if request.method == "POST":
        habit_name = request.form.get("habit_name")
        if not habit_name:
            return render_template("add_habit.html", error="Please enter a habit name.")

        db.execute("INSERT INTO habits (user_id, name) VALUES (?, ?)", current_user.id, habit_name)
        return redirect("/")
    
    return render_template("add_habit.html")


@app.route("/stats")
@login_required
def stats():
    # Get the last 7 days' dates (Sun–Sat format)
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday() + 1)  # last Sunday
    end_date = start_date + timedelta(days=6)  # next Saturday

    # Query counts per day for the current user
    rows = db.execute("""
        SELECT date_completed, COUNT(*) as count
        FROM completions
        WHERE user_id = ?
        AND date_completed BETWEEN ? AND ?
        GROUP BY date_completed
    """, current_user.id, start_date.date(), end_date.date())

    # Initialize array with 0's for 7 days
    completions_per_day = [0] * 7
    for row in rows:
        day_index = (datetime.strptime(row["date_completed"], "%Y-%m-%d").weekday() + 1) % 7
        completions_per_day[day_index] = row["count"]

    return render_template("stats.html", completions_per_day=completions_per_day)

@app.route("/habits")
@login_required
def habits():
    today_str = date.today().isoformat()
    
    # All habits for the user
    all_habits = db.execute("SELECT * FROM habits WHERE user_id = ?", current_user.id)
    
    # Completed habit IDs today
    completed_today_rows = db.execute("""
        SELECT habit_id FROM completions 
        WHERE user_id = ? AND date_completed = ?
    """, current_user.id, today_str)
    
    completed_today_ids = {row["habit_id"] for row in completed_today_rows}
    
    # Separate active and completed habits
    active_habits = [h for h in all_habits if h["id"] not in completed_today_ids]
    completed_habits = [h for h in all_habits if h["id"] in completed_today_ids]
    
    return render_template("habits.html", active_habits=active_habits, completed_habits=completed_habits)

# Add habit
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_new_habit():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("add.html", error="Please enter a habit name.")
        db.execute("INSERT INTO habits (user_id, name) VALUES (?, ?)", current_user.id, name)
        return redirect("/habits")
    return render_template("add.html")

# Mark habit complete
@app.route("/complete/<int:habit_id>", methods=["POST"])
@login_required
def complete_habit(habit_id):
    today_str = date.today().isoformat()
    existing = db.execute(
        "SELECT * FROM completions WHERE user_id = ? AND habit_id = ? AND date_completed = ?",
        current_user.id, habit_id, today_str
    )
    if not existing:
        db.execute(
            "INSERT INTO completions (user_id, habit_id, date_completed) VALUES (?, ?, ?)",
            current_user.id, habit_id, today_str
        )
    
    habit_row = db.execute("SELECT name FROM habits WHERE id = ?", habit_id)
    habit_name = habit_row[0]["name"] if habit_row else "Habit"

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # AJAX request → return JSON
        return jsonify(success=True, habit_name=habit_name)
    else:
        # normal request → redirect
        return redirect(url_for("habits"))

# Stats route (use your working /stats route here)

if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)