import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
import requests

load_dotenv()

id = os.getenv('STATION_ID')
url = f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id}"
db_url = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.ctpns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def getdata():
    response = requests.get(url)

    if response.status_code == 200:
        json_response = response.json()
        return json_response['data']
    else:
        raise Exception("Désoler les données ne sont pas accéssible")

def averagecalculation(data):

    daily_sums = defaultdict(int)
    daily_counts = defaultdict(int)

    for record in data:
        date = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S').date()
        daily_sums[date] += record['CO']
        daily_counts[date] += 1

    daily_means = {date: daily_sums[date] / daily_counts[date] for date in daily_sums}
    
    for date, mean in daily_means.items():
        print(f"{date}: {mean}")


def savedata(data):
    try:
        client = MongoClient(db_url)
        db = client["airquality"]
        collection = db["sensordata"]
        insertion_result = collection.insert_many(data)
    except:
        print("Une erreur s'est produit lors de la connection a la BD")

    
data = getdata()

averagecalculation(data)

