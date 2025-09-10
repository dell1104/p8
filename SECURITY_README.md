# 🛡️ GUÍA DE SEGURIDAD - SISTEMA FORENSE

## ⚠️ IMPORTANTE - LECTURA OBLIGATORIA

Este sistema maneja información sensible y evidencia forense. **DEBE** seguirse esta guía de seguridad para proteger los datos.

## 🚀 INICIO SEGURO

### Para Desarrollo
```bash
python start_secure.py
```

### Para Producción
```bash
# 1. Configurar variables de entorno
export SECRET_KEY="tu_clave_super_secreta_aqui"
export DATABASE_URL="sqlite:///instance/database.db"
export ALLOWED_ORIGINS="https://tu-dominio.com"

# 2. Iniciar con configuración de producción
python app.py
```

## 🔒 MEDIDAS DE SEGURIDAD IMPLEMENTADAS

### 1. **Validación de Archivos**
- ✅ Verificación de tipo MIME real
- ✅ Validación de extensiones permitidas
- ✅ Límite de tamaño (50MB)
- ✅ Nombres de archivo seguros
- ✅ Detección de archivos maliciosos

### 2. **Protección de Inputs**
- ✅ Sanitización de datos del usuario
- ✅ Validación de expedientes
- ✅ Prevención de XSS
- ✅ Prevención de inyección SQL
- ✅ Prevención de path traversal

### 3. **Rate Limiting**
- ✅ Máximo 10 casos por minuto
- ✅ Máximo 20 archivos por minuto
- ✅ Máximo 1000 requests por hora
- ✅ Bloqueo automático de IPs sospechosas

### 4. **Headers de Seguridad**
- ✅ X-Content-Type-Options
- ✅ X-Frame-Options
- ✅ X-XSS-Protection
- ✅ Strict-Transport-Security
- ✅ Content-Security-Policy

### 5. **Sesiones Seguras**
- ✅ Cookies HttpOnly
- ✅ Cookies SameSite
- ✅ Timeout de sesión (1 hora)
- ✅ Protección CSRF

### 6. **Logging de Seguridad**
- ✅ Registro de intentos de ataque
- ✅ Logs de subida de archivos
- ✅ Trazabilidad de usuarios
- ✅ Retención de 90 días

## 📋 CHECKLIST DE SEGURIDAD

### Antes de Iniciar
- [ ] Cambiar `SECRET_KEY` en `config.py`
- [ ] Verificar que `python-magic` esté instalado
- [ ] Crear carpetas `casos_data` y `instance`
- [ ] Verificar permisos de escritura
- [ ] Revisar logs de seguridad

### En Producción
- [ ] Usar HTTPS obligatorio
- [ ] Configurar `SESSION_COOKIE_SECURE = True`
- [ ] Establecer variables de entorno
- [ ] Configurar firewall
- [ ] Monitorear logs de seguridad
- [ ] Respaldos automáticos

## 🚨 ALERTAS DE SEGURIDAD

### Eventos de Alto Riesgo
- Intento de inyección SQL
- Intento de XSS
- Path traversal
- Subida de archivos maliciosos
- Exceso de rate limiting

### Eventos de Riesgo Medio
- Expedientes inválidos
- Archivos rechazados
- Acceso no autorizado
- Datos de formulario inválidos

## 📊 MONITOREO

### Archivos de Log
- `security.log` - Eventos de seguridad
- `application.log` - Logs generales
- `logs/` - Directorio de logs rotativos

### Comandos de Monitoreo
```bash
# Ver eventos de seguridad recientes
tail -f security.log

# Buscar intentos de ataque
grep "ATTACK" security.log

# Ver rate limiting
grep "RATE_LIMIT" security.log
```

## 🔧 CONFIGURACIÓN AVANZADA

### Variables de Entorno Requeridas
```bash
SECRET_KEY=tu_clave_super_secreta_32_caracteres
DATABASE_URL=sqlite:///instance/database.db
ALLOWED_ORIGINS=https://tu-dominio.com
```

### Configuración de Firewall
```bash
# Permitir solo puerto 443 (HTTPS)
ufw allow 443
ufw deny 80
ufw enable
```

### Configuración de Nginx (Recomendado)
```nginx
server {
    listen 443 ssl;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🆘 RESPUESTA A INCIDENTES

### Si Detectas un Ataque
1. **Inmediato**: Bloquear IP en firewall
2. **Revisar**: Logs de seguridad
3. **Analizar**: Tipo de ataque
4. **Documentar**: Todo en security.log
5. **Notificar**: Al administrador del sistema

### Comandos de Emergencia
```bash
# Bloquear IP específica
ufw deny from 192.168.1.100

# Ver conexiones activas
netstat -tulpn | grep :5000

# Reiniciar aplicación
pkill -f "python app.py"
python start_secure.py
```

## 📞 CONTACTO DE SEGURIDAD

- **Administrador**: [Tu nombre]
- **Email**: [tu-email@dominio.com]
- **Teléfono**: [tu-teléfono]
- **Horario**: 24/7 para incidentes críticos

## 🔄 ACTUALIZACIONES DE SEGURIDAD

### Revisar Mensualmente
- [ ] Logs de seguridad
- [ ] Dependencias desactualizadas
- [ ] Configuración de firewall
- [ ] Respaldos de base de datos

### Actualizar Trimestralmente
- [ ] Claves de sesión
- [ ] Certificados SSL
- [ ] Políticas de seguridad
- [ ] Entrenamiento del personal

---

**⚠️ RECUERDA**: La seguridad es responsabilidad de todos. Reporta cualquier comportamiento sospechoso inmediatamente.
