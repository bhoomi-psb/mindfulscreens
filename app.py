from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_model = db.Column(db.String(50))
    operating_system = db.Column(db.String(20))
    app_usage_time = db.Column(db.Integer)
    screen_on_time = db.Column(db.Float)
    battery_drain = db.Column(db.Integer)
    num_apps_installed = db.Column(db.Integer)
    data_usage = db.Column(db.Integer)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    behavior_class = db.Column(db.Integer)

# Routes
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = User(
            device_model=request.form['device_model'],
            operating_system=request.form['operating_system'],
            app_usage_time=int(request.form['app_usage_time']),
            screen_on_time=float(request.form['screen_on_time']),
            battery_drain=int(request.form['battery_drain']),
            num_apps_installed=int(request.form['num_apps_installed']),
            data_usage=int(request.form['data_usage']),
            age=int(request.form['age']),
            gender=request.form['gender'],
            behavior_class=int(request.form['behavior_class'])
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.device_model = request.form['device_model']
        user.operating_system = request.form['operating_system']
        user.app_usage_time = int(request.form['app_usage_time'])
        user.screen_on_time = float(request.form['screen_on_time'])
        user.battery_drain = int(request.form['battery_drain'])
        user.num_apps_installed = int(request.form['num_apps_installed'])
        user.data_usage = int(request.form['data_usage'])
        user.age = int(request.form['age'])
        user.gender = request.form['gender']
        user.behavior_class = int(request.form['behavior_class'])

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('update_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/charts', methods=['GET'])
def charts():
    users = User.query.all()
    return render_template('charts.html', users=users)

# Initialize Database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
