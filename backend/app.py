from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
from routes import bp as routes_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)

app.register_blueprint(routes_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)