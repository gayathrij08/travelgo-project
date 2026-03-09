import os
import uuid
import datetime
from decimal import Decimal
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient

app = Flask(__name__)

app.secret_key = "travelgo_secret"

# ---------------- MONGODB CONNECTION ----------------

mongo_uri = os.environ.get("MONGO_URI")

client = MongoClient(mongo_uri)

db = client["travelDB"]

users_collection = db["users"]
bookings_collection = db["bookings"]

# ---------------- STATIC DATA ----------------

bus_data = [
    {"id": "B1", "name": "Super Luxury Bus", "source": "Hyderabad", "dest": "Bangalore", "price": 800},
    {"id": "B2", "name": "Express Bus", "source": "Chennai", "dest": "Hyderabad", "price": 700}
]

train_data = [
    {"id": "T1", "name": "Rajdhani Express", "source": "Hyderabad", "dest": "Delhi", "price": 1500},
    {"id": "T2", "name": "Shatabdi Express", "source": "Chennai", "dest": "Bangalore", "price": 900}
]

flight_data = [
    {"id": "F1", "name": "Indigo 6E203", "source": "Hyderabad", "dest": "Dubai", "price": 8500},
    {"id": "F2", "name": "Air India AI102", "source": "Delhi", "dest": "Singapore", "price": 9500}
]

hotel_data = [
    {"id": "H1", "name": "Grand Palace", "city": "Chennai", "type": "Luxury", "price": 4000},
    {"id": "H2", "name": "Budget Inn", "city": "Hyderabad", "type": "Budget", "price": 1500}
]

# ---------------- HELPER ----------------

def get_transport_info(t_id):

    for b in bus_data:
        if b["id"] == t_id:
            return {"type":"Bus","source":b["source"],"destination":b["dest"],"details":b["name"]}

    for t in train_data:
        if t["id"] == t_id:
            return {"type":"Train","source":t["source"],"destination":t["dest"],"details":t["name"]}

    for f in flight_data:
        if f["id"] == t_id:
            return {"type":"Flight","source":f["source"],"destination":f["dest"],"details":f["name"]}

    for h in hotel_data:
        if h["id"] == t_id:
            return {"type":"Hotel","source":h["city"],"destination":h["city"],"details":h["name"]}

    return None


# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        users_collection.insert_one({
            "email":request.form['email'],
            "name":request.form['name'],
            "password":request.form['password'],
            "logins":0
        })

        return redirect('/login')

    return render_template("register.html")


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        user = users_collection.find_one({"email":request.form['email']})

        if user and user["password"] == request.form['password']:

            session['user'] = user['email']
            session['name'] = user['name']

            return redirect('/dashboard')

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    bookings = list(bookings_collection.find({"email":session['user']}))

    return render_template("dashboard.html",
                           name=session['name'],
                           bookings=bookings)


@app.route('/bus')
def bus():
    return render_template("bus.html", buses=bus_data)


@app.route('/train')
def train():
    return render_template("train.html", trains=train_data)


@app.route('/flight')
def flight():
    return render_template("flight.html", flights=flight_data)


@app.route('/hotels')
def hotels():
    return render_template("hotels.html", hotels=hotel_data)


@app.route('/seat/<transport_id>/<price>')
def seat(transport_id, price):

    if 'user' not in session:
        return redirect('/login')

    return render_template("seat.html", id=transport_id, price=price)


@app.route('/book', methods=['POST'])
def book():

    if 'user' not in session:
        return redirect('/login')

    t_id = request.form['transport_id']
    seats = request.form.get('seat')
    price = request.form['price']

    info = get_transport_info(t_id)

    session['booking_flow'] = {
        "transport_id":t_id,
        "type":info['type'],
        "source":info['source'],
        "destination":info['destination'],
        "details":info['details'],
        "seat":seats,
        "price":price,
        "date":str(datetime.date.today())
    }

    return render_template("payment.html", booking=session['booking_flow'])


@app.route('/payment', methods=['POST'])
def payment():

    if 'user' not in session or 'booking_flow' not in session:
        return redirect('/dashboard')

    booking = session['booking_flow']

    booking["booking_id"] = str(uuid.uuid4())[:8]
    booking["email"] = session['user']
    booking["payment_method"] = request.form.get('method')
    booking["payment_reference"] = request.form.get('reference')

    bookings_collection.insert_one(booking)

    session.pop('booking_flow', None)

    return render_template("ticket.html", booking=booking)


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


if __name__ == '__main__':

    app.run(debug=True)