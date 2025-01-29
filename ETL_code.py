import os
from dotenv import load_dotenv
from pymongo import MongoClient
from rich.console import Console
import pandas as pd
import requests

load_dotenv()

console = Console()

station_id = os.getenv('STATION_ID').split(',')

url = "https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{}"
db_url = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.ctpns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def getdata(url):
    response = requests.get(url)
    if response.status_code == 200:
        console.log('Collecte de donnée éffectué')
        return response.json()
    else:
        raise Exception("Désoler les données ne sont pas accéssible")


def averagecalculation(data,sensor_id):
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['t_created'] = df['timestamp'].dt.date
    daily_means = df.groupby('t_created', as_index=False)[['CO', 'PM2.5']].mean()
    daily_means['t_created'] = daily_means['t_created'].astype(str)
    daily_means['sensor_id'] = sensor_id
    daily_means = daily_means.rename(columns={'PM2.5': 'PM2_5'})
    result = daily_means.to_dict(orient='records')
    return result


def savedata(data,client):
    try:
        db = client["airquality"]
        collection = db["sensor"]
        insertion_result = collection.insert_one(data["header"])
        console.log('Sauvegarde de donnée du capteur éffectué')

        meanday = averagecalculation(data["data"], insertion_result.inserted_id)
        collection = db["meanday"]
        collection.insert_many(meanday)
        console.log('Sauvegarde de moyenne CO et PM2.5 par jour éffectué')

        collection = db["sensordata"]
        key_mapping = {
            'timestamp': 't_created',
            'T. int.': 'T_int',
            'PM2.5':'PM2_5'
        }
        data["data"] = [
            {key_mapping.get(k, k): v for k, v in record.items()} for record in data["data"]
        ]
        sensordata = [{**record, 'sensor_id': insertion_result.inserted_id} for record in data["data"]]
        collection.insert_many(sensordata)
        console.log('Sauvegarde de donnée relevé par heure éffectué')
    except:
        print("Une erreur s'est produit lors de l'insertion d'une donnée")



with console.status("[bold green]Exécution des taches...") as status: 

    client = MongoClient(db_url)
    console.log('connection de la BD éffectué')
    
    for id in station_id:
        console.log(f"Opération sur la station {id}")
        json_responce = getdata(f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id}")
        savedata(json_responce,client)