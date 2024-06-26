import requests
import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from sqlalchemy import create_engine, MetaData, select, insert, update, delete
from sqlalchemy.orm import sessionmaker
import json

# Настройки подключения
DATABASE_URL_DWH = Variable.get('POSTGRESQL_URI')
API_URL = Variable.get('API_URL')


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2024, 5, 24, tz="UTC"),
    catchup=False,
    tags=['api', 'stg'],
    is_paused_upon_creation=False
)
def load_api_to_stg():
    # Подключение к PostgreSQL
    dwh_engine = create_engine(DATABASE_URL_DWH)
    DwhSession = sessionmaker(bind=dwh_engine)
    dwh_metadata = MetaData()
    dwh_metadata.reflect(bind=dwh_engine, schema='stg')

    def get_deliverers():
        url = f'{API_URL}/delivery/deliverers'
        page = 0
        limit = 10
        deliverers = []

        while True:
            response = requests.get(url, params={'limit': limit, 'page': page})
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break
                deliverers.extend(data)
                page += 1
            else:
                raise Exception(f"Failed to fetch data: {response.status_code}")

        return deliverers

    def get_deliveryman_data(deliveryman_id):
        url = f'{API_URL}/delivery/deliveryman/{deliveryman_id}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data for deliveryman {deliveryman_id}: {response.status_code}")

    def load_deliverers_to_stg(deliverers):
        dwh_session = DwhSession()
        settings_table = dwh_metadata.tables['stg.settings']
        stg_table = dwh_metadata.tables['stg.api_deliveryman']

        # Получение последней версии из таблицы настроек
        query = select([settings_table.c.settings]).where(
            settings_table.c.setting_key == 'api_deliveryman_last_version')
        result = dwh_session.execute(query).fetchone()
        if result:
            last_version = result['settings']['last_version']
        else:
            last_version = 0
            initial_settings = insert(settings_table).values(
                setting_key='api_deliveryman_last_version',
                settings={'last_version': last_version}
            )
            dwh_session.execute(initial_settings)
            dwh_session.commit()

        # Сохранение данных deliverers в stg.api_deliveryman
        for deliverer in deliverers:
            deliverer_id = deliverer['id']
            deliverer_name = deliverer['name']
            deliverer_json = json.dumps(deliverer, default=str, ensure_ascii=False)

            existing_record = dwh_session.execute(
                select([stg_table]).where(stg_table.c.obj_id == deliverer_id)
            ).fetchone()

            if existing_record:
                # Обновляем существующую запись новой версией
                update_stmt = update(stg_table).where(stg_table.c.obj_id == deliverer_id).values(
                    obj_val=deliverer_name,
                    when_updated=pendulum.now(),
                    version=last_version + 1
                )
                dwh_session.execute(update_stmt)
            else:
                # Вставляем новую запись
                insert_stmt = insert(stg_table).values(
                    obj_id=deliverer_id,
                    obj_val=deliverer_name,
                    when_updated=pendulum.now(),
                    version=last_version + 1
                )
                dwh_session.execute(insert_stmt)

        # Удаление неактуальных версий
        delete_stmt = delete(stg_table).where(stg_table.c.version <= last_version)
        dwh_session.execute(delete_stmt)

        # Обновление последней версии в таблице настроек
        update_settings = update(settings_table).where(
            settings_table.c.setting_key == 'api_deliveryman_last_version'
        ).values(
            settings={'last_version': last_version + 1}
        )
        dwh_session.execute(update_settings)
        dwh_session.commit()

        dwh_session.close()

    def load_deliveryman_data_to_stg(deliverers):
        dwh_session = DwhSession()
        settings_table = dwh_metadata.tables['stg.settings']
        stg_table = dwh_metadata.tables['stg.api_delivery']

        for deliverer in deliverers:
            deliverer_id = deliverer['id']
            deliveries = get_deliveryman_data(deliverer_id)

            # Получение последней версии из таблицы настроек
            query = select([settings_table.c.settings]).where(
                settings_table.c.setting_key == f'api_delivery_{deliverer_id}_last_version')
            result = dwh_session.execute(query).fetchone()
            if result:
                last_version = result['settings']['last_version']
            else:
                last_version = 0
                initial_settings = insert(settings_table).values(
                    setting_key=f'api_delivery_{deliverer_id}_last_version',
                    settings={'last_version': last_version}
                )
                dwh_session.execute(initial_settings)
                dwh_session.commit()

            # Сохранение данных deliveries в stg.api_delivery
            for delivery in deliveries:
                delivery_id = delivery['deliveryId']
                delivery_json = json.dumps(delivery, default=str, ensure_ascii=False)

                existing_record = dwh_session.execute(
                    select([stg_table]).where(stg_table.c.obj_id == delivery_id)
                ).fetchone()

                if existing_record:
                    # Обновляем существующую запись новой версией
                    update_stmt = update(stg_table).where(stg_table.c.obj_id == delivery_id).values(
                        obj_val=delivery_json,
                        when_updated=pendulum.now(),
                        version=last_version + 1
                    )
                    dwh_session.execute(update_stmt)
                else:
                    # Вставляем новую запись
                    insert_stmt = insert(stg_table).values(
                        obj_id=delivery_id,
                        obj_val=delivery_json,
                        when_updated=pendulum.now(),
                        version=last_version + 1
                    )
                    dwh_session.execute(insert_stmt)

            # Удаление неактуальных версий
            delete_stmt = delete(stg_table).where(stg_table.c.version <= last_version)
            dwh_session.execute(delete_stmt)

            # Обновление последней версии в таблице настроек
            update_settings = update(settings_table).where(
                settings_table.c.setting_key == f'api_delivery_{deliverer_id}_last_version'
            ).values(
                settings={'last_version': last_version + 1}
            )
            dwh_session.execute(update_settings)
            dwh_session.commit()

        dwh_session.close()

    @task()
    def load_deliverers_task():
        deliverers = get_deliverers()
        load_deliverers_to_stg(deliverers)
        return deliverers

    @task()
    def load_deliveries_task(deliverers):
        load_deliveryman_data_to_stg(deliverers)

    deliverers = load_deliverers_task()
    load_deliveries_task(deliverers)


api_to_stg_dag = load_api_to_stg()
