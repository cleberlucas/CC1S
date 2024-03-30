from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import json

with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__)

@app.route('/enviar-url', methods=['POST'])
def send_ip():
    response = ""
    try:
        url = request.json['url']
        id = request.json['id']
        ssid = request.json['ssid']

        db_config = config.get("db", {})
        conexao_bd = mysql.connector.connect(
            host=db_config.get("host", "localhost"),
            user=db_config.get("user", "root"),
            password=db_config.get("password", ""),
            database=db_config.get("database", "")
        )

        if conexao_bd.is_connected():
            cursor = conexao_bd.cursor()

            cursor.execute('''REPLACE INTO esp_info (id,url, ssid) VALUES (%s,%s, %s)''', (id,url,ssid))
            conexao_bd.commit()
            response = "Endereço IP enviado para o banco de dados."

    except Error as e:
        response = "Ocorreu um erro" + str(e)

    finally:
        if 'conexao_bd' in locals() and conexao_bd.is_connected():
            cursor.close()
            conexao_bd.close()

    return jsonify({'message': response})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
