from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import json

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)

@app.route('/esp/start', methods=['POST'])
def send_ip():
    response = ""
    try:
        url = request.json['url']
        id = request.json['id']
        ssid = request.json['ssid']

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute('''REPLACE INTO esp_info (id, url, ssid) VALUES (%s, %s, %s)''', (id, url, ssid))
            db_connection.commit()
            response = "Success"

    except Error as e:
        response = "An error occurred: " + str(e)

    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            cursor.close()
            db_connection.close()

    return jsonify({'message': response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
