from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)
CORS(app)

@app.route('/user', methods=['POST'])
def post():
    try:
        id = request.json['id']
        name = request.json['name']
        local = request.json['local']

        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400

        if not name:
            return jsonify({'message': 'Name parameter is missing'}), 400

        if not local:
            return jsonify({'message': 'Local parameter is missing'}), 400

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute("REPLACE INTO system_user (id, name, local) VALUES (%s, %s, %s)", (id, name, local))
            db_connection.commit()

            cursor.close()
            db_connection.close()

            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except Error as e:
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



