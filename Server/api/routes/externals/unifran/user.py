from flask import Blueprint, request, jsonify
from models import db, UnifranUser

externals_unifran_user_bp = Blueprint('externals_unifran_user_bp', __name__)

@externals_unifran_user_bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
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
    new_user = UnifranUser(
        rgm=data['rgm'],
        user_id=data['user_id'],
        name=data.get('name'),
        local=data['local'],
        type=data['type']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'rgm': new_user.rgm}), 201

@externals_unifran_user_bp.route('/<int:rgm>', methods=['GET'])
def get_user_by_rgm(rgm):
    """
    Get a user by RGM
    ---
    parameters:
      - name: rgm
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The user data
        schema:
          $ref: '#/definitions/UnifranUser'
    """
    user = UnifranUser.query.filter_by(rgm=rgm).first_or_404()
    return jsonify({
        'rgm': user.rgm,
        'user_id': user.user_id,
        'name': user.name,
        'local': user.local,
        'type': user.type,
    })

@externals_unifran_user_bp.route('', methods=['GET'])
def get_all_users():
    """
    Get all users
    ---
    responses:
      200:
        description: A list of users
        schema:
          type: array
          items:
            $ref: '#/definitions/UnifranUser'
    """
    users = UnifranUser.query.all()
    return jsonify([{
        'rgm': user.rgm,
        'user_id': user.user_id,
        'name': user.name,
        'local': user.local,
        'type': user.type,
    } for user in users])

@externals_unifran_user_bp.route('/<int:rgm>', methods=['PUT'])
def update_user(rgm):
    """
    Update a user by RGM
    ---
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
    user = UnifranUser.query.filter_by(rgm=rgm).first_or_404()
    user.user_id = data['user_id']
    user.name = data.get('name')
    user.local = data['local']
    user.type = data['type']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@externals_unifran_user_bp.route('/<int:rgm>', methods=['DELETE'])
def delete_user(rgm):
    """
    Delete a user by RGM
    ---
    parameters:
      - name: rgm
        in: path
        type: integer
        required: true
    responses:
      204:
        description: No content
    """
    user = UnifranUser.query.filter_by(rgm=rgm).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return '', 204
