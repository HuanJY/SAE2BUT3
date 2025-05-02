from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
from routes import bp as routes_bp
from llm_download_pdfs2 import download_all_pdfs

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)

app.register_blueprint(routes_bp)

if __name__ == '__main__':
    #from llm import embedding_model
    #from llm_download_pdfs import download_all_pdfs
    from vector_store import embedding_model
    from llm_download_pdfs2 import download_all_pdfs
    
    with app.app_context():
        db.create_all()
        download_all_pdfs(embedding_model) # safe à cet endroit
    app.run(port=5000, debug=True, use_reloader=False)
