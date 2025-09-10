# app.py - Versión modularizada
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from security_config import SECURITY_HEADERS
from security_middleware import security_middleware
from config import config
from models import db, Usuario
from blueprints.auth import auth_bp
from blueprints.casos import casos_bp
from blueprints.transcripcion import transcripcion_bp
from blueprints.admin import admin_bp
from blueprints.api import api_bp

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    CORS(app)
    
    # Configurar Rate Limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["1000 per hour", "100 per minute"]
    )
    limiter.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))
    
    # Middleware para headers de seguridad
    @app.after_request
    def add_security_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    # Aplicar middleware de seguridad
    security_middleware(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(casos_bp)
    app.register_blueprint(transcripcion_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Rutas principales
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('index.html')
        return redirect(url_for('auth.login'))
    
    @app.route('/portal-cliente')
    def portal_cliente():
        return render_template('portal_cliente.html')
    
    @app.route('/sala-de-espera')
    def sala_de_espera():
        return render_template('sala-de-espera_sidebar.html')
    
    @app.route('/busqueda')
    def busqueda():
        return render_template('busqueda.html')
    
    @app.route('/gestion-firmas')
    def gestion_firmas():
        return render_template('gestion-firmas.html')
    
    @app.route('/audio-menu')
    def audio_menu():
        return render_template('audio-menu.html')
    
    # Ruta para el favicon (debe ir antes de la ruta general)
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # No Content - evita el error
    
    # Ruta para servir archivos HTML estáticos
    @app.route('/<filename>')
    def serve_html_page(filename):
        # Mapear archivos específicos a sus versiones con sidebar
        template_mapping = {
            'acta.html': 'acta_sidebar.html',
            'formularioacta.html': 'formularioacta_sidebar.html',
            'sala-de-espera.html': 'sala-de-espera_sidebar.html',
            'transcripcion-audios.html': 'transcripcion-audios_sidebar.html'
        }
        
        # Usar el template con sidebar si existe, sino el original
        template_name = template_mapping.get(filename, filename)
        return render_template(template_name)
    
    # Ruta para servir archivos desde casos_data
    @app.route('/casos_data/<path:filename>')
    def serve_casos_data(filename):
        return send_from_directory('casos_data', filename)
    
    @app.route('/api/usuario_actual')
    def get_usuario_actual():
        if current_user.is_authenticated:
            return jsonify({
                'success': True,
                'usuario': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'nombre': current_user.nombre_completo or current_user.username,
                    'email': current_user.email,
                    'rol': current_user.rol
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado'
            }), 401
    
    # Crear tablas de base de datos
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            
            # Crear usuario administrador por defecto si no existe
            if not Usuario.query.filter_by(username='admin').first():
                from utils import log_evento
                import bcrypt
                
                admin_user = Usuario(
                    username='admin',
                    email='admin@sistema.com',
                    nombre_completo='Administrador del Sistema',
                    rol='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Usuario administrador creado (admin/admin123)")
            
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
    
    return app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Crear carpetas necesarias
    os.makedirs('casos_data', exist_ok=True)
    os.makedirs('casos_data/temp', exist_ok=True)
    
    print("🚀 Iniciando aplicación Flask...")
    print("📁 Carpetas creadas: casos_data, casos_data/temp")
    print("🔗 Acceso: http://127.0.0.1:5000")
    print("👤 Usuario admin: admin / admin123")
    
    app.run(host='0.0.0.0', port=5000, debug=True)