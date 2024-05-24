from sqlalchemy import create_engine


def open_connection():
    server_name = '192.168.20.206\\CE'
    database_name = 'SIOS_PRUEBA'
    username = 'sa'
    password = 'sa1_xxxx'

    connection_string = (
        f'mssql+pyodbc://{username}:{password}@{server_name}/{database_name}?driver=ODBC+Driver+17'
        f'+for+SQL+Server'
    )

    try:
        engine = create_engine(connection_string)
        connection = engine.connect()
        return connection  # Solo se devuelve la conexión
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def close_connection(connection):
    try:
        if connection:
            connection.close()
    except Exception as e:
        print(f"Error al cerrar la conexión: {e}")


def refresh_connection(engine):
    try:
        if engine:
            # Cierra la conexión actual
            engine.dispose()
            # Crea un nuevo engine y una nueva conexión
            new_engine = create_engine(engine.url)
            new_connection = new_engine.connect()
            return new_connection, new_engine
    except Exception as e:
        print(f"Error al Reiniciar la conexión: {e}")
        return None, None

