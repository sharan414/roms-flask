from flask import Flask, render_template, request, redirect, url_for, session
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'
logging.basicConfig(level=logging.DEBUG)

# Users and roles
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "waiter": {"password": "waiter123", "role": "waiter"}
}

# Menu
menu = {
    "Burger": 120,
    "Pizza": 250,
    "Fries": 100,
    "Coke": 40
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = users.get(uname)

        if user and user['password'] == pwd:
            session['username'] = uname
            session['role'] = user['role']
            logging.info(f"User logged in: {uname} (role: {user['role']})")
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    username = session.get('username')
    logging.info(f"Accessing dashboard: {username} ({role})")

    if role == 'admin':
        return render_template('admin_dashboard.html', user=username)
    elif role == 'waiter':
        return render_template('waiter_dashboard.html', user=username)
    else:
        return "Access Denied", 403

@app.route('/index')
def index():
    if 'username' not in session or session.get('role') != 'waiter':
        return "Access Denied", 403
    return render_template('index.html', menu=menu, user=session['username'])

@app.route('/order', methods=['POST'])
def order():
    if 'username' not in session or session.get('role') != 'waiter':
        return "Access Denied", 403

    order_items = {}
    total = 0

    for item, price in menu.items():
        qty = int(request.form.get(item, 0))
        if qty > 0:
            order_items[item] = {"qty": qty, "price": price}
            total += qty * price

    return render_template('confirmation.html', order_items=order_items, total=total)

if __name__ == '__main__':
    app.run(debug=True)
