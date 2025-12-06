import mysql.connector
from flask import current_app

def get_connection():
    return mysql.connector.connect(
        host=current_app.config["DB_HOST"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
    )
