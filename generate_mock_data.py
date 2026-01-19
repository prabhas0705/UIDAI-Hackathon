import pandas as pd
import numpy as np
import json
import random
import os
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker('en_IN')

# Configuration
STATES = {
    "Maharashtra": ["Mumbai", "Thane", "Pune", "Nagpur", "Nashik"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Gautam Buddha Nagar", "Prayagraj"],
    "Karnataka": ["Bangalore Urban", "Mysore", "Belgaum", "Kalaburagi", "Dakshina Kannada"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Purnia", "Darbhanga"],
    "Kerala": ["Thiruvananthapuram", "Ernakulam", "Kozhikode", "Malappuram", "Thrissur"]
}

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_dates(start, end, n):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_seconds = [random.randrange(int_delta) for _ in range(n)]
    return [start + timedelta(seconds=s) for s in random_seconds]

def generate_saturation_data():
    data = []
    print("Generating Saturation Data...")
    for state, districts in STATES.items():
        for dist in districts:
            pop = random.randint(500000, 5000000)
            # Simulate outliers like Delhi/Kerala > 100%
            if state in ["Kerala", "Maharashtra"]:
                saturation = random.uniform(98.0, 105.0)
            elif state == "Bihar":
                saturation = random.uniform(85.0, 92.0)
            else:
                saturation = random.uniform(90.0, 100.0)
            
            aadhaar_assigned = int(pop * (saturation/100))
            
            data.append({
                "State": state,
                "District": dist,
                "Projected_Pop_2025": pop,
                "Aadhaar_Assigned": aadhaar_assigned,
                "Saturation_Percentage": round(saturation, 2)
            })
    
    df = pd.DataFrame(data)
    df.to_csv("data/saturation_data.csv", index=False)
    print("Saved data/saturation_data.csv")

def generate_enrolment_data(num_records=5000):
    print("Generating Enrolment Data...")
    data = []
    dates = generate_dates(START_DATE, END_DATE, num_records)
    
    for i in range(num_records):
        state = random.choice(list(STATES.keys()))
        district = random.choice(STATES[state])
        
        # Age buckets
        age_group = random.choices(["0-5", "5-18", "18+"], weights=[0.6, 0.3, 0.1])[0]
        gender = random.choice(["Male", "Female", "Transgender"])
        
        # Rejection logic (higher in some areas)
        rejection = 0
        if random.random() < 0.05:
            rejection = 1
            
        data.append({
            "Date": dates[i].strftime("%Y-%m-%d"),
            "State": state,
            "District": district,
            "Age_Group": age_group,
            "Gender": gender,
            "Rejection": rejection
        })
        
    df = pd.DataFrame(data)
    # Aggregate to monthly for the dashboard
    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('ME')
    df_agg = df.groupby(['Month', 'State', 'District', 'Age_Group', 'Gender']).agg(
        Enrolment_Count=('Rejection', 'count'),
        Rejection_Count=('Rejection', 'sum')
    ).reset_index()
    df_agg.to_csv("data/enrolment_data.csv", index=False)
    print("Saved data/enrolment_data.csv")

def generate_update_data(num_records=10000):
    print("Generating Update Data...")
    data = []
    dates = generate_dates(START_DATE, END_DATE, num_records)
    
    update_types = ["Address", "Mobile", "Biometric", "DOB", "Name"]
    weights = [0.3, 0.4, 0.2, 0.05, 0.05] # Mobile and Address are most common
    
    for i in range(num_records):
        state = random.choice(list(STATES.keys()))
        district = random.choice(STATES[state])
        u_type = random.choices(update_types, weights=weights)[0]
        gender = random.choice(["Male", "Female"])
        
        # Simulate trends
        # Higher mobile updates for women in MP/Bihar (we don't have MP, so stick to general)
        if u_type == "Mobile" and gender == "Female" and random.random() < 0.6:
            # Boost weight
            pass

        # Higher address updates in urban centers (Migration)
        if district in ["Bangalore Urban", "Mumbai", "Gautam Buddha Nagar"] and u_type == "Address":
             # Implicitly higher because of random choice, but we could boost
             pass
             
        data.append({
            "Date": dates[i].strftime("%Y-%m-%d"),
            "State": state,
            "District": district,
            "Update_Type": u_type,
            "Gender": gender,
            "Count": 1 # Granular transaction
        })

    df = pd.DataFrame(data)
    # Aggregate
    df['Month'] = pd.to_datetime(df['Date']).dt.to_period('ME')
    df_agg = df.groupby(['Month', 'State', 'District', 'Update_Type', 'Gender']).sum().reset_index()
    df_agg.to_csv("data/update_data.csv", index=False)
    print("Saved data/update_data.csv")

def generate_mock_geojson():
    print("Generating Mock GeoJSON...")
    # Create simple boxes for districts to allow map rendering
    features = []
    
    # Approximate lat/lon for states to place boxes
    # This is a VERY ROUGH approximation just to get polygons on the map
    base_coords = {
        "Maharashtra": [19.75, 75.71],
        "Uttar Pradesh": [26.84, 80.94],
        "Karnataka": [15.31, 75.71],
        "Bihar": [25.09, 85.31],
        "Kerala": [10.85, 76.27]
    }
    
    for state, districts in STATES.items():
        lat, lon = base_coords[state]
        for i, dist in enumerate(districts):
            # Create a small box around the center, offset by i
            offset_lat = lat + (i * 0.5)
            offset_lon = lon + (i * 0.5)
            
            # Polygon coordinates (box)
            coords = [
                [offset_lon, offset_lat],
                [offset_lon + 0.4, offset_lat],
                [offset_lon + 0.4, offset_lat + 0.4],
                [offset_lon, offset_lat + 0.4],
                [offset_lon, offset_lat] # Close loop
            ]
            
            feature = {
                "type": "Feature",
                "properties": {
                    "district": dist,
                    "state": state
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
            features.append(feature)
            
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open("data/india_districts.geojson", "w") as f:
        json.dump(geojson, f)
    print("Saved data/india_districts.geojson")

if __name__ == "__main__":
    ensure_dir("data")
    generate_saturation_data()
    generate_enrolment_data()
    generate_update_data()
    generate_mock_geojson()
