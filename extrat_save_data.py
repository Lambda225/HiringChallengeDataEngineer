import os
from dotenv import load_dotenv
import requests

load_dotenv()

id = os.getenv('STATION_ID')
url = f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id}"


def getdata():
    response = requests.get(url)

    if response.status_code == 200:
        json_response = response.json()
        print(json_response['data'])
    else:
        raise Exception("Désoler les données ne sont pas accéssible")
    
getdata()