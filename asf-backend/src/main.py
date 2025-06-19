import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db, User
from src.routes.user import user_bp
from src.routes.forum import forum_bp
from src.routes.survey import survey_bp

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asf-consulting-portal-secret-key-2024')
app.config['SESSION_COOKIE_SECURE'] = True  # Doit être True en production avec HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configure CORS for production
# L'URL de votre frontend déployé sur Vercel, Netlify, ou Render Static Site
# Assurez-vous d'ajouter l'URL réelle de votre frontend ici.
# Pour le développement local, 'http://localhost:3000' est toujours utile.
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

CORS(app,
     supports_credentials=True,
     origins=CORS_ORIGINS,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(forum_bp, url_prefix='/api')
app.register_blueprint(survey_bp, url_prefix='/api')

# Database configuration
# Utilisez une variable d'environnement pour la base de données en production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

    # Create default admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@asfconsulting.tn',
            company='ASF Consulting',
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        #print("Default admin user created: admin/admin123")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'message': 'ASF Consulting Portal API is running'}

# Cette partie est modifiée pour la production
# En production, Gunicorn ou un autre serveur WSGI sera utilisé pour lancer l'application.
# Le port sera fourni par l'environnement (Render utilise la variable PORT).
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False en production


