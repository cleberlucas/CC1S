from flask import Blueprint, request, jsonify
from models import db, SystemEsp8266

esp_8266_bp = Blueprint('esp_8266_bp', __name__)

@esp_8266_bp.route('', methods=['POST'])
def create_esp():
    """
    Create a new ESP-8266 entry
    ---
    parameters:
      - name: mac
        in: body
        type: string
        required: true
      - name: local
        in: body
        type: integer
        required: true
    responses:
      201:
        description: The ID of the created ESP-8266 entry
        schema:
          type: object
          properties:
            id:
              type: integer
    """
    data = request.json
    new_esp_8266 = SystemEsp8266(
        mac=data['mac'],
        local=data['local'],
    )
    db.session.add(new_esp_8266)
    db.session.commit()
    return jsonify({'id': new_esp_8266.id}), 201

@esp_8266_bp.route('/<int:id>', methods=['GET'])
def get_esp(id):
    """
    Get an ESP-8266 entry by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The ESP-8266 entry data
        schema:
          type: object
          properties:
            id:
              type: integer
            mac:
              type: string
            local:
              type: integer
            last_start:
              type: string
              format: date-time
    """
    esp_8266 = SystemEsp8266.query.get_or_404(id)
    return jsonify({
        'id': esp_8266.id,
        'mac': esp_8266.mac,
        'local': esp_8266.local,
        'last_start': esp_8266.last_start
    })

@esp_8266_bp.route('', methods=['GET'])
def get_all_esps():
    """
    Get all ESP-8266 entries
    ---
    responses:
      200:
        description: A list of ESP-8266 entries
        schema:
          type: array
          items:
            $ref: '#/definitions/ESP-8266'
    """
    esp_8266s = SystemEsp8266.query.all()

    local_filter = request.args.get('local')
    if local_filter:
        esp_8266s = SystemEsp8266.query.filter_by(local=local_filter).all()
    else:
        esp_8266s = SystemEsp8266.query.all()

    return jsonify([{
        'id': esp_8266.id,
        'mac': esp_8266.mac,
        'local': esp_8266.local,
        'last_start': esp_8266.last_start
    } for esp_8266 in esp_8266s])

@esp_8266_bp.route('/<int:id>', methods=['PUT'])
def update_esp(id):
    """
    Update an ESP-8266 entry by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: mac
        in: body
        type: string
        required: true
      - name: local
        in: body
        type: integer
        required: true
    responses:
      200:
        description: Success message
    """
    data = request.json
    esp_8266 = SystemEsp8266.query.get_or_404(id)
    esp_8266.mac = data['mac']
    esp_8266.local = data['local']
    db.session.commit()
    return jsonify({'message': 'ESP-8266 updated successfully'})

@esp_8266_bp.route('/<int:id>', methods=['DELETE'])
def delete_esp(id):
    """
    Delete an ESP-8266 entry by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Success message
    """
    esp_8266 = SystemEsp8266.query.get_or_404(id)
    db.session.delete(esp_8266)
    db.session.commit()
    return jsonify({'message': 'ESP-8266 deleted successfully'})
