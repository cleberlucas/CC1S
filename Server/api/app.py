from flask import Flask

from flasgger import Swagger
from models import db
from models import Config

def create_app():
    app = Flask(__name__) 
    app.config.from_object(Config)

    db.init_app(app)
    swagger = Swagger(app)

    from routes.system.user import user_bp
    from routes.system.face import face_bp
    from routes.system.capture import capture_bp
    from routes.system.esp_32_cam import esp_32_cam_bp
    from routes.system.esp_8266 import esp_8266_bp
    from routes.externals.unifran.user import externals_unifran_user_bp
    from routes.externals.unifran.classrom import externals_unifran_classrom_bp

    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(face_bp, url_prefix='/face')
    app.register_blueprint(capture_bp, url_prefix='/capture')
    app.register_blueprint(esp_32_cam_bp, url_prefix='/esp-32-cam')
    app.register_blueprint(esp_8266_bp, url_prefix='/esp-8266')
    app.register_blueprint(externals_unifran_user_bp, url_prefix='/externals/unifran/user')
    app.register_blueprint(externals_unifran_classrom_bp, url_prefix='/externals/unifran/classrom')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
