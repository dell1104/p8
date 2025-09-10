#!/usr/bin/env python3
# start_secure.py - Script de inicio seguro del sistema forense

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_cors', 'flask_login',
        'bcrypt', 'requests', 'magic', 'flask_limiter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - FALTANTE")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Faltan dependencias: {', '.join(missing_packages)}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def check_directories():
    """Verificar que existan las carpetas necesarias"""
    print("\n📁 Verificando estructura de directorios...")
    
    required_dirs = [
        'casos_data',
        'casos_data/temp',
        'instance',
        'static',
        'templates',
        'blueprints'
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"  📁 Creando directorio: {directory}")
            os.makedirs(directory, exist_ok=True)
        else:
            print(f"  ✅ {directory}")
    
    return True

def check_permissions():
    """Verificar permisos de escritura"""
    print("\n🔐 Verificando permisos...")
    
    test_dirs = ['casos_data', 'instance']
    
    for directory in test_dirs:
        try:
            test_file = os.path.join(directory, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"  ✅ {directory} - Escritura OK")
        except Exception as e:
            print(f"  ❌ {directory} - Sin permisos de escritura: {e}")
            return False
    
    return True

def check_security_config():
    """Verificar configuración de seguridad"""
    print("\n🛡️ Verificando configuración de seguridad...")
    
    # Verificar que exista el archivo de configuración de seguridad
    if not os.path.exists('security_config.py'):
        print("  ❌ security_config.py no encontrado")
        return False
    
    # Verificar que exista el middleware de seguridad
    if not os.path.exists('security_middleware.py'):
        print("  ❌ security_middleware.py no encontrado")
        return False
    
    # Verificar que exista el archivo de log de seguridad
    if not os.path.exists('security.log'):
        print("  📝 Creando archivo de log de seguridad...")
        with open('security.log', 'w') as f:
            f.write(f"# Log de Seguridad - Iniciado el {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("  ✅ Configuración de seguridad OK")
    return True

def generate_secret_key():
    """Generar una clave secreta segura"""
    import secrets
    return secrets.token_hex(32)

def update_secret_key():
    """Actualizar la clave secreta en config.py"""
    print("\n🔑 Verificando clave secreta...")
    
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Verificar si la clave es la por defecto
        if 'tu_clave_secreta_super_segura_aqui_2025' in content:
            print("  ⚠️ Usando clave secreta por defecto - Generando nueva...")
            
            new_key = generate_secret_key()
            content = content.replace(
                "SECRET_KEY = 'tu_clave_secreta_super_segura_aqui_2025'",
                f"SECRET_KEY = '{new_key}'"
            )
            
            with open('config.py', 'w') as f:
                f.write(content)
            
            print(f"  ✅ Nueva clave secreta generada: {new_key[:16]}...")
        else:
            print("  ✅ Clave secreta personalizada encontrada")
        
        return True
    except Exception as e:
        print(f"  ❌ Error actualizando clave secreta: {e}")
        return False

def start_application():
    """Iniciar la aplicación Flask"""
    print("\n🚀 Iniciando aplicación Flask...")
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Iniciar la aplicación
        subprocess.run([sys.executable, 'app.py'], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Aplicación detenida por el usuario")
        return True
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🛡️ SISTEMA FORENSE - INICIO SEGURO")
    print("=" * 50)
    
    # Verificaciones de seguridad
    checks = [
        check_dependencies,
        check_directories,
        check_permissions,
        check_security_config,
        update_secret_key
    ]
    
    for check in checks:
        if not check():
            print("\n❌ Verificación fallida. Corrige los errores antes de continuar.")
            sys.exit(1)
    
    print("\n✅ Todas las verificaciones de seguridad completadas")
    print("🔒 El sistema está listo para iniciar de forma segura")
    
    # Preguntar al usuario si desea continuar
    try:
        response = input("\n¿Iniciar la aplicación? (s/n): ").lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            start_application()
        else:
            print("👋 Inicio cancelado por el usuario")
    except KeyboardInterrupt:
        print("\n👋 Inicio cancelado por el usuario")

if __name__ == "__main__":
    main()
