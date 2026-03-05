from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecret123"

# ✅ TEMP STORAGE (instead of MongoDB)
users = []
bookings = []

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template("login.html")


# -------------------- LOGIN --------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        # find user in list
        user = next((u for u in users if u["email"] == email), None)

        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid Email or Password")

    return redirect(url_for('home'))


# -------------------- SIGNUP --------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # check existing
        existing_user = next((u for u in users if u["email"] == email), None)
        if existing_user:
            return render_template("signup.html", error="Email already exists")

        users.append({
            "username": username,
            "email": email,
            "password": generate_password_hash(password)
        })

        return redirect(url_for('home'))

    return render_template("signup.html")


# -------------------- DASHBOARD --------------------

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("home.html", username=session['user'])
    else:
        return redirect(url_for('home'))


# -------------------- LOGOUT --------------------

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


# -------------------- FLIGHTS --------------------

@app.route("/flights", methods=["GET", "POST"])
def flights():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        from_city = request.form.get("from")
        to_city = request.form.get("to")
        date = request.form.get("date")

        flights_data = [
            {
                "from": from_city,
                "to": to_city,
                "date": date,
                "airline": "Indigo",
                "time": "10:00 AM",
                "price": 4500
            },
            {
                "from": from_city,
                "to": to_city,
                "date": date,
                "airline": "Air India",
                "time": "2:00 PM",
                "price": 5200
            }
        ]

        return render_template("search_flights.html", flights=flights_data)

    return render_template("search_flights.html", flights=None)


# -------------------- BOOK FLIGHT --------------------

@app.route("/book", methods=["POST"])
def book():
    if "user" not in session:
        return redirect("/login")

    booking = {
        "airline": request.form.get("airline"),
        "price": request.form.get("price"),
        "from": request.form.get("from"),
        "to": request.form.get("to"),
        "date": request.form.get("date")
    }

    return render_template("payment.html", booking=booking)


# -------------------- CONFIRM PAYMENT --------------------

@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    if "user" not in session:
        return redirect("/login")

    booking = {
        "email": session["user"],
        "airline": request.form.get("airline"),
        "price": request.form.get("price"),
        "from": request.form.get("from"),
        "to": request.form.get("to"),
        "date": request.form.get("date")
    }

    bookings.append(booking)

    return redirect("/my_bookings")


# -------------------- MY BOOKINGS --------------------

@app.route("/my_bookings")
def my_bookings():
    if "user" not in session:
        return redirect("/login")

    user_email = session["user"]

    user_bookings = [b for b in bookings if b["email"] == user_email]

    return render_template("my_bookings.html", bookings=user_bookings)


# -------------------- HOTELS --------------------

@app.route("/hotels", methods=["GET", "POST"])
def hotels():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        city = request.form["city"]

        hotels_list = [
            {"name": "Taj Hotel", "city": city, "price": 5000},
            {"name": "Oberoi", "city": city, "price": 7000}
        ]

        return render_template("search_hotels.html", hotels=hotels_list)

    return render_template("search_hotels.html")


@app.route("/book_hotel", methods=["POST"])
def book_hotel():
    return "Hotel booked successfully!"


# -------------------- BUSES --------------------

@app.route("/buses", methods=["GET", "POST"])
def buses():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        from_city = request.form["from"]
        to_city = request.form["to"]

        buses_list = [
            {"name": "KSRTC", "from": from_city, "to": to_city, "price": 800},
            {"name": "VRL Travels", "from": from_city, "to": to_city, "price": 1200}
        ]

        return render_template("search_bus.html", buses=buses_list)

    return render_template("search_bus.html")


@app.route("/book_bus", methods=["POST"])
def book_bus():
    return "Bus booked successfully!"


# -------------------- RUN --------------------

if __name__ == "__main__":
    app.run(debug=True)