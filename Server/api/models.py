from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Config:
    with open('../config.json') as f:
        config_data = json.load(f)
        
        SQLALCHEMY_DATABASE_URI = config_data.get('SQLALCHEMY_DATABASE_URI')
        SQLALCHEMY_TRACK_MODIFICATIONS = config_data.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)

class SystemUser(db.Model):
    __tablename__ = 'system_user'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())

class SystemFace(db.Model):
    __tablename__ = 'system_face'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    face_img = db.Column(db.Text, nullable=False)

class SystemCapture(db.Model):
    __tablename__ = 'system_capture'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    door = db.Column(db.Enum('entrance', 'exit'), nullable=False)
    local = db.Column(db.Integer, nullable=False)
    capture_time = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class SystemEsp32Cam(db.Model):
    __tablename__ = 'system_esp_32_cam'
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(17), nullable=False)
    door = db.Column(db.Enum('entrance', 'exit'))
    local = db.Column(db.Integer, nullable=False)
    register_user_id = db.Column(db.Integer)
    last_start = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class SystemEsp8266(db.Model):
    __tablename__ = 'system_esp_8266'
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(17), nullable=False)
    local = db.Column(db.Integer, nullable=False)
    last_start = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

#Domains
class UniversityUser(db.Model):
    __tablename__ = 'university_user'
    rgm = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(250))
    local = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum('student', 'teacher'))

class UniversityClassroom(db.Model):
    __tablename__ = 'university_classroom'
    teacher_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    local = db.Column(db.Integer, nullable=False)
    start_class = db.Column(db.Time, nullable=False)
    end_class = db.Column(db.Time, nullable=False)
    start_interval = db.Column(db.Time, nullable=False)
    end_interval = db.Column(db.Time, nullable=False)
    learning_time = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    __table_args__ = (
        db.PrimaryKeyConstraint('teacher_id', 'date', 'local'), 
    )