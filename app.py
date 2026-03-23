from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

import os

uri = os.environ.get("DATABASE_URL")

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///database.db'

db = SQLAlchemy(app)

# =====================
# MODEL
# =====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))


class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(200))
    name = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    price = db.Column(db.Integer)
    weight = db.Column(db.Float)
    user_id = db.Column(db.Integer)

# =====================
# ROUTES
# =====================

@app.route('/')
def index():
    return redirect(url_for('login'))

#ล็อคอิน
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username 
            return redirect('/home')
        else:
            return "Login Failed ❌"

    return render_template('login.html')

#สมัครใช้งาน
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_pw = generate_password_hash(password)

        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

#หน้าหลัก
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    q = request.args.get('q')

    if q:
        bikes = Bike.query.filter(
            Bike.name.contains(q),
            Bike.user_id == session['user_id']
        ).all()
    else:
        bikes = Bike.query.filter_by(user_id=session['user_id']).all()

    return render_template('home.html', bikes=bikes)

#ออกจากระบบ
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


#เพิ่มรถ
@app.route('/add', methods=['GET', 'POST'])
def add_bike():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        brand = request.form['brand']
        name = request.form['name']
        image_url = request.form['image_url']
        price = request.form['price']
        weight = request.form['weight']

        bike = Bike(
            brand=brand,
            name=name,
            image_url=image_url,
            price=price,
            weight=weight,
            user_id=session['user_id']
        )

        db.session.add(bike)
        db.session.commit()

        return redirect('/home')

    return render_template('add.html')


#ลบรถ
@app.route('/delete/<int:id>')
def delete_bike(id):
    bike = Bike.query.get(id)
    db.session.delete(bike)
    db.session.commit()

    return redirect('/home')

#แก้ไขรถ
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_bike(id):
    if 'user_id' not in session:
        return redirect('/login')

    bike = Bike.query.get(id)

    if request.method == 'POST':
        bike.brand = request.form['brand']
        bike.name = request.form['name']
        bike.image_url = request.form['image_url']
        bike.price = request.form['price']
        bike.weight = request.form['weight']

        db.session.commit()

        return redirect('/home')

    return render_template('edit.html', bike=bike)


#โปรไฟล์
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        new_password = request.form['password']

        user.password = generate_password_hash(new_password)
        db.session.commit()

        return redirect('/home')

    return render_template('profile.html', user=user)


#ดูรถ

@app.route('/bike/<int:id>')
def bike_detail(id):
    if 'user_id' not in session:
        return redirect('/login')

    bike = Bike.query.filter_by(
        id=id,
        user_id=session['user_id']
    ).first()

    if not bike:
        return "Not Found", 404

    return render_template('bike_detail.html', bike=bike)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000)

