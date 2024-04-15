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

@app.route('/face', methods=['POST'])
def post():
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

            cursor.execute("SELECT user_id FROM system_user WHERE user_id = %s", (user_id,))
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
def get():
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
                    INNER JOIN unifran_user uu ON su.user_id = uu.user_id
                    WHERE uu.local = %s
                    """, (local,))
            else:
                cursor.execute("""
                    SELECT sf.face_img, uu.`name`, uu.user_id
                    FROM system_face sf
                    INNER JOIN system_user su ON sf.user_id = su.id
                    INNER JOIN unifran_user uu ON su.user_id = uu.user_id
                    """)
           
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



