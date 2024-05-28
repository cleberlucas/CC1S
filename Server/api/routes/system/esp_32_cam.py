from flask import Blueprint, request, jsonify
from models import db, SystemEsp32Cam

esp_32_cam_bp = Blueprint('esp_32_cam_bp', __name__)

@esp_32_cam_bp.route('', methods=['POST'])
def create_esp():
    """
    Create a new ESP32 CAM entry
    ---
    tags:
        - ESP32 CAM
    parameters:
      - name: mac
        in: body
        type: string
        required: true
      - name: door
        in: body
        type: string
        enum: ['entrance', 'exit']
      - name: local
        in: body
        type: integer
        required: true
      - name: register_user_id
        in: body
        type: integer
    responses:
      201:
        description: The ID of the created ESP32 CAM entry
        schema:
          type: object
          properties:
            id:
              type: integer
    """
    data = request.json
    new_esp_32_cam = SystemEsp32Cam(
        mac=data['mac'],
        door=data.get('door'),
        local=data['local'],
        register_user_id=data.get('register_user_id')
    )
    db.session.add(new_esp_32_cam)
    db.session.commit()
    return jsonify({'id': new_esp_32_cam.id}), 201

@esp_32_cam_bp.route('/<int:id>', methods=['GET'])
def get_esp(id):
    """
    Get an ESP32 CAM entry by ID
    ---
    tags:
        - ESP32 CAM
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The ESP32 CAM entry data
        schema:
          type: object
          properties:
            id:
              type: integer
            mac:
              type: string
            door:
              type: string
              enum: ['entrance', 'exit']
            local:
              type: integer
            register_user_id:
              type: integer
            last_start:
              type: string
              format: date-time
    """
    esp_32_cam = SystemEsp32Cam.query.get_or_404(id)
    return jsonify({
        'id': esp_32_cam.id,
        'mac': esp_32_cam.mac,
        'door': esp_32_cam.door,
        'local': esp_32_cam.local,
        'register_user_id': esp_32_cam.register_user_id,
        'last_start': esp_32_cam.last_start
    })

@esp_32_cam_bp.route('', methods=['GET'])
def get_all_esps():
    """
    Get all ESP32 CAM entries
    ---
    tags:
        - ESP32 CAM
    responses:
      200:
        description: A list of ESP32 CAM entries
        schema:
          type: array
          items:
            $ref: '#/definitions/ESP32 CAM'
    """
    local_filter = request.args.get('local')
    mac_filter = request.args.get('mac')

    query = SystemEsp32Cam.query

    if local_filter:
        query = query.filter_by(local=local_filter)
    if mac_filter:
        query = query.filter_by(mac=mac_filter)

    esp_32_cams = query.all()

    return jsonify([{
        'id': esp_32_cam.id,
        'mac': esp_32_cam.mac,
        'door': esp_32_cam.door,
        'local': esp_32_cam.local,
        'register_user_id': esp_32_cam.register_user_id,
        'last_start': esp_32_cam.last_start
    } for esp_32_cam in esp_32_cams])
@esp_32_cam_bp.route('/<int:id>', methods=['PUT'])
def update_esp(id):
    """
    Update an ESP32 CAM entry by ID
    ---
    tags:
        - ESP32 CAM
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: mac
        in: body
        type: string
        required: true
      - name: door
        in: body
        type: string
        enum: ['entrance', 'exit']
      - name: local
        in: body
        type: integer
        required: true
      - name: register_user_id
        in: body
        type: integer
    responses:
      200:
        description: Success message
    """
    data = request.json
    esp_32_cam = SystemEsp32Cam.query.get_or_404(id)
    
    if 'mac' in data:
        esp_32_cam.mac = data['mac']
    if 'door' in data:
        esp_32_cam.door = data['door']
    if 'local' in data:
        esp_32_cam.local = data['local']
    if 'register_user_id' in data:
        esp_32_cam.register_user_id = data['register_user_id']
    
    db.session.commit()
    
    return jsonify({'message': 'ESP32 CAM updated successfully'})


@esp_32_cam_bp.route('/<int:id>', methods=['DELETE'])
def delete_esp(id):
    """
    Delete an ESP32 CAM entry by ID
    ---
    tags:
        - ESP32 CAM
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Success message
    """
    esp_32_cam = SystemEsp32Cam.query.get_or_404(id)
    db.session.delete(esp_32_cam)
    db.session.commit()
    return jsonify({'message': 'ESP32 CAM deleted successfully'})
