from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json
import pickle
import base64

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)
CORS(app)

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

@app.route('/esp', methods=['POST'])
def send_ip():
    response = ""
    try:
        id = request.json['id']
        url = request.json['url']
        ssid = request.json['ssid']
        local = request.json['local']

        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400
        
        if not url:
            return jsonify({'message': 'URL parameter is missing'}), 400
        
        if not ssid:
            return jsonify({'message': 'Ssid parameter is missing'}), 400
        
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

            cursor.execute('''REPLACE INTO esp_info (id, url, ssid,`local`) VALUES (%s, %s, %s, %s)''', (id, url, ssid, local))
            db_connection.commit()
            response = "Success"

    except Error as e:
        response = "An error occurred: " + str(e)

    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            cursor.close()
            db_connection.close()

    return jsonify({'message': response})

@app.route('/esp/user-id-register', methods=['GET'])
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
            cursor.execute("SELECT user_id_register FROM esp_info WHERE id = %s", (id,))
            register_mode = cursor.fetchone()
            cursor.close()
            db_connection.close()

            if register_mode is not None:
                return jsonify({'user_id_register': register_mode[0]})
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except mysql.connector.Error as err:
        return jsonify({'message': 'Error executing SQL query: ' + str(err)}), 500

@app.route('/esp/user-id-register', methods=['PUT'])
def update_esp_register_mode():
    try:
        id = request.json['id']
        user_id_register = request.json['user_id_register']

        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400

        if not user_id_register:
            return jsonify({'message': 'User ID Register parameter is missing'}), 400

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute("UPDATE esp_info SET user_id_register = %s WHERE id = %s", (user_id_register, id))
            db_connection.commit()

            cursor.close()
            db_connection.close()

            return jsonify({'message': 'User ID Register updated successfully'})
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except Error as e:
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500


@app.route('/face', methods=['POST'])
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

@app.route('/face', methods=['GET'])
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
                cursor.execute("SELECT u.`name`, u.id, f.face_img FROM facial_recognition f INNER JOIN user u ON f.user_id = u.id WHERE u.local = %s", (local,))
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

@app.route('/user', methods=['POST'])
def register_user():
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

            cursor.execute("REPLACE INTO user (id, name, local) VALUES (%s, %s, %s)", (id, name, local))
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



