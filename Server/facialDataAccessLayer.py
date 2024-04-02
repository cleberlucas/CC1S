from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import json
import pickle
import base64

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)

@app.route('/esp/start', methods=['POST'])
def send_ip():
    response = ""
    try:
        id = request.json['id']
        url = request.json['url']
        ssid = request.json['ssid']

        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400
        
        if not url:
            return jsonify({'message': 'URL parameter is missing'}), 400
        
        if not ssid:
            return jsonify({'message': 'Ssid parameter is missing'}), 400

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

@app.route('/esp', methods=['GET'])
def get_url_by_id_and_local():
    try:
        id = request.args.get('id')

        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400
    
        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute('''SELECT url, `local` FROM esp_info WHERE id = %s''', (id,))

            esp_info = cursor.fetchone()

            if esp_info:
                return jsonify({'url': esp_info[0], 'local': esp_info[1]})
            else:
                return jsonify({'message': 'URL not found for the given ID'}), 404

    except Error as e:
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500

    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            cursor.close()
            db_connection.close()

@app.route('/register-face', methods=['POST'])
def register_face():
    try:
        id = request.json['id']
        if not id:
            return jsonify({'message': 'ID body is missing'}), 400
        
        serialized_face = request.json['serialized_face']
        if not serialized_face:
            return jsonify({'message': 'Serialized Face body is missing'}), 400

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute("INSERT INTO facial_recognition (user_id, face_img) VALUES (%s, %s)", (id, serialized_face))
            db_connection.commit()

            cursor.close()
            db_connection.close()

            return jsonify({'message': 'Face registered successfully'})
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except Error as e:
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500

@app.route('/faces', methods=['GET'])
def get_faces():
    try:
        local = request.args.get('local')

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            if local:
                cursor.execute("SELECT u.`name`, u.id, f.face_img FROM facial_recognition f INNER JOIN user u ON f.user_id = u.id WHERE u.local = %s", (id,))
            else:
                cursor.execute("SELECT u.`name`, u.id, f.face_img FROM facial_recognition f INNER JOIN user u ON f.user_id = u.id")
            
            records = cursor.fetchall()

            face_data = []
            for name, user_id, serialized_face_base64 in records:
                serialized_face = base64.b64decode(serialized_face_base64)  # Decodificar a imagem de base64
                registered_face = pickle.loads(serialized_face)
                face_data.append({'name': name, 'user_id': user_id, 'face_img': registered_face.tolist()})

            cursor.close()
            db_connection.close()

            return jsonify({'faces': face_data})
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except mysql.connector.Error as err:
        return jsonify({'message': 'Error executing SQL query: ' + str(err)}), 500

@app.route('/esp/register-mode', methods=['GET'])
def get_esp_register_mode():
    try:
        id = request.args.get('id')
        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()
            cursor.execute("SELECT register_mode FROM esp_info WHERE id = %s", (id,))
            register_mode = cursor.fetchone()
            cursor.close()
            db_connection.close()

            if register_mode is not None:
                return jsonify({'register_mode': bool(register_mode[0])})
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except mysql.connector.Error as err:
        return jsonify({'message': 'Error executing SQL query: ' + str(err)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
