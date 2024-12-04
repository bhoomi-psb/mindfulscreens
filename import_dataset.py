import csv
from app import db, User,app

# Path to your dataset
DATASET_PATH = "dataset.csv"

def import_data():
    with open(DATASET_PATH, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Create a new User object for each row
            user = User(
                id=int(row['id']),
                device_model=row['device_model'],
                operating_system=row['operating_system'],
                app_usage_time=int(row['app_usage_time']),
                screen_on_time=float(row['screen_on_time']),
                battery_drain=int(row['battery_drain']),
                num_apps_installed=int(row['num_apps_installed']),
                data_usage=int(row['data_usage']),
                age=int(row['age']),
                gender=row['gender'],
                behavior_class=int(row['behavior_class'])
            )
            db.session.add(user)
        db.session.commit()
        print("Dataset imported successfully!")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database and table exist
        import_data()
