import mysql.connector
from mysql.connector import pooling, Error
from config import db_config

connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

def get_db_connection():
    try:
        return connection_pool.get_connection()
    except Error as e:
        return None
