from flask import Blueprint, request, jsonify
from models import db, UniversityUser

domains_university_user_bp = Blueprint('domains_university_user_bp', __name__)

@domains_university_user_bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    tags:
    - University user
    parameters:
      - name: rgm
        in: body
        type: integer
        required: true
      - name: user_id
        in: body
        type: integer
        required: true
      - name: name
        in: body
        type: string
      - name: local
        in: body
        type: integer
        required: true
      - name: type
        in: body
        type: string
        enum: ['student', 'teacher']
        required: true
    responses:
      201:
        description: The ID of the created user
        schema:
          type: object
          properties:
            rgm:
              type: integer
    """
    data = request.json
    new_user = UniversityUser(
        rgm=data['rgm'],
        user_id=data['user_id'],
        name=data.get('name'),
        local=data['local'],
        type=data['type']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'rgm': new_user.rgm}), 201

@domains_university_user_bp.route('/<int:rgm>', methods=['GET'])
def get_user_by_rgm(rgm):
    """
    Get a user by RGM
    ---
    tags:
    - University user
    parameters:
      - name: rgm
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The user data
        schema:
          $ref: '#/definitions/UniversityUser'
    """
    user = UniversityUser.query.filter_by(rgm=rgm).first_or_404()
    return jsonify({
        'rgm': user.rgm,
        'user_id': user.user_id,
        'name': user.name,
        'local': user.local,
        'type': user.type,
    })

@domains_university_user_bp.route('/user_id/<int:user_id>', methods=['GET'])
def get_user_by_user_id(user_id):
    """
    Get a user by User ID
    ---
    tags:
    - University user
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The user data
        schema:
          $ref: '#/definitions/UniversityUser'
    """
    user = UniversityUser.query.filter_by(user_id=user_id).first_or_404()
    return jsonify({
        'rgm': user.rgm,
        'user_id': user.user_id,
        'name': user.name,
        'local': user.local,
        'type': user.type,
    })

@domains_university_user_bp.route('', methods=['GET'])
def get_all_users():
    """
    Get all users
    ---
    tags:
    - University user
    responses:
      200:
        description: A list of users
        schema:
          type: array
          items:
            $ref: '#/definitions/UniversityUser'
    """
    users = UniversityUser.query.all()
    return jsonify([{
        'rgm': user.rgm,
        'user_id': user.user_id,
        'name': user.name,
        'local': user.local,
        'type': user.type,
    } for user in users])

@domains_university_user_bp.route('/<int:rgm>', methods=['PUT'])
def update_user(rgm):
    """
    Update a user by RGM
    ---
    tags:
    - University user
    parameters:
      - name: rgm
        in: path
        type: integer
        required: true
      - name: user_id
        in: body
        type: integer
        required: true
      - name: name
        in: body
        type: string
      - name: local
        in: body
        type: integer
        required: true
      - name: type
        in: body
        type: string
        enum: ['student', 'teacher']
        required: true
    responses:
      200:
        description: Success message
    """
    data = request.json
    user = UniversityUser.query.filter_by(rgm=rgm).first_or_404()
    user.user_id = data['user_id']
    user.name = data.get('name')
    user.local = data['local']
    user.type = data['type']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@domains_university_user_bp.route('/<int:rgm>', methods=['DELETE'])
def delete_user(rgm):
    """
    Delete a user by RGM
    ---
    tags:
    - University user
    parameters:
      - name: rgm
        in: path
        type: integer
        required: true
    responses:
      204:
        description: No content
    """
    user = UniversityUser.query.filter_by(rgm=rgm).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return '', 204
