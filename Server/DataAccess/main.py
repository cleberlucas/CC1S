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

@app.route('/capture', methods=['POST'])
def capture_post():
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

            cursor.execute('''INSERT INTO system_capture (esp_id, user_id, door, `local`) VALUES (%s, %s, %s, %s)''', (esp_id, user_id, door, local))
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
def esp_get():
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

            cursor.execute('''SELECT url, `local` FROM system_esp WHERE id = %s''', (id,))

            system_esp = cursor.fetchone()

            if system_esp:
                return jsonify({'url': system_esp[0], 'local': system_esp[1]})
            else:
                return jsonify({'message': 'URL not found for the given ID'}), 404

    except Error as e:
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500

    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            cursor.close()
            db_connection.close()

@app.route('/esp', methods=['POST'])
def esp_post():
    response = ""
    try:
        id = request.json['id']
        url = request.json['url']
        ssid = request.json['ssid']
        local = request.json['local']
        mac = request.json['mac']
        door = request.json.get('door')

        if not id:
            return jsonify({'message': 'ID parameter is missing'}), 400
        
        if not url:
            return jsonify({'message': 'URL parameter is missing'}), 400
        
        if not ssid:
            return jsonify({'message': 'SSID parameter is missing'}), 400
        
        if not local:
            return jsonify({'message': 'Local parameter is missing'}), 400
        
        if not mac:
            return jsonify({'message': 'Mac parameter is missing'}), 400

        db_config = config.get("db", {})
        db_connection = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if db_connection.is_connected():
            cursor = db_connection.cursor()

            cursor.execute('''REPLACE INTO system_esp (id, url, ssid, mac, door, `local`) VALUES (%s, %s, %s, %s, %s, %s)''', (id, url, ssid, mac, door, local))
            db_connection.commit()
            response = "Success"

    except Error as e:
        response = "An error occurred: " + str(e)

    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            cursor.close()
            db_connection.close()

    return jsonify({'message': response})

@app.route('/esp/register-user-id', methods=['GET'])
def get_register_mode_get():
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
            cursor.execute("SELECT register_user_id FROM system_esp WHERE id = %s", (id,))
            register_user_id = cursor.fetchone()
            cursor.close()
            db_connection.close()

            if register_user_id is not None:
                return jsonify({'register_user_id': register_user_id[0]})
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except mysql.connector.Error as err:
        return jsonify({'message': 'Error executing SQL query: ' + str(err)}), 500
    
@app.route('/face', methods=['POST'])
def face_post():
    try:
        user_id = request.json.get('user_id')
        serialized_face = request.json.get('serialized_face')

        if not user_id:
            return jsonify({'message': 'ID body is missing'}), 400
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

            cursor.execute("SELECT id FROM system_user WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                cursor.execute("INSERT INTO system_face (user_id, face_img) VALUES (%s, %s)", (user_id, serialized_face))
                db_connection.commit()
                cursor.close()
                db_connection.close()
                return jsonify({'message': 'Face registered successfully'})
            else:
                return jsonify({'message': 'User does not exist'}), 400
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except Error as e:
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500

@app.route('/face', methods=['GET'])
def face_get():
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
                cursor.execute("""
                    SELECT sf.face_img, uu.`name`, uu.user_id
                    FROM system_face sf
                    INNER JOIN system_user su ON sf.user_id = su.id
                    INNER JOIN unifran_user uu ON sf.user_id = uu.user_id
                    WHERE uu.local = %s
                    """, (local,))
            else:
                cursor.execute("""
                    SELECT sf.face_img, uu.`name`, uu.user_id
                    FROM system_face sf
                    INNER JOIN system_user su ON sf.user_id = su.id
                    INNER JOIN unifran_user uu ON sf.user_id = uu.user_id
                    """)
           
            records = cursor.fetchall()

            face_data = []
            for face_img_base64, name, user_id in records:
                try:
                    serialized_face = base64.b64decode(face_img_base64)
                    registered_face = pickle.loads(serialized_face)
                    face_data.append({'name': name, 'user_id': user_id, 'face_img': registered_face.tolist()})
                except pickle.UnpicklingError as e:
                    print("Error decoding face image:", e)

            cursor.close()
            db_connection.close()

            return jsonify({'faces': face_data})
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except mysql.connector.Error as err:
        return jsonify({'message': 'Error executing SQL query: ' + str(err)}), 500
    
@app.route('/user', methods=['POST'])
def user_post():
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



