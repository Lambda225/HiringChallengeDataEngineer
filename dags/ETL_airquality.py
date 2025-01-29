import os
from dotenv import load_dotenv
from datetime import datetime,timedelta,time
from airflow.decorators import dag,task
from pymongo import MongoClient
import requests
import pandas as pd
from bson import json_util
import json

load_dotenv()

def averagecalculation(data):
    df = pd.DataFrame(data)
    df['t_created'] = pd.to_datetime(df['t_created'])
    current_time = datetime.now().time()
    reference_time = time(23, 0, 0)
    df['t_created'] = df['t_created'].dt.date
    daily_means = df.groupby('t_created', as_index=False)[['CO', 'PM2_5']].mean()
    daily_means['t_created'] = daily_means['t_created'].astype(str)
    result = daily_means.to_dict(orient='records')
    if current_time < reference_time:
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        result = [item for item in result if item['t_created'] != today_str]
    return result

db_url = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.ctpns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

default_value = {
    "ower":'parfait',
    'retries':2,
    "retry_delay":timedelta(minutes=2)
}

@dag(
    dag_id='ETL_airquality',
    default_args=default_value,
    start_date=datetime(2025,1,29),
    schedule_interval='@hourly',
    catchup=False,
)
def myETl():

    @task()
    def get_data():
        station_id =os.getenv('STATION_ID').split(',')
        all_data = []
        for id in station_id:
            response = requests.get(f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id}")
            all_data.append(response.json())
        return (all_data)
    

    @task()
    def db_existe():
        client = MongoClient(db_url)
        db = client["airquality"]

        return "sensor" in db.list_collection_names()
    

    @task()
    def data_transforme(all_data,val_bool):
        key_mapping = {
                'timestamp': 't_created',
                'T. int.': 'T_int',
                'PM2.5':'PM2_5'
            }
        date_format = '%Y-%m-%d %H:%M:%S'
        all_data_transforme = []
        if val_bool:
            for data in all_data:
                data = {'header':data["header"],'data':data['data'][-1]}
                data['data'] = {key_mapping.get(k, k): v for k, v in data['data'].items()}
                data['data'] = {**data['data'], 'date_converted': datetime.strptime(data['data']['t_created'], date_format)}
                all_data_transforme.append(data)
        else:
            for data in all_data:
                data['data'] = [
                    {key_mapping.get(k, k): v for k, v in record.items()} for record in data["data"]
                ]
                data = {**data,'meanData':averagecalculation(data['data'])}
                data['data'] = [{**record, 'date_converted': datetime.strptime(record['t_created'], date_format)} for record in data['data']]
                
                all_data_transforme.append(data)
        
        return all_data_transforme

    
    @task()
    def save_data(all_data_transforme,val_bool):
        client = MongoClient(db_url)
        db = client["airquality"]
        if val_bool:
            for data in all_data_transforme:
                collection = db["sensor"]
                insertion_result = collection.find_one({'station_name':data["header"]["station_name"]})
                data['data'] = {**data['data'],'sensor_id':insertion_result['_id']}

                current_time = datetime.now().time()
                reference_time = time(23, 0, 0)

                if current_time >= reference_time:
                    collection = db["sensordata"]
                    today = datetime.now()
                    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
                    end_of_day = datetime(today.year, today.month, today.day, 23, 30, 0)

                    results = list(collection.find({
                        "date_converted": {"$gte": start_of_day, "$lt": end_of_day},
                        'sensor_id':insertion_result['_id']
                    }))
                    
                    data['meanData'] = averagecalculation(results)[0]
                    
                    collection = db["meanday"]
                    data['meanData'] = {**data['meanData'],'sensor_id':insertion_result['_id']}
                    collection.insert_one(data['meanData'])

                collection = db["sensordata"]
                collection.insert_one(data["data"])
        else:
            for data in all_data_transforme:
                collection = db["sensor"]
                insertion_result = collection.insert_one(data["header"])

                data['meanData'] = [{**record, 'sensor_id': insertion_result.inserted_id} for record in data["meanData"]]
                collection = db["meanday"]
                collection.insert_many(data['meanData'])

                sensordata = [{**record, 'sensor_id': insertion_result.inserted_id} for record in data["data"]]
                collection = db["sensordata"]
                collection.insert_many(sensordata)
    

    val_bool = db_existe()
    all_data = get_data()
    all_data_transforme = data_transforme(all_data,val_bool)
    save_data(all_data_transforme,val_bool)


greet_dag = myETl()