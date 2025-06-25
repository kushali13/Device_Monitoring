import os
import json
import random
import sys
from datetime import datetime, timedelta

# Add your project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Configure Django settings before any imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_monitoring.settings")

import django
django.setup()

# Now import your models AFTER Django is configured
from monitor.models import Asset

# --- Settings ---
DATA_FOLDER = 'media/data'
START_YEAR = 2020  # Start year for random dates
END_YEAR = 2025    # End year for random dates
ENTRIES_PER_FILE = 5  # Number of entries per file

LAPTOP_APPS = ["Google", "Youtube", "Gmail", "Microsoft Word"]
IFP_APPS = ["PowerPoint", "Google", "Firefox", "Google DOCs"]

def get_all_device_serials():
    """Get all device serial numbers from the database"""
    return list(Asset.objects.values_list('serial_number', flat=True))

def random_time(start_hour=9, end_hour=15):
    """Generate random time between school hours"""
    start = datetime(2025, 1, 1, start_hour)
    end = datetime(2025, 1, 1, end_hour)
    delta = (end - start).seconds
    random_second = random.randint(0, delta)
    return (start + timedelta(seconds=random_second)).time()

def random_date():
    """Generate random date between START_YEAR and END_YEAR"""
    start_date = datetime(START_YEAR, 1, 1)
    end_date = datetime(END_YEAR, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_duration(min_minutes=5, max_minutes=5):
    """Generate fixed 5 minute duration as per your example"""
    return timedelta(minutes=min_minutes)

def format_duration(td):
    """Format duration as HH:MM:SS"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def generate_timing_entries(serial_number, count=ENTRIES_PER_FILE):
    """Generate multiple timing entries in requested format"""
    entries = []
    for _ in range(count):
        date = random_date()
        start = random_time()
        duration = random_duration()
        end = (datetime.combine(date, start) + duration).time()
        
        entries.append({
            "serial_number": serial_number,
            "date": date.strftime('%m/%d/%Y'),
            "start_time": start.strftime('%H:%M:%S'),
            "end_time": end.strftime('%H:%M:%S'),
            "duration": format_duration(duration)
        })
    return {"entries": entries}

def generate_app_entries(device_type, count=ENTRIES_PER_FILE):
    """Generate multiple app usage entries in requested format"""
    apps = IFP_APPS if device_type == 'IFP' else LAPTOP_APPS
    entries = []
    for _ in range(count):
        date = random_date()
        start = random_time()
        duration = random_duration()
        end = (datetime.combine(date, start) + duration).time()
        
        entries.append({
            "package_name": random.choice(apps),
            "date": date.strftime('%m/%d/%Y'),
            "start_time": start.strftime('%H:%M:%S'),
            "end_time": end.strftime('%H:%M:%S'),
            "duration": format_duration(duration)
        })
    return entries

def write_json(file_path, data):
    """Write data to JSON file with proper formatting"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    try:
        all_devices = get_all_device_serials()
        print(f"Generating data for devices: {all_devices}")
        
        os.makedirs(DATA_FOLDER, exist_ok=True)

        for serial in all_devices:
            device_type = 'IFP' if serial.startswith('UD') else 'Laptop'
            
            # Generate timing data
            timing_file = os.path.join(DATA_FOLDER, f"{serial}_timing_Data.json")
            timing_data = generate_timing_entries(serial)
            write_json(timing_file, timing_data)
            
            # Generate app data
            app_file = os.path.join(DATA_FOLDER, f"{serial}_app_data.json")
            app_data = generate_app_entries(device_type)
            write_json(app_file, app_data)

        print("✅ Data generation complete!")
        print(f"Generated {ENTRIES_PER_FILE} entries per file in: {os.path.abspath(DATA_FOLDER)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()