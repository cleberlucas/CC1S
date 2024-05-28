from flask import Blueprint, request, jsonify
from models import db, SystemCapture

capture_bp = Blueprint('capture_bp', __name__)

@capture_bp.route('', methods=['POST'])
def create_capture():
    """
    Create a new capture entry
    ---
    tags:
      - Capture
    parameters:
      - name: user_id
        in: body
        type: integer
        required: true
      - name: door
        in: body
        type: string
        enum: ['entrance', 'exit']
        required: true
      - name: local
        in: body
        type: integer
        required: true
    responses:
      201:
        description: The ID of the created capture entry
        schema:
          type: object
          properties:
            id:
              type: integer
    """
    data = request.json
    new_capture = SystemCapture(
        user_id=data['user_id'],
        door=data['door'],
        local=data['local']
    )
    db.session.add(new_capture)
    db.session.commit()
    return jsonify({'id': new_capture.id}), 201

@capture_bp.route('/<int:id>', methods=['GET'])
def get_capture(id):
    """
    Get a capture entry by ID
    ---
    tags:
      - Capture
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The capture entry data
        schema:
          type: object
          properties:
            id:
              type: integer
            user_id:
              type: integer
            door:
              type: string
              enum: ['entrance', 'exit']
            local:
              type: integer
            capture_time:
              type: string
              format: date-time
    """
    capture = SystemCapture.query.get_or_404(id)
    return jsonify({
        'id': capture.id,
        'user_id': capture.user_id,
        'door': capture.door,
        'local': capture.local,
        'capture_time': capture.capture_time
    })

@capture_bp.route('', methods=['GET'])
def get_all_captures():
    """
    Get all capture entries
    ---
    tags:
      - Capture
    responses:
      200:
        description: A list of capture entries
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              user_id:
                type: integer
              door:
                type: string
                enum: ['entrance', 'exit']
              local:
                type: integer
              capture_time:
                type: string
                format: date-time
    """
    local_filter = request.args.get('local')
    if local_filter:
        captures = SystemCapture.query.filter_by(local=local_filter).all()
    else:
        captures = SystemCapture.query.all()

    return jsonify([{
        'id': capture.id,
        'user_id': capture.user_id,
        'door': capture.door,
        'local': capture.local,
        'capture_time': capture.capture_time
    } for capture in captures])

@capture_bp.route('/<int:id>', methods=['PUT'])
def update_capture(id):
    """
    Update a capture entry by ID
    ---
    tags:
      - Capture
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: user_id
        in: body
        type: integer
        required: true
      - name: door
        in: body
        type: string
        enum: ['entrance', 'exit']
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
    capture = SystemCapture.query.get_or_404(id)
    capture.user_id = data['user_id']
    capture.door = data['door']
    capture.local = data['local']
    db.session.commit()
    return jsonify({'message': 'Capture updated successfully'})

@capture_bp.route('/<int:id>', methods=['DELETE'])
def delete_capture(id):
    """
    Delete a capture entry by ID
    ---
    tags:
      - Capture
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Success message
    """
    capture = SystemCapture.query.get_or_404(id)
    db.session.delete(capture)
    db.session.commit()
    return jsonify({'message': 'Capture deleted successfully'})
