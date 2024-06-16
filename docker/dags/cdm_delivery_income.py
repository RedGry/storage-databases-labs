import json
from datetime import datetime
from airflow.decorators import dag, task
import pendulum
from airflow.models import Variable
from airflow.sensors.external_task import ExternalTaskSensor
from sqlalchemy import create_engine, MetaData, select, insert, update, text, and_
from sqlalchemy.orm import sessionmaker

DATABASE_URL_DDS = Variable.get('POSTGRESQL_URI')
DATABASE_URL_CDM = Variable.get('POSTGRESQL_URI')


def period_start_for_date(d):
    if d.day < 21:
        if d.month == 1:
            return datetime(d.year - 1, 12, 21)
        else:
            return datetime(d.year, d.month - 1, 21)
    else:
        return datetime(d.year, d.month, 21)


def period_end_for_date(d):
    if d.day < 21:
        return datetime(d.year, d.month, 21)
    else:
        if d.month == 12:
            return datetime(d.year + 1, 1, 21)
        else:
            return datetime(d.year, d.month + 1, 21)


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2024, 5, 24, tz="UTC"),
    catchup=False,
    tags=['cdm', 'delivery_income'],
    is_paused_upon_creation=False
)
def calculate_deliveryman_income():
    dds_engine = create_engine(DATABASE_URL_DDS)
    cdm_engine = create_engine(DATABASE_URL_CDM)
    DdsSession = sessionmaker(bind=dds_engine)
    CdmSession = sessionmaker(bind=cdm_engine)
    dds_metadata = MetaData()
    cdm_metadata = MetaData()

    dds_metadata.reflect(bind=dds_engine, schema='dds')
    cdm_metadata.reflect(bind=cdm_engine, schema='cdm')

    @task
    def process_deliveryman_income():
        dds_session = DdsSession()
        cdm_session = CdmSession()

        dm_fact_table = dds_metadata.tables['dds.dm_fact_table']
        dm_orders_table = dds_metadata.tables['dds.dm_orders']
        dm_time_table = dds_metadata.tables['dds.dm_time']
        dm_delivery_table = dds_metadata.tables['dds.dm_delivery']
        dm_deliveryman_table = dds_metadata.tables['dds.dm_deliveryman']
        deliveryman_income_table = cdm_metadata.tables['cdm.deliveryman_income']

        # Truncate the deliveryman_income table
        cdm_session.execute(deliveryman_income_table.delete())
        cdm_session.commit()

        now_time = datetime.now()

        # Get the oldest order date
        oldest_order_date_query = select([dm_time_table.c.time_mark]).select_from(
            dm_time_table.join(dm_orders_table, dm_time_table.c.id == dm_orders_table.c.time_id)
        ).where(dm_orders_table.c.status == 'CLOSE').order_by(dm_time_table.c.time_mark).limit(1)

        oldest_order_date_result = dds_session.execute(oldest_order_date_query).fetchone()

        if not oldest_order_date_result:
            return  # No orders found

        oldest_order_date = oldest_order_date_result.time_mark
        current_period_start = period_start_for_date(oldest_order_date)
        current_period_end = period_end_for_date(oldest_order_date)

        if current_period_end > now_time:
            print("Время ещё не настало...")
            return

        while current_period_end < now_time:
            # Query for calculating deliveryman income
            query = select([
                dm_deliveryman_table.c.deliveryman_unique_id.label('deliveryman_id'),
                dm_deliveryman_table.c.name.label('deliveryman_name'),
                text('AVG(dm_delivery.rating) as rating'),
                text('SUM(dm_delivery.tips) as tips'),
                dm_orders_table.c.id.label('order_id'),
                dm_time_table.c.time_mark
            ]).select_from(
                dm_deliveryman_table.join(dm_delivery_table,
                                          dm_deliveryman_table.c.id == dm_delivery_table.c.deliveryman_id)
                .join(dm_orders_table, dm_delivery_table.c.order_id == dm_orders_table.c.id)
                .join(dm_time_table, dm_orders_table.c.time_id == dm_time_table.c.id)
            ).where(
                and_(
                    dm_orders_table.c.status == 'CLOSE',
                    dm_time_table.c.time_mark.between(current_period_start, current_period_end)
                )
            ).group_by(
                dm_deliveryman_table.c.id,
                dm_deliveryman_table.c.name,
                dm_orders_table.c.id,
                dm_time_table.c.time_mark
            )

            results = dds_session.execute(query).fetchall()

            income_data = {}

            for result in results:
                deliveryman_id = result['deliveryman_id']
                deliveryman_name = result['deliveryman_name']
                rating = result['rating']
                tips = result['tips']
                order_id = result['order_id']

                # Calculate orders_total_cost and orders_amount
                orders_total_cost_query = select([
                    text('SUM(dm_fact_table.total_amount) as orders_total_cost')
                ]).select_from(
                    dm_fact_table.join(dm_orders_table, dm_fact_table.c.order_id == dm_orders_table.c.id)
                ).where(
                    dm_fact_table.c.order_id == order_id
                )

                orders_total_cost_result = dds_session.execute(orders_total_cost_query).fetchone()
                orders_total_cost = orders_total_cost_result['orders_total_cost'] if orders_total_cost_result else 0

                if deliveryman_id not in income_data:
                    income_data[deliveryman_id] = {
                        'deliveryman_name': deliveryman_name,
                        'year': current_period_start.year,
                        'month': current_period_start.month,
                        'orders_amount': 0,
                        'orders_total_cost': 0,
                        'rating': 0,
                        'tips': 0,
                        'rating_count': 0
                    }

                income_data[deliveryman_id]['orders_amount'] += 1
                income_data[deliveryman_id]['orders_total_cost'] += orders_total_cost
                income_data[deliveryman_id]['tips'] += tips
                income_data[deliveryman_id]['rating'] += rating
                income_data[deliveryman_id]['rating_count'] += 1

            for deliveryman_id, data in income_data.items():
                if data['rating_count'] > 0:
                    data['rating'] /= data['rating_count']

                deliveryman_income_record = {
                    'deliveryman_id': deliveryman_id,
                    'deliveryman_name': data['deliveryman_name'],
                    'year': data['year'],
                    'month': data['month'],
                    'orders_amount': data['orders_amount'],
                    'orders_total_cost': data['orders_total_cost'],
                    'rating': data['rating'],
                    'tips': data['tips']
                }

                insert_stmt = deliveryman_income_table.insert().values(**deliveryman_income_record)
                cdm_session.execute(insert_stmt)

            # Update the period
            current_period_start = current_period_end
            current_period_end = period_end_for_date(current_period_end)

        cdm_session.commit()
        dds_session.close()
        cdm_session.close()

    # wait_for_dds = ExternalTaskSensor(
    #     task_id='wait_for_dds',
    #     external_dag_id='load_stg_tables_to_dds',
    #     external_task_id=None,
    #     mode='poke',
    #     timeout=120
    # )

    delivery_income_task = process_deliveryman_income()

    # wait_for_dds >> delivery_income_task
    delivery_income_task


cdm_delivery_income_dag = calculate_deliveryman_income()
