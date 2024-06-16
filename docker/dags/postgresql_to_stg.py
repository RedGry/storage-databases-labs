import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from sqlalchemy import create_engine, MetaData, select, insert, update, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL_SRC = Variable.get('POSTGRESQL_URI')
DATABASE_URL_DWH = Variable.get('POSTGRESQL_URI')


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2024, 5, 24, tz="UTC"),
    catchup=False,
    tags=['postgres', 'stg'],
    is_paused_upon_creation=False
)
def load_pg_tables_to_stg():
    src_engine = create_engine(DATABASE_URL_SRC)
    dwh_engine = create_engine(DATABASE_URL_DWH)
    Session = sessionmaker(bind=src_engine)
    DwhSession = sessionmaker(bind=dwh_engine)
    src_metadata = MetaData()
    dwh_metadata = MetaData()

    src_metadata.reflect(bind=src_engine, schema='public')
    dwh_metadata.reflect(bind=dwh_engine, schema='stg')

    def load_table_data(table_name, stg_table_name):
        src_session = Session()
        dwh_session = DwhSession()

        source_table = src_metadata.tables[f'public.{table_name}']
        stg_table = dwh_metadata.tables[f'stg.{stg_table_name}']
        settings_table = dwh_metadata.tables['stg.settings']

        # Get last loaded ID
        query = select([settings_table.c.settings]).where(settings_table.c.setting_key == f'{stg_table_name}_last_id')
        result = dwh_session.execute(query).fetchone()

        if result:
            last_id = result['settings']['last_id']
        else:
            # Initialize settings if the table is empty
            last_id = None
            initial_settings = insert(settings_table).values(
                setting_key=f'{stg_table_name}_last_id',
                settings={'last_id': last_id}
            )
            dwh_session.execute(initial_settings)
            dwh_session.commit()

        key_id = getattr(source_table.c, table_name + "_id")
        # query = select(source_table).where(key_id > last_id)
        # new_rows = src_session.execute(query).fetchall()
        if last_id is not None:
            if isinstance(last_id, int):
                query = select([source_table]).where(key_id > last_id)
            else:
                query = select([source_table]).where(key_id > text(f"'{last_id}'"))
        else:
            query = select([source_table])
        new_rows = src_session.execute(query).fetchall()

        for row in new_rows:
            insert_stmt = stg_table.insert().values(
                **row,
                when_update=pendulum.now()
            )
            dwh_session.execute(insert_stmt)

        if new_rows:
            last_id = new_rows[-1][key_id]
            existing_setting = dwh_session.execute(
                select([settings_table.c.setting_key]).where(
                    settings_table.c.setting_key == f'{stg_table_name}_last_id')
            ).fetchone()

            if existing_setting:
                update_settings = update(settings_table).where(
                    settings_table.c.setting_key == f'{stg_table_name}_last_id'
                ).values(
                    settings={'last_id': last_id}
                )
                dwh_session.execute(update_settings)
            else:
                insert_settings = insert(settings_table).values(
                    setting_key=f'{stg_table_name}_last_id',
                    settings={'last_id': last_id}
                )
                dwh_session.execute(insert_settings)

        dwh_session.commit()
        src_session.close()
        dwh_session.close()

    @task
    def load_category_data():
        load_table_data('category', 'pg_category')

    @task
    def load_dish_data():
        load_table_data('dish', 'pg_dish')

    @task
    def load_client_data():
        load_table_data('client', 'pg_client')

    category_task = load_category_data()
    dish_task = load_dish_data()
    client_task = load_client_data()

    category_task >> [dish_task, client_task]


pg_tables_dag = load_pg_tables_to_stg()
