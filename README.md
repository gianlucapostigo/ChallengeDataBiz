```## 1.Requisitos

- **Docker**: Asegúrate de tener Docker instalado en tu máquina.
- **Python**: Este proyecto utiliza Python y se recomienda tener una versión reciente instalada.

## 2.Estructura del Proyecto
prueba_challenge/
│
├── .venv/                     # Entorno virtual
│
├── config/                    # Configuraciones de Airflow
│
├── dags/                      # Archivos de DAG de Airflow
│   └── dag.py                 # Tu archivo DAG principal
│
├── logs/                      # Archivos de registro de Airflow
│
├── plugins/                   # Complementos de Airflow
│
├── docker-compose.yaml         # Configuración de Docker
│
└── README.md                  # Documentación del proyecto

## 3. Instalación de Dependencias

Para instalar las dependencias necesarias para este proyecto, asegúrate de que el entorno virtual esté activo y ejecuta:

```bash
pip install -r requirements.txt

## Configuración de Docker

Este proyecto utiliza Docker para orquestar los servicios necesarios para construir el Data Warehouse. A continuación se describe la configuración de `docker-compose.yaml`.

### 4. Servicios

- **PostgreSQL**: Base de datos donde se almacenarán los datos transformados.
  - **Usuario**: `airflow`
  - **Contraseña**: `airflow`
  - **Base de Datos**: `airflow`
  
- **pgAdmin**: Interfaz web para gestionar PostgreSQL.
  - **Acceder en**: `http://localhost:5050`
  - **Email**: `admin@admin.com`
  - **Contraseña**: `root`

- **Redis**: Utilizado como broker para la ejecución de tareas en Airflow.

- **Apache Airflow**: Sistema de orquestación de flujos de trabajo.
  - **Acceder en**: `http://localhost:8080`
  - **Usuario**: `airflow`
  - **Contraseña**: `airflow`

### 5.Iniciar los Servicios

Para iniciar todos los servicios, ejecuta el siguiente comando en la terminal:

docker-compose up -d

## 6. Creacion y Coneccion de Base de datos:
Para crear un server necesitamos el IpAddress del contenedor de docker para esto ejecutamos:
-docker ps (copiar el que tiene "-airflow-webserver-1")
-docker inspect prueba_challenge-postgres-1 | grep "IPAddress"
Esto deberia salir:
"SecondaryIPAddresses": null,
            "IPAddress": "",
                    "IPAddress": "172.19.0.3", (usaremos esto)

En esta parte tuve problemas de conexion asi que decidi buscar alternativas y encontre esto:

1. Se accedió al contenedor de PostgreSQL para verificar y editar la configuración:
- docker exec -it prueba_challenge-postgres-1 /bin/bash

2. Se copió el archivo pg_hba.conf desde el contenedor a la máquina local para su edición.
- docker cp prueba_challenge-postgres-1:/var/lib/postgresql/data/pg_hba.conf ./pg_hba.conf

3. Edición del Archivo pg_hba.conf:
- Se abrió el archivo pg_hba.conf en un editor de texto y se agregó la siguiente línea para permitir conexiones desde cualquier dirección IP usando autenticación md5:
plaintext
Copiar código
host    all             all             0.0.0.0/0               md5

4. Copie del Archivo Editado de Vuelta al Contenedor:
-docker cp ./pg_hba.conf prueba_challenge-postgres-1:/var/lib/postgresql/data/pg_hba.conf

5. Se reinició el contenedor de PostgreSQL para aplicar los cambios realizados en la configuración.
- docker-compose restart postgres

6. Prueba de Conexión:
Se verificó la conexión a PostgreSQL utilizando un cliente (pgAdmin) con la siguiente información:
Host: Dirección IP del contenedor.
Puerto: 5432
Usuario: airflow
Contraseña: airflow
##Reflexion: 
Se logró configurar PostgreSQL para aceptar conexiones externas con éxito.
La configuración permite la conexión desde cualquier dirección IP, lo cual es útil para el desarrollo.

##7. Creacion de tablas en SQL:
- Creamos una nueva base de datos llamada sales

- Insertamos los queries en el Query tool:
CREATE TABLE Sales (
    RowID SERIAL PRIMARY KEY,
    OrderID VARCHAR(20),
    OrderDate DATE,
    ShipDate DATE,
    ShipMode VARCHAR(50),
    CustomerID VARCHAR(20),
    ProductID VARCHAR(20),
    Sales NUMERIC(10, 2),
    Quantity INT,
    Discount NUMERIC(5, 2),
    Profit NUMERIC(10, 2) 
);

CREATE TABLE Customers (
    CustomerID VARCHAR(20) PRIMARY KEY,
    CustomerName VARCHAR(255),
    Segment VARCHAR(50),
    Country VARCHAR(50),
    City VARCHAR(50),
    State VARCHAR(50),
    PostalCode VARCHAR(20),
    Region VARCHAR(50)
);

CREATE TABLE Products (
    ProductID VARCHAR(20) PRIMARY KEY,
    ProductName VARCHAR(255),
    Category VARCHAR(50),
    SubCategory VARCHAR(50),
    Price NUMERIC(10, 2) 
);

CREATE TABLE Orders (
    OrderID VARCHAR(20) PRIMARY KEY,
    CustomerID VARCHAR(20),
    OrderDate DATE,
    ShipDate DATE,
    ShipMode VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

7. Creacion del DAG: 

- Importación de Módulos: Importé las bibliotecas necesarias de Airflow y Pandas en el archivo dag.py, incluyendo DAG, PythonOperator y PostgresHook para facilitar la conexión con PostgreSQL.

- Definición de la Función: Definí la función load_data_to_postgres, la cual se encarga de:

- Leer las primeras 1000 filas del archivo CSV sales.csv utilizando Pandas.
Conectar a la base de datos PostgreSQL utilizando PostgresHook.
Insertar los datos leídos en las tablas correspondientes: Customers, Products, Orders y Sales, utilizando comandos SQL con gestión de conflictos para evitar duplicados.
Configuración del DAG:

- Definí el DAG utilizando el contexto with DAG(...) donde establecí el nombre del DAG (load_all_data_dag), la fecha de inicio y la programación (schedule_interval='@once' para que se ejecute una sola vez).

- Utilicé PythonOperator para ejecutar la función load_data_to_postgres como una tarea dentro del DAG.
Ejecución: La tarea se ejecuta automáticamente cuando se activa el DAG en Airflow, lo que permite cargar los datos de manera organizada en la base de datos.