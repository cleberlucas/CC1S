from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)
CORS(app)

@app.route('/capture', methods=['POST'])
def get():
    response = ""
    try:
        esp_id = request.json['esp_id']
        user_id = request.json['user_id']
        local = request.json['local']
        door = request.json.get('door')
        
        if not esp_id:
            return jsonify({'message': 'Esp ID parameter is missing'}), 400
        
        if not user_id:
            return jsonify({'message': 'User ID parameter is missing'}), 400
        
        if not local:
            return jsonify({'message': 'Local parameter is missing'}), 400
        
        if not door:
            return jsonify({'message': 'Door parameter is missing'}), 400

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute('''INSERT INTO system_capture (esp_id, user_id, door, `local`) VALUES (%s, %s, %s, %s, %s, %s)''', (id, esp_id, user_id, mac, door, local))
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



