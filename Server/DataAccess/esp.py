from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)
CORS(app)

@app.route('/esp', methods=['GET'])
def get():
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
def post():
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

@app.route('/esp/register-mode', methods=['GET'])
def get_register_mode():
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
            register_mode = cursor.fetchone()
            cursor.close()
            db_connection.close()

            if register_mode is not None:
                return jsonify({'register_user_id': register_mode[0]})
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Database connection failed'}), 500

    except mysql.connector.Error as err:
        return jsonify({'message': 'Error executing SQL query: ' + str(err)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



