import os
from dotenv import load_dotenv
from pymongo import MongoClient
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

def savedata(data):
    try:
        client = MongoClient(db_url)
        db = client["airquality"]
        collection = db["sensordata"]
        insertion_result = collection.insert_many(data)
    except:
        print("Une erreur s'est produit lors de la connection a la BD")

    
data = getdata()

savedata(data)

