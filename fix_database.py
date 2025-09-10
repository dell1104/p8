#!/usr/bin/env python3
# Script para arreglar la base de datos

from app import create_app
from models import db, Usuario, Caso
import os

def fix_database():
    """Arreglar la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Iniciando reparación de base de datos...")
        
        # Eliminar base de datos existente si hay problemas
        if os.path.exists('database.db'):
            print("📁 Base de datos existente encontrada")
            try:
                # Verificar si las tablas existen
                result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in result]
                print(f"📊 Tablas existentes: {tables}")
            except Exception as e:
                print(f"❌ Error verificando tablas: {e}")
        
        # Crear todas las tablas
        print("🏗️ Creando tablas...")
        db.create_all()
        
        # Verificar que las tablas se crearon
        try:
            result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in result]
            print(f"✅ Tablas creadas: {tables}")
            
            # Verificar usuarios
            user_count = Usuario.query.count()
            print(f"👥 Usuarios en BD: {user_count}")
            
            # Verificar casos
            case_count = Caso.query.count()
            print(f"📁 Casos en BD: {case_count}")
            
            if case_count == 0:
                print("⚠️ No hay casos en la base de datos")
                print("💡 Los casos se crean en las carpetas pero no se guardan en BD")
            
        except Exception as e:
            print(f"❌ Error verificando datos: {e}")
        
        print("✅ Reparación completada")

if __name__ == "__main__":
    fix_database()
