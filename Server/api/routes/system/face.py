from flask import Blueprint, request, jsonify
from models import db, SystemFace, UniversityUser
import base64

face_bp = Blueprint('face_bp', __name__)

@face_bp.route('', methods=['POST'])
def create_face():
    """
    Create a new face entry
    ---
    parameters:
      - name: user_id
        in: body
        type: integer
        required: true
      - name: face_img
        in: body
        type: string
        format: byte
        required: true
    responses:
      201:
        description: The ID of the created face entry
        schema:
          type: object
          properties:
            id:
              type: integer
    """
    user_id = request.json['user_id']
    face_img = request.json['face_img']
    
    new_face = SystemFace(user_id=user_id, face_img=face_img)
    db.session.add(new_face)
    db.session.commit()
    return jsonify({'id': new_face.id}), 201

@face_bp.route('/<int:id>', methods=['GET'])
def get_face(id):
    """
    Get a face entry by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The face entry data
        schema:
          type: object
          properties:
            id:
              type: integer
            user_id:
              type: integer
            face_img:
              type: string
              format: byte
    """
    face = SystemFace.query.get_or_404(id)

    return jsonify({'id': face.id, 'user_id': face.user_id, 'face_img': face.face_img})

@face_bp.route('', methods=['GET'])
def get_all_faces():
    """
    Get all face entries
    ---
    responses:
      200:
        description: A list of face entries
        schema:
          type: array
          items:
            $ref: '#/definitions/Face'
    """
    local_filter = request.args.get('local')
    if local_filter:
        faces = db.session.query(SystemFace).join(UniversityUser, SystemFace.user_id == UniversityUser.user_id).filter(UniversityUser.local == local_filter).all()
    else:
        faces = SystemFace.query.all()
    
    return jsonify([{
        'id': face.id, 
        'user_id': face.user_id, 
        'face_img': face.face_img
    } for face in faces])

@face_bp.route('/<int:id>', methods=['PUT'])
def update_face(id):
    """
    Update a face entry by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: user_id
        in: body
        type: integer
        required: true
      - name: face_img
        in: body
        type: string
        format: byte
        required: true
    responses:
      200:
        description: Success message
    """
    data = request.json
    face = SystemFace.query.get_or_404(id)
    
    face.user_id = data['user_id']
    face.face_img = data['face_img']
    
    db.session.commit()
    return jsonify({'message': 'Face updated successfully'})

@face_bp.route('/<int:id>', methods=['DELETE'])
def delete_face(id):
    """
    Delete a face entry by ID
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
    face = SystemFace.query.get_or_404(id)
    db.session.delete(face)
    db.session.commit()
    return jsonify({'message': 'Face deleted successfully'})
