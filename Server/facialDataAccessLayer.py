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

@app.route('/esp/url/<int:id>', methods=['GET'])
def get_url_by_id(id):
    try:
        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute('''SELECT url FROM esp_info WHERE id = %s''', (id,))
            url = cursor.fetchone()

            if url:
                return jsonify({'url': url[0]})
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
        serialized_face = request.json['serialized_face']

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
        id = request.args.get('id')
        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            if id:
                cursor.execute("SELECT u.`name`, u.id, f.face_img FROM facial_recognition f INNER JOIN user u ON f.user_id = u.id WHERE u.id = %s", (id,))
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

@app.route('/user/exists', methods=['GET'])
def check_user_exists():
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
            cursor.execute("SELECT COUNT(*) FROM user WHERE id = %s", (id,))
            user_exists = cursor.fetchone()[0]
            cursor.close()
            db_connection.close()

            return jsonify({'exists': bool(user_exists)})
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
