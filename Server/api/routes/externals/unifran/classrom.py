from flask import Blueprint, request, jsonify
from models import db, UnifranUser, UnifranClassroom

externals_unifran_classrom_bp = Blueprint('externals_unifran_classrom_bp', __name__)

@externals_unifran_classrom_bp.route('', methods=['POST'])
def create_classroom():
    """
    Create a new classroom
    ---
    parameters:
      - name: teacher_id
        in: body
        type: integer
        required: true
      - name: date
        in: body
        type: string
        format: date
        required: true
      - name: local
        in: body
        type: integer
        required: true
      - name: start_class
        in: body
        type: string
        format: time
        required: true
      - name: end_class
        in: body
        type: string
        format: time
        required: true
      - name: start_interval
        in: body
        type: string
        format: time
        required: true
      - name: end_interval
        in: body
        type: string
        format: time
        required: true
      - name: learning_time
        in: body
        type: integer
        required: true
    responses:
      201:
        description: Success
        schema:
          type: object
          properties:
            teacher_id:
              type: integer
            date:
              type: string
              format: date
            local:
              type: integer
    """
    data = request.json
    new_classroom = UnifranClassroom(
        teacher_id=data['teacher_id'],
        date=data['date'],
        local=data['local'],
        start_class=data['start_class'],
        end_class=data['end_class'],
        start_interval=data['start_interval'],
        end_interval=data['end_interval'],
        learning_time=data['learning_time']
    )
    db.session.add(new_classroom)
    db.session.commit()
    return jsonify({'teacher_id': new_classroom.teacher_id, 'date': new_classroom.date, 'local': new_classroom.local}), 201

@externals_unifran_classrom_bp.route('/<int:teacher_id>/<string:date>/<int:local>', methods=['GET'])
def get_classroom_by_teacher_and_date(teacher_id, date, local):
    """
    Get a classroom by teacher ID, date, and location
    ---
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
      - name: date
        in: path
        type: string
        format: date
        required: true
      - name: local
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The classroom data
        schema:
          $ref: '#/definitions/UnifranClassroom'
    """
    classroom = UnifranClassroom.query.filter_by(teacher_id=teacher_id, date=date, local=local).first_or_404()
    return jsonify({
        'teacher_id': classroom.teacher_id,
        'date': classroom.date,
        'local': classroom.local,
        'start_class': classroom.start_class.strftime('%H:%M:%S'),
        'end_class': classroom.end_class.strftime('%H:%M:%S'),
        'start_interval': classroom.start_interval.strftime('%H:%M:%S'),
        'end_interval': classroom.end_interval.strftime('%H:%M:%S'),
        'learning_time': classroom.learning_time
    })

@externals_unifran_classrom_bp.route('', methods=['GET'])
def get_all_classrooms():
    """
    Get all classrooms
    ---
    responses:
      200:
        description: A list of classrooms
        schema:
          type: array
          items:
            $ref: '#/definitions/UnifranClassroom'
    """
    classrooms = UnifranClassroom.query.all()
    return jsonify([{
            'teacher_id': classroom.teacher_id,
            'date': classroom.date,
            'local': classroom.local,
            'start_class': classroom.start_class.strftime('%H:%M:%S'),
            'end_class': classroom.end_class.strftime('%H:%M:%S'),
            'start_interval': classroom.start_interval.strftime('%H:%M:%S'),
            'end_interval': classroom.end_interval.strftime('%H:%M:%S'),
            'learning_time': classroom.learning_time
    } for classroom in classrooms])

@externals_unifran_classrom_bp.route('/<int:teacher_id>/<string:date>/<int:local>', methods=['PUT'])
def update_classroom(teacher_id, date, local):
    """
    Update a classroom by teacher ID, date, and location
    ---
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
      - name: date
        in: path
        type: string
        format: date
        required: true
      - name: local
        in: path
        type: integer
        required: true
      - name: start_class
        in: body
        type: string
        format: time
        required: true
      - name: end_class
        in: body
        type: string
        format: time
        required: true
      - name: start_interval
        in: body
        type: string
        format: time
        required: true
      - name: end_interval
        in: body
        type: string
        format: time
        required: true
      - name: learning_time
        in: body
        type: integer
        required: true
    responses:
      200:
        description: Success message
    """
    data = request.json
    classroom = UnifranClassroom.query.filter_by(teacher_id=teacher_id, date=date, local=local).first_or_404()
    classroom.start_class = data['start_class']
    classroom.end_class = data['end_class']
    classroom.start_interval = data['start_interval']
    classroom.end_interval = data['end_interval']
    classroom.learning_time = data['learning_time']
    db.session.commit()
    return jsonify({'message': 'Classroom updated successfully'})

@externals_unifran_classrom_bp.route('/<int:teacher_id>/<string:date>/<int:local>', methods=['DELETE'])
def delete_classroom(teacher_id, date, local):
    """
    Delete a classroom by teacher ID, date, and location
    ---
    parameters:
      - name: teacher_id
        in: path
        type: integer
        required: true
      - name: date
        in: path
        type: string
        format: date
        required: true
      - name: local
        in: path
        type: integer
        required: true
    responses:
      204:
        description: No content
    """
    classroom = UnifranClassroom.query.filter_by(teacher_id=teacher_id, date=date, local=local).first_or_404()
    db.session.delete(classroom)
    db.session.commit()
    return '', 204
