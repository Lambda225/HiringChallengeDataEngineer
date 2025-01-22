import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
from rich.console import Console
import pandas as pd
import requests

load_dotenv()

console = Console()

ids = os.getenv('STATION_ID')
id = ids.split(',')[0]
url = f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id}"
db_url = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.ctpns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def getdata():
    response = requests.get(url)
    if response.status_code == 200:
        console.log('Collecte de donnée éffectué')
        return response.json()
    else:
        raise Exception("Désoler les données ne sont pas accéssible")


def averagecalculation(data,sensor_id):
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    daily_means = df.groupby('date', as_index=False)[['CO', 'PM2.5']].mean()
    daily_means['date'] = daily_means['date'].astype(str)
    daily_means['sensor_id'] = sensor_id
    result = daily_means.to_dict(orient='records')
    return result


def savedata(data):
    try:
        client = MongoClient(db_url)
        console.log('connection de la BD éffectué')

        db = client["airquality"]
        collection = db["sensor"]
        insertion_result = collection.insert_one(data["header"])
        console.log('Sauvegarde de donnée du capter éffectué')

        meanday = averagecalculation(data["data"], insertion_result.inserted_id)
        collection = db["meanday"]
        collection.insert_many(meanday)
        console.log('Sauvegarde de moyenne CO et PM2.5 par jour éffectué')

        collection = db["sensordata"]
        sensordata = [{**record, 'sensor_id': insertion_result.inserted_id} for record in data["data"]]
        collection.insert_many(sensordata)
        console.log('Sauvegarde de donnée relevé par heure éffectué')
    except:
        print("Une erreur s'est produit lors de la connection a la BD")



with console.status("[bold green]Exécution des taches...") as status:   
    data = getdata()
    savedata(data)

