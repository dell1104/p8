# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='usuario')  # admin, usuario, perito
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    assemblyai_key = db.Column(db.String(255), nullable=True)
    ultimo_acceso = db.Column(db.DateTime)
    
    # Relación con casos
    casos = db.relationship('Caso', backref='usuario', lazy=True)
    
    def set_password(self, password):
        """Hash de la contraseña usando bcrypt"""
        import bcrypt
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verificar contraseña"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_admin(self):
        """Verificar si el usuario es administrador"""
        return self.rol == 'admin'
    
    @property
    def es_admin(self):
        """Propiedad para compatibilidad con templates"""
        return self.rol == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Caso(db.Model):
    """Modelo de caso/expediente"""
    __tablename__ = 'casos'
    
    id = db.Column(db.Integer, primary_key=True)
    sesion_id = db.Column(db.String(150), unique=True, nullable=False)
    nombre_caso = db.Column(db.String(150), nullable=False)
    expediente = db.Column(db.String(150), nullable=False)
    numero_informe_tecnico = db.Column(db.String(50), unique=True, nullable=True)
    fecha_intervencion = db.Column(db.Date, nullable=True)
    hora_intervencion = db.Column(db.Time, nullable=True)
    origen_solicitud = db.Column(db.String(200), nullable=True)  # Fiscalía u oficina fiscal
    tipo_requerimiento = db.Column(db.String(100), nullable=True)  # Tipo de análisis requerido
    estado_caso = db.Column(db.String(50), default='En Proceso')  # En Proceso, Completado, Archivado
    observaciones = db.Column(db.Text, nullable=True)
    completado = db.Column(db.Boolean, default=False)
    datos_formulario = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relación con archivos
    archivos = db.relationship('ArchivoCaso', backref='caso', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Caso {self.numero_informe_tecnico}>'

class ArchivoCaso(db.Model):
    """Modelo de archivo asociado a un caso"""
    __tablename__ = 'archivos_caso'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    hash_sha256 = db.Column(db.String(64), nullable=False)
    tipo_archivo = db.Column(db.String(50), nullable=False)  # audio, video, imagen, documento, etc.
    tamaño_bytes = db.Column(db.BigInteger, nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text)
    
    # Clave foránea
    caso_id = db.Column(db.Integer, db.ForeignKey('casos.id'), nullable=False)
    
    def __repr__(self):
        return f'<ArchivoCaso {self.nombre_original}>'

class Transcripcion(db.Model):
    """Modelo de transcripción de audio"""
    __tablename__ = 'transcripciones'
    
    id = db.Column(db.Integer, primary_key=True)
    archivo_original = db.Column(db.String(255), nullable=False)
    hash_archivo = db.Column(db.String(64), nullable=False)
    transcripcion_texto = db.Column(db.Text, nullable=False)
    confianza = db.Column(db.Float)
    idioma = db.Column(db.String(10), default='es')
    modelo_usado = db.Column(db.String(50), default='conversational')
    fecha_transcripcion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_correccion = db.Column(db.DateTime)
    corregida = db.Column(db.Boolean, default=False)
    usuario_correccion_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relación con usuario que corrigió
    usuario_correccion = db.relationship('Usuario', foreign_keys=[usuario_correccion_id])
    
    def __repr__(self):
        return f'<Transcripcion {self.archivo_original}>'

class LogEvento(db.Model):
    """Modelo para logs del sistema"""
    __tablename__ = 'log_eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_evento = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    fecha_evento = db.Column(db.DateTime, default=datetime.utcnow)
    datos_adicionales = db.Column(db.JSON)
    
    # Relación con usuario
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    
    def __repr__(self):
        return f'<LogEvento {self.tipo_evento}>'

class FirmaPermanente(db.Model):
    """Modelo de firma permanente"""
    __tablename__ = 'firmas_permanentes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)
    signature_data = db.Column(db.Text, nullable=False)  # Base64 de la imagen
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_creador = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<FirmaPermanente {self.nombre}>'
