import time

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from sqlalchemy import create_engine, MetaData, select, insert, update, delete
from sqlalchemy.orm import sessionmaker
import json
from bson import ObjectId

# Настройки подключения
MONGO_URI = Variable.get('MONGO_URI')
DATABASE_URL_DWH = Variable.get('POSTGRESQL_URI')


def connect_to_mongo(retries=5, delay=5):
    for i in range(retries):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, socketTimeoutMS=20000)
            client.admin.command('ping')  # Проверка подключения
            return client
        except ConnectionFailure as e:
            print(f"Connection failed, retrying in {delay} seconds... (Attempt {i + 1}/{retries})")
            time.sleep(delay)
    raise Exception("Failed to connect to MongoDB after several retries")


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2024, 5, 24, tz="UTC"),
    catchup=False,
    tags=['mongo', 'stg'],
    is_paused_upon_creation=False
)
def load_mongo_to_stg():
    # Подключение к PostgreSQL
    dwh_engine = create_engine(DATABASE_URL_DWH)
    DwhSession = sessionmaker(bind=dwh_engine)
    dwh_metadata = MetaData()
    dwh_metadata.reflect(bind=dwh_engine, schema='stg')

    def load_data_from_mongo(collection_name, stg_table_name):
        # Подключение к MongoDB
        mongo_client = connect_to_mongo()
        mongo_db = mongo_client['mydatabase']

        dwh_session = DwhSession()
        stg_table = dwh_metadata.tables[f'stg.{stg_table_name}']
        settings_table = dwh_metadata.tables['stg.settings']

        # Получаем данные из таблицы настроек
        query = select([settings_table.c.settings]).where(
            settings_table.c.setting_key == f'{stg_table_name}_last_version')
        result = dwh_session.execute(query).fetchone()
        if result:
            last_version = result['settings']['last_version']
        else:
            last_version = 0
            initial_settings = insert(settings_table).values(
                setting_key=f'{stg_table_name}_last_version',
                settings={'last_version': last_version}
            )
            dwh_session.execute(initial_settings)
            dwh_session.commit()

        # Извлекаем данные из MongoDB
        collection = mongo_db[collection_name]
        new_data = collection.find()

        # print(new_data)

        # Вставляем данные в PostgreSQL
        for doc in new_data:
            doc_id = str(doc['_id'])
            doc.pop('_id')
            doc_json = json.dumps(doc, default=str, ensure_ascii=False)

            existing_record = dwh_session.execute(
                select([stg_table]).where(stg_table.c.obj_id == doc_id)
            ).fetchone()

            if existing_record:
                # Обновляем существующую запись новой версией
                update_stmt = update(stg_table).where(stg_table.c.obj_id == doc_id).values(
                    obj_val=doc_json,
                    when_updated=pendulum.now(),
                    version=last_version + 1
                )
                dwh_session.execute(update_stmt)
            else:
                # Вставляем новую запись
                insert_stmt = insert(stg_table).values(
                    obj_id=f'{doc_id}',
                    obj_val=doc_json,
                    when_updated=pendulum.now(),
                    version=last_version + 1
                )
                dwh_session.execute(insert_stmt)

        delete_stmt = delete(stg_table).where(stg_table.c.version <= last_version)
        dwh_session.execute(delete_stmt)

        # Обновляем last_version в таблице настроек
        update_settings = update(settings_table).where(
            settings_table.c.setting_key == f'{stg_table_name}_last_version'
        ).values(
            settings={'last_version': last_version + 1}
        )

        dwh_session.execute(update_settings)
        dwh_session.commit()
        dwh_session.close()

    @task()
    def load_clients():
        load_data_from_mongo('Clients', 'mongo_clients')

    @task()
    def load_restaurants():
        load_data_from_mongo('Restaurant', 'mongo_restaurants')

    @task()
    def load_orders():
        load_data_from_mongo('Orders', 'mongo_orders')

    clients_task = load_clients()
    restaurants_task = load_restaurants()
    orders_task = load_orders()

    [clients_task, restaurants_task, orders_task]


mongo_to_stg_dag = load_mongo_to_stg()
