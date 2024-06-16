import json
import time

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from sqlalchemy import create_engine, MetaData, select, insert, update, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import sessionmaker

DATABASE_URL_STG = Variable.get('POSTGRESQL_URI')
DATABASE_URL_DDS = Variable.get('POSTGRESQL_URI')


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2024, 5, 24, tz="UTC"),
    catchup=False,
    tags=['stg', 'dds'],
    is_paused_upon_creation=False
)
def load_stg_tables_to_dds():
    stg_engine = create_engine(DATABASE_URL_STG)
    dds_engine = create_engine(DATABASE_URL_DDS)
    StgSession = sessionmaker(bind=stg_engine)
    DdsSession = sessionmaker(bind=dds_engine)
    stg_metadata = MetaData()
    dds_metadata = MetaData()

    stg_metadata.reflect(bind=stg_engine, schema='stg')
    dds_metadata.reflect(bind=dds_engine, schema='dds')

    def load_table_data(stg_table_name, dds_table_name, unique_key, transform_func):
        stg_session = StgSession()
        dds_session = DdsSession()

        stg_table = stg_metadata.tables[f'stg.{stg_table_name}']
        dds_table = dds_metadata.tables[f'dds.{dds_table_name}']
        settings_table = dds_metadata.tables['dds.settings']

        # Get last loaded update time
        query = select([settings_table.c.settings]).where(
            settings_table.c.setting_key == f'{dds_table_name}_last_update')
        result = dds_session.execute(query).fetchone()

        if result:
            last_update_time = result['settings']['last_update']
        else:
            last_update_time = None
            initial_settings = insert(settings_table).values(
                setting_key=f'{dds_table_name}_last_update',
                settings={'last_update': last_update_time}
            )
            dds_session.execute(initial_settings)
            dds_session.commit()

        if last_update_time is not None:
            query = select([stg_table]).where(stg_table.c.when_updated > text(f"'{last_update_time}'"))
        else:
            query = select([stg_table])

        new_rows = stg_session.execute(query).fetchall()

        for row in new_rows:
            row_dict = dict(row)
            if row_dict.get('obj_id'):
                obj_id = row_dict.get('obj_id')
                obj_val_data = row_dict.get('obj_val')

                try:
                    obj_val_data = json.loads(obj_val_data)
                except json.JSONDecodeError:
                    obj_val_data = {'name': obj_val_data}
                row_dict.update(obj_val_data)
            else:
                obj_id = row_dict.get(unique_key)
            transformed_row = transform_func(obj_id, row_dict)
            insert_stmt = pg_insert(dds_table).values(**transformed_row)
            # insert_stmt = insert(dds_table).values(**transformed_row)
            do_update_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[dds_table.c[unique_key.replace("_", "_unique_")]],
                set_=transformed_row
            )
            dds_session.execute(do_update_stmt)

        if new_rows:
            last_update_time = new_rows[-1][stg_table.c.when_updated]
            update_settings = update(settings_table).where(
                settings_table.c.setting_key == f'{dds_table_name}_last_update'
            ).values(
                settings={'last_update': str(last_update_time)}
            )
            dds_session.execute(update_settings)

        dds_session.commit()
        stg_session.close()
        dds_session.close()

    def transform_category(obj_id, row):
        return {
            'category_unique_id': obj_id,
            'name': row.get('name'),
            'percent': row.get('percent'),
            'min_payment': row.get('min_payment')
        }

    def transform_restaurant(obj_id, row):
        return {
            'restaurant_unique_id': obj_id,
            'name': row['name'],
            'phone': row['phone'],
            'email': row['email'],
            'founding_day': row['founding_day'],
            'menu': row['menu']
        }

    def transform_dish(obj_id, row):
        return {
            'dish_unique_id': obj_id,
            'name': row['name'],
            'price': row['price']
        }

    def transform_deliveryman(obj_id, row):
        return {
            'deliveryman_unique_id': obj_id,
            'name': row['name'],
        }

    def load_clients():
        stg_session = StgSession()
        dds_session = DdsSession()

        mongo_clients_table = stg_metadata.tables['stg.mongo_clients']
        pg_clients_table = stg_metadata.tables['stg.pg_client']
        dds_clients_table = dds_metadata.tables['dds.dm_clients']
        dds_category_table = dds_metadata.tables['dds.dm_category']
        settings_table = dds_metadata.tables['dds.settings']

        # Get last loaded update times for both tables
        query_mongo = select([settings_table.c.settings]).where(
            settings_table.c.setting_key == 'dm_clients_mongo_last_update')
        query_pg = select([settings_table.c.settings]).where(
            settings_table.c.setting_key == 'dm_clients_pg_last_update')

        result_mongo = dds_session.execute(query_mongo).fetchone()
        result_pg = dds_session.execute(query_pg).fetchone()

        last_update_time_mongo = result_mongo['settings']['last_update'] if result_mongo else None
        last_update_time_pg = result_pg['settings']['last_update'] if result_pg else None

        if not result_mongo:
            initial_settings_mongo = insert(settings_table).values(
                setting_key='dm_clients_mongo_last_update',
                settings={'last_update': last_update_time_mongo}
            )
            dds_session.execute(initial_settings_mongo)
            dds_session.commit()

        if not result_pg:
            initial_settings_pg = insert(settings_table).values(
                setting_key='dm_clients_pg_last_update',
                settings={'last_update': last_update_time_pg}
            )
            dds_session.execute(initial_settings_pg)
            dds_session.commit()

        if last_update_time_mongo is not None:
            query_mongo = select([mongo_clients_table]).where(
                mongo_clients_table.c.when_updated > text(f"'{last_update_time_mongo}'"))
        else:
            query_mongo = select([mongo_clients_table])

        if last_update_time_pg is not None:
            query_pg = select([pg_clients_table]).where(
                pg_clients_table.c.when_updated > text(f"'{last_update_time_pg}'"))
        else:
            query_pg = select([pg_clients_table])

        new_mongo_rows = stg_session.execute(query_mongo).fetchall()
        new_pg_rows = stg_session.execute(query_pg).fetchall()

        pg_columns = pg_clients_table.columns.keys()

        mongo_data = {row['obj_id']: json.loads(row['obj_val']) for row in new_mongo_rows}
        pg_data = {row[1]: dict(zip(pg_columns, row)) for row in new_pg_rows}

        combined_data = []
        for client_id in mongo_data:
            if client_id in pg_data:
                mongo_record = mongo_data[client_id]
                pg_record = pg_data[client_id]

                # Fetch the category id from dm_category
                category_query = select([dds_category_table.c.id]).where(
                    dds_category_table.c.category_unique_id == pg_record['category_id'])
                category_result = dds_session.execute(category_query).fetchone()
                if category_result:
                    category_id = category_result['id']
                else:
                    category_id = None

                combined_record = {
                    'client_unique_id': client_id,
                    'name': mongo_record['name'],
                    'phone': mongo_record['phone'],
                    'birthday': mongo_record['birthday'],
                    'email': mongo_record['email'],
                    'login': mongo_record['login'],
                    'address': mongo_record['address'],
                    'bonus_balance': pg_record['bonus_balance'],
                    'category_id': category_id
                }

                combined_data.append(combined_record)

        for row in combined_data:
            insert_stmt = pg_insert(dds_clients_table).values(**row)
            do_update_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[dds_clients_table.c.client_unique_id],
                set_=row
            )
            dds_session.execute(do_update_stmt)

        if new_mongo_rows:
            last_update_time_mongo = new_mongo_rows[-1][mongo_clients_table.c.when_updated]
            update_settings_mongo = update(settings_table).where(
                settings_table.c.setting_key == 'dm_clients_mongo_last_update'
            ).values(
                settings={'last_update': str(last_update_time_mongo)}
            )
            dds_session.execute(update_settings_mongo)

        if new_pg_rows:
            last_update_time_pg = new_pg_rows[-1][pg_clients_table.c.when_updated]
            update_settings_pg = update(settings_table).where(
                settings_table.c.setting_key == 'dm_clients_pg_last_update'
            ).values(
                settings={'last_update': str(last_update_time_pg)}
            )
            dds_session.execute(update_settings_pg)

        dds_session.commit()
        stg_session.close()
        dds_session.close()

    def load_orders():
        stg_session = StgSession()
        dds_session = DdsSession()

        mongo_orders_table = stg_metadata.tables['stg.mongo_orders']
        dds_orders_table = dds_metadata.tables['dds.dm_orders']
        dds_time_table = dds_metadata.tables['dds.dm_time']
        dds_clients_table = dds_metadata.tables['dds.dm_clients']
        dds_restaurants_table = dds_metadata.tables['dds.dm_restaurants']
        settings_table = dds_metadata.tables['dds.settings']

        # Get last loaded update time
        query = select([settings_table.c.settings]).where(settings_table.c.setting_key == 'dm_orders_last_update')
        result = dds_session.execute(query).fetchone()

        if result:
            last_update_time = result['settings']['last_update']
        else:
            last_update_time = None
            initial_settings = insert(settings_table).values(
                setting_key='dm_orders_last_update',
                settings={'last_update': last_update_time}
            )
            dds_session.execute(initial_settings)
            dds_session.commit()

        if last_update_time is not None:
            query = select([mongo_orders_table]).where(
                mongo_orders_table.c.when_updated > text(f"'{last_update_time}'"))
        else:
            query = select([mongo_orders_table])

        new_rows = stg_session.execute(query).fetchall()

        for row in new_rows:
            row_dict = dict(row)
            obj_id = row_dict['obj_id']
            obj_val_data = json.loads(row_dict['obj_val'])
            row_dict.update(obj_val_data)

            # Fetch user_id from dm_clients
            user_query = select([dds_clients_table.c.id]).where(
                dds_clients_table.c.client_unique_id == row_dict['client']['_id'])
            user_result = dds_session.execute(user_query).fetchone()
            if user_result:
                user_id = user_result['id']
            else:
                user_id = None

            # Fetch restaurant_id from dm_restaurants
            restaurant_query = select([dds_restaurants_table.c.id]).where(
                dds_restaurants_table.c.restaurant_unique_id == row_dict['restaurant']['_id'])
            restaurant_result = dds_session.execute(restaurant_query).fetchone()
            if restaurant_result:
                restaurant_id = restaurant_result['id']
            else:
                restaurant_id = None

            # Extract time details from statuses
            time_details = {status['status']: status['time'] for status in row_dict['statuses']}
            final_status_time = time_details.get(row_dict['final_status'])

            if final_status_time:
                time_mark = pendulum.parse(final_status_time)
                time_record = {
                    'time_mark': time_mark,
                    'year': time_mark.year,
                    'month': time_mark.month,
                    'day': time_mark.day,
                    'time': time_mark.time(),
                    'date': time_mark.date()
                }
                time_insert_stmt = pg_insert(dds_time_table).values(**time_record)
                # do_update_stmt = time_insert_stmt.on_conflict_do_update(
                #     index_elements=[dds_time_table.c.time_mark],
                #     set_=time_record
                # )
                result = dds_session.execute(time_insert_stmt)
                time_id = result.inserted_primary_key[0]

                order_record = {
                    'order_unique_id': obj_id,
                    'user_id': user_id,
                    'restaurant_id': restaurant_id,
                    'time_id': time_id,
                    'status': row_dict['final_status']
                }
                order_insert_stmt = pg_insert(dds_orders_table).values(**order_record)
                do_update_order_stmt = order_insert_stmt.on_conflict_do_update(
                    index_elements=[dds_orders_table.c.order_unique_id],
                    set_=order_record
                )
                dds_session.execute(do_update_order_stmt)

        if new_rows:
            last_update_time = new_rows[-1][mongo_orders_table.c.when_updated]
            update_settings = update(settings_table).where(
                settings_table.c.setting_key == 'dm_orders_last_update'
            ).values(
                settings={'last_update': str(last_update_time)}
            )
            dds_session.execute(update_settings)

        dds_session.commit()
        stg_session.close()
        dds_session.close()

    def load_deliveries():
        stg_session = StgSession()
        dds_session = DdsSession()

        api_delivery_table = stg_metadata.tables['stg.api_delivery']
        dds_delivery_table = dds_metadata.tables['dds.dm_delivery']
        dds_orders_table = dds_metadata.tables['dds.dm_orders']
        dds_deliveryman_table = dds_metadata.tables['dds.dm_deliveryman']
        settings_table = dds_metadata.tables['dds.settings']

        # Get last loaded update time
        query = select([settings_table.c.settings]).where(settings_table.c.setting_key == 'dm_delivery_last_update')
        result = dds_session.execute(query).fetchone()

        if result:
            last_update_time = result['settings']['last_update']
        else:
            last_update_time = None
            initial_settings = insert(settings_table).values(
                setting_key='dm_delivery_last_update',
                settings={'last_update': last_update_time}
            )
            dds_session.execute(initial_settings)
            dds_session.commit()

        if last_update_time is not None:
            query = select([api_delivery_table]).where(
                api_delivery_table.c.when_updated > text(f"'{last_update_time}'"))
        else:
            query = select([api_delivery_table])

        new_rows = stg_session.execute(query).fetchall()
        columns = api_delivery_table.columns.keys()

        for row in new_rows:
            row_dict = dict(zip(columns, row))
            obj_val_data = json.loads(row_dict['obj_val'])
            row_dict.update(obj_val_data)

            # Fetch order_id from dm_orders
            order_query = select([dds_orders_table.c.id]).where(
                dds_orders_table.c.order_unique_id == row_dict['orderId'])
            order_result = dds_session.execute(order_query).fetchone()
            if order_result:
                order_id = order_result.id
            else:
                order_id = None

            # Fetch deliveryman_id from dm_deliveryman
            deliveryman_query = select([dds_deliveryman_table.c.id]).where(
                dds_deliveryman_table.c.deliveryman_unique_id == row_dict['deliverymanId'])
            deliveryman_result = dds_session.execute(deliveryman_query).fetchone()
            if deliveryman_result:
                deliveryman_id = deliveryman_result.id
            else:
                deliveryman_id = None

            delivery_record = {
                'delivery_unique_id': row_dict['deliveryId'],
                'order_id': order_id,
                'deliveryman_id': deliveryman_id,
                'delivery_address': row_dict['deliveryAddress'],
                'delivery_time': row_dict['deliveryTime'],
                'rating': row_dict['rating'],
                'tips': row_dict['tips']
            }
            delivery_insert_stmt = pg_insert(dds_delivery_table).values(**delivery_record)
            do_update_stmt = delivery_insert_stmt.on_conflict_do_update(
                index_elements=[dds_delivery_table.c.delivery_unique_id],
                set_=delivery_record
            )
            dds_session.execute(do_update_stmt)

        if new_rows:
            last_update_time = new_rows[-1][api_delivery_table.c.when_updated]
            update_settings = update(settings_table).where(
                settings_table.c.setting_key == 'dm_delivery_last_update'
            ).values(
                settings={'last_update': str(last_update_time)}
            )
            dds_session.execute(update_settings)

        dds_session.commit()
        stg_session.close()
        dds_session.close()

    def load_fact_table():
        stg_session = StgSession()
        dds_session = DdsSession()

        mongo_orders_table = stg_metadata.tables['stg.mongo_orders']
        dds_fact_table = dds_metadata.tables['dds.dm_fact_table']
        dds_orders_table = dds_metadata.tables['dds.dm_orders']
        dds_dish_table = dds_metadata.tables['dds.dm_dish']
        settings_table = dds_metadata.tables['dds.settings']

        # Get last loaded update time
        query = select([settings_table.c.settings]).where(settings_table.c.setting_key == 'dm_fact_table_last_update')
        result = dds_session.execute(query).fetchone()

        if result:
            last_update_time = result['settings']['last_update']
        else:
            last_update_time = None
            initial_settings = insert(settings_table).values(
                setting_key='dm_fact_table_last_update',
                settings={'last_update': last_update_time}
            )
            dds_session.execute(initial_settings)
            dds_session.commit()

        if last_update_time is not None:
            query = select([mongo_orders_table]).where(
                mongo_orders_table.c.when_updated > text(f"'{last_update_time}'"))
        else:
            query = select([mongo_orders_table])

        new_rows = stg_session.execute(query).fetchall()
        columns = mongo_orders_table.columns.keys()

        for row in new_rows:
            row_dict = dict(zip(columns, row))
            obj_val_data = json.loads(row_dict['obj_val'])
            row_dict.update(obj_val_data)

            # Fetch order_id from dm_orders
            order_query = select([dds_orders_table.c.id]).where(
                dds_orders_table.c.order_unique_id == row_dict['obj_id'])
            order_result = dds_session.execute(order_query).fetchone()
            if order_result:
                order_id = order_result['id']
            else:
                order_id = None

            for dish in row_dict['ordered_dishes_mongo']:
                # Fetch dish_id from dm_dish
                dish_query = select([dds_dish_table.c.id]).where(dds_dish_table.c.dish_unique_id == dish['_id'])
                dish_result = dds_session.execute(dish_query).fetchone()
                if dish_result:
                    dish_id = dish_result['id']
                else:
                    dish_id = None

                fact_record = {
                    'dish_id': dish_id,
                    'order_id': order_id,
                    'amount': dish['quantity'],
                    'price': dish['price'],
                    'total_amount': dish['quantity'] * dish['price'],
                    'bonus_payment': row_dict['payed_by_bonuses'],
                    'bonus_grant': row_dict['bonus_for_visit']
                }
                fact_insert_stmt = pg_insert(dds_fact_table).values(**fact_record)
                do_update_stmt = fact_insert_stmt.on_conflict_do_update(
                    index_elements=[dds_fact_table.c.id],
                    set_=fact_record
                )
                dds_session.execute(do_update_stmt)

        if new_rows:
            last_update_time = new_rows[-1][mongo_orders_table.c.when_updated]
            update_settings = update(settings_table).where(
                settings_table.c.setting_key == 'dm_fact_table_last_update'
            ).values(
                settings={'last_update': str(last_update_time)}
            )
            dds_session.execute(update_settings)

        dds_session.commit()
        stg_session.close()
        dds_session.close()

    @task
    def load_category_data():
        time.sleep(10)
        load_table_data('pg_category', 'dm_category', 'category_id', transform_category)

    @task
    def load_restaurant_data():
        load_table_data('mongo_restaurants', 'dm_restaurants', 'restaurant_id', transform_restaurant)

    @task
    def load_dish_data():
        load_table_data('pg_dish', 'dm_dish', 'dish_id', transform_dish)

    @task
    def load_deliveryman_data():
        load_table_data('api_deliveryman', 'dm_deliveryman', 'deliveryman_id', transform_deliveryman)

    @task
    def load_client_data():
        load_clients()

    @task
    def load_orders_data():
        load_orders()

    @task
    def load_delivery_data():
        load_deliveries()

    @task
    def load_fact_table_data():
        load_fact_table()

    category_task = load_category_data()
    client_task = load_client_data()
    restaurant_task = load_restaurant_data()
    dish_task = load_dish_data()
    orders_task = load_orders_data()
    deliveryman_task = load_deliveryman_data()
    delivery_task = load_delivery_data()
    fact_table_task = load_fact_table_data()

    # Define task dependencies
    category_task >> client_task >> [restaurant_task,
                                     dish_task] >> orders_task >> deliveryman_task >> delivery_task >> fact_table_task


pg_to_dds_dag = load_stg_tables_to_dds()
