from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
from datetime import datetime

# Función para cargar datos en PostgreSQL
def load_data_to_postgres():
    try:
        # Cargar las primeras 1000 filas del archivo
        df = pd.read_csv("/opt/airflow/sales.csv", nrows=1000)
        # Conectar a PostgreSQL
        postgres_hook = PostgresHook(postgres_conn_id='sales_connection')
        conn = postgres_hook.get_conn()
        cursor = conn.cursor()

        # Insertar datos en la tabla Customers
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Customers (CustomerID, CustomerName, Segment, Country, City, State, PostalCode, Region)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (CustomerID) DO NOTHING;
            """, (row['Customer ID'], row['Customer Name'], row['Segment'],
                  row['Country'], row['City'], row['State'],
                  row['Postal Code'], row['Region']))
        
        # Insertar datos en la tabla Products
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Products (ProductID, ProductName, Category, SubCategory, Price)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ProductID) DO NOTHING;
            """, (row['Product ID'], row['Product Name'], row['Category'],
                  row['Sub-Category'], row['Sales'])) 

        # Insertar datos en la tabla Orders
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Orders (OrderID, CustomerID, OrderDate, ShipDate, ShipMode)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (OrderID) DO NOTHING;
            """, (row['Order ID'], row['Customer ID'], row['Order Date'],
                  row['Ship Date'], row['Ship Mode']))
        
        # Insertar datos en la tabla Sales
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Sales (OrderID, OrderDate, ShipDate, ShipMode, CustomerID, ProductID, Sales, Quantity, Discount, Profit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (row['Order ID'], row['Order Date'], row['Ship Date'], row['Ship Mode'],
                  row['Customer ID'], row['Product ID'], row['Sales'], row['Quantity'],
                  row['Discount'], row['Profit']))

        conn.commit()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        cursor.close()
        conn.close()

# Definición del DAG
with DAG('load_all_data_dag', start_date=datetime(2024, 10, 21), schedule_interval='@once') as dag:

    load_data_task = PythonOperator(
        task_id='load_data_to_postgres',
        python_callable=load_data_to_postgres
    )

    load_data_task
