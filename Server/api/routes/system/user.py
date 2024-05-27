from flask import Blueprint, request, jsonify
from models import db, SystemUser

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    responses:
      201:
        description: The ID of the created user
        schema:
          type: object
          properties:
            id:
              type: integer
    """
    new_user = SystemUser()
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id}), 201

@user_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    """
    Get a user by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The user data
        schema:
          type: object
          properties:
            id:
              type: integer
            created:
              type: string
              format: date-time
    """
    user = SystemUser.query.get_or_404(id)
    return jsonify({'id': user.id, 'created': user.created})

@user_bp.route('', methods=['GET'])
def get_all_users():
    """
    Get all users
    ---
    responses:
      200:
        description: A list of user IDs
        schema:
          type: array
          items:
            type: integer
    """
    users = SystemUser.query.all()
    return jsonify([{
        "id" : user.id
    } for user in users])


@user_bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    """
    Update a user by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: created
        in: body
        type: string
        format: date-time
        required: true
    responses:
      200:
        description: Success message
    """
    data = request.json
    user = SystemUser.query.get_or_404(id)
    user.created = data['created']
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@user_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Delete a user by ID
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: No content
    """
    user = SystemUser.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
