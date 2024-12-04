from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Ensure the 'data' directory exists for SQLite file
if not os.path.exists('data'):
    os.makedirs('data')


# Database model for goals and tasks
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_time = db.Column(db.Float, nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)


# Home page route
@app.route('/')
def index():
    return render_template('index.html')


# Dashboard page route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Load user data from CSV
    csv_file_path = 'user_data.csv'
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"The file {csv_file_path} does not exist.")

    user_data = pd.read_csv(csv_file_path)

    # Ensure proper data types and handle missing data
    user_data['app_usage_time'] = pd.to_numeric(user_data['app_usage_time'], errors='coerce')
    user_data['battery_drain'] = pd.to_numeric(user_data['battery_drain'], errors='coerce')
    user_data['data_usage'] = pd.to_numeric(user_data['data_usage'], errors='coerce')
    user_data = user_data.dropna(subset=['app_usage_time', 'battery_drain', 'data_usage'])

    # Example: Compute average statistics
    avg_app_usage = user_data['app_usage_time'].mean()
    avg_battery_drain = user_data['battery_drain'].mean()
    avg_data_usage = user_data['data_usage'].mean()

    # Group data by user behavior class for analysis
    behavior_analysis = user_data.groupby('user_behaviour_class').agg({
        'app_usage_time': 'mean',
        'battery_drain': 'mean',
        'data_usage': 'mean'
    }).reset_index()

    # Handle goal setting form
    if request.method == 'POST':
        goal_time = request.form['goal_time']
        new_goal = Goal(goal_time=goal_time)
        try:
            db.session.add(new_goal)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

    # Fetch tasks and goals from database
    goals = Goal.query.all()
    tasks = Task.query.all()

    return render_template('dashboard.html',
                           avg_app_usage=avg_app_usage,
                           avg_battery_drain=avg_battery_drain,
                           avg_data_usage=avg_data_usage,
                           behavior_analysis=behavior_analysis.to_dict(orient='records'),
                           goals=goals,
                           tasks=tasks)


# Task completion toggle route
@app.route('/toggle_task/<int:id>', methods=['POST'])
def toggle_task(id):
    task = Task.query.get(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('dashboard'))


# Task deletion route
@app.route('/delete_task/<int:id>', methods=['POST'])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))


# AJAX-based filtering route
@app.route('/filter')
def filter_data():
    user_class = request.args.get('user_class')
    csv_file_path = 'user_data.csv'
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"The file {csv_file_path} does not exist.")

    user_data = pd.read_csv(csv_file_path)
    filtered_data = user_data[user_data['user_behaviour_class'] == user_class]

    filtered_analysis = filtered_data.groupby('user_behaviour_class').agg({
        'app_usage_time': 'mean',
        'battery_drain': 'mean',
        'data_usage': 'mean'
    }).reset_index()

    return jsonify(filtered_analysis.to_dict(orient='records'))


# Run the app
if __name__ == '__main__':
    db.create_all()  # Create tables if not exist
    app.run(debug=True)
