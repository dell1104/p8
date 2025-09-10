# transcripcion_audio.py
# Funcionalidad de transcripción de audios de WhatsApp integrada desde V1.2

import requests
import time
import hashlib
import os
from datetime import datetime
from pathlib import Path
from flask import request, jsonify, current_app
import json

def calcular_hash_sha256(archivo_path):
    """Calcula el hash SHA256 de un archivo"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(archivo_path, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                hash_sha256.update(bloque)
        return hash_sha256.hexdigest()
    except Exception as e:
        return f"Error al calcular hash: {str(e)}"

def upload_and_transcribe(archivo_path, assemblyai_key):
    """Sube un archivo de audio a AssemblyAI y inicia la transcripción"""
    try:
        # Verificar que el archivo existe y obtener información
        if not os.path.exists(archivo_path):
            return None, None, f"El archivo {archivo_path} no existe"
        
        file_size = os.path.getsize(archivo_path)
        print(f"📁 Archivo: {archivo_path}")
        print(f"📁 Tamaño: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
        
        # Verificar tamaño del archivo (AssemblyAI tiene límites)
        if file_size > 100 * 1024 * 1024:  # 100MB
            return None, None, f"El archivo es demasiado grande ({file_size / (1024*1024):.2f} MB). Máximo 100MB"
        
        if file_size == 0:
            return None, None, "El archivo está vacío"
        
        # Verificar extensión del archivo
        file_ext = os.path.splitext(archivo_path)[1].lower()
        supported_formats = ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.opus']
        
        if file_ext not in supported_formats:
            print(f"⚠️ Formato de archivo no estándar: {file_ext}")
            print(f"⚠️ Formatos soportados: {supported_formats}")
            # Continuar de todas formas, AssemblyAI puede manejar algunos formatos no listados
        
        headers = {'authorization': assemblyai_key}
        print(f"🔑 Headers enviados: authorization={assemblyai_key[:8]}...")
        
        # Subir archivo
        print(f"📤 Enviando archivo a AssemblyAI...")
        with open(archivo_path, 'rb') as f:
            response_upload = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=f)
        
        print(f"📤 Respuesta de upload: {response_upload.status_code}")
        print(f"📤 Contenido de respuesta: {response_upload.text}")
        
        if response_upload.status_code == 422:
            return None, None, f"Error 422 - Archivo no válido: {response_upload.text}. Posibles causas: formato no soportado, archivo corrupto, o tamaño excesivo."
        elif response_upload.status_code != 200:
            return None, None, f"Error subiendo: {response_upload.text}"
        
        upload_url = response_upload.json()['upload_url']
        print(f"✅ Upload URL obtenida: {upload_url}")
        
        # Crear transcripción usando el formato correcto de AssemblyAI (como en v1.2)
        json_payload = {
            'audio_url': upload_url, 
            'language_code': 'es',  # Especificar idioma español
            'speaker_labels': True  # Habilitar identificación de hablantes
        }
        print(f"📝 Creando transcripción con payload: {json_payload}")
        response_transcript = requests.post('https://api.assemblyai.com/v2/transcript', headers=headers, json=json_payload)
        
        print(f"📝 Respuesta de transcript: {response_transcript.status_code}")
        print(f"📝 Contenido de respuesta: {response_transcript.text}")
        
        if response_transcript.status_code != 200:
            return None, None, f"Error creando transcripción: {response_transcript.text}"
        
        transcript_id = response_transcript.json()['id']
        print(f"✅ Transcript ID obtenido: {transcript_id}")
        return upload_url, transcript_id, None
        
    except Exception as e:
        print(f"❌ Excepción en upload_and_transcribe: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, f"Error en upload_and_transcribe: {str(e)}"

def poll_for_transcript(transcript_id, assemblyai_key):
    """Obtiene el resultado de la transcripción"""
    try:
        headers = {'authorization': assemblyai_key}
        polling_endpoint = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
        
        print(f"⏳ Polling endpoint: {polling_endpoint}")
        
        while True:
            time.sleep(3)  # Reducir tiempo de espera
            response = requests.get(polling_endpoint, headers=headers)
            
            print(f"🔄 Status check: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error en polling: {response.text}")
                return None, f"Error obteniendo transcripción: {response.text}"
            
            data = response.json()
            status = data.get('status', 'unknown')
            print(f"📊 Status: {status}")
            
            if status == 'completed':
                transcript_text = data.get('text', '')
                print(f"✅ Transcripción completada: {len(transcript_text)} caracteres")
                
                # Intentar usar utterances si están disponibles
                if 'utterances' in data and data['utterances']:
                    transcripcion = "\n".join([f"Hablante {u['speaker']}: {u['text']}" for u in data['utterances']])
                    print(f"✅ Transcripción con speakers: {len(transcripcion)} caracteres")
                    return transcripcion, None
                
                return transcript_text, None
            elif status == 'error':
                error_msg = data.get('error', 'Error desconocido')
                print(f"❌ Error en transcripción: {error_msg}")
                return None, f"Error: {error_msg}"
            else:
                print(f"⏳ Esperando... (status: {status})")
                continue
                
    except Exception as e:
        return None, f"Error en poll_for_transcript: {str(e)}"

def procesar_audio_individual(archivo_path, assemblyai_key):
    """Procesa un archivo de audio individual y retorna la transcripción"""
    try:
        # Calcular hash del archivo
        hash_archivo = calcular_hash_sha256(archivo_path)
        
        # Verificar que la clave API no esté vacía
        print(f"🔑 Clave AssemblyAI recibida: {'Configurada' if assemblyai_key else 'No configurada'}")
        print(f"🔑 Longitud de la clave: {len(assemblyai_key) if assemblyai_key else 0}")
        print(f"🔑 Primeros 8 caracteres: {assemblyai_key[:8] if assemblyai_key else 'N/A'}")
        
        if not assemblyai_key or assemblyai_key.strip() == "":
            return None, "Clave API de AssemblyAI no proporcionada", hash_archivo
        
        # Verificar formato de la clave (debería ser alfanumérica de 32 caracteres)
        if len(assemblyai_key) != 32 or not assemblyai_key.isalnum():
            print(f"⚠️ Formato de clave sospechoso: longitud={len(assemblyai_key)}, alfanumérica={assemblyai_key.isalnum()}")
            return None, f"Formato de clave API inválido. Longitud: {len(assemblyai_key)}", hash_archivo
        
        # Subir y transcribir
        print(f"📤 Subiendo archivo: {archivo_path}")
        upload_url, transcript_id, error = upload_and_transcribe(archivo_path, assemblyai_key)
        if error:
            print(f"❌ Error en upload_and_transcribe: {error}")
            return None, error, hash_archivo
        
        print(f"✅ Archivo subido exitosamente. Transcript ID: {transcript_id}")
        
        # Esperar resultado
        print(f"⏳ Esperando transcripción...")
        transcripcion, error = poll_for_transcript(transcript_id, assemblyai_key)
        if error:
            print(f"❌ Error en poll_for_transcript: {error}")
            return None, error, hash_archivo
        
        print(f"✅ Transcripción completada: {len(transcripcion) if transcripcion else 0} caracteres")
        return transcripcion, None, hash_archivo
        
    except Exception as e:
        print(f"Error en procesar_audio_individual: {e}")
        import traceback
        traceback.print_exc()
        return None, f"Error general: {str(e)}", None

def cargar_chat_whatsapp(archivo_path):
    """Carga un archivo de chat de WhatsApp"""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.readlines()
        return contenido, None
    except Exception as e:
        return None, f"Error al cargar chat: {str(e)}"

def insertar_transcripcion_en_chat(chat_lines, nombre_audio, transcripcion, hash_audio):
    """Inserta una transcripción en el chat de WhatsApp"""
    try:
        nuevo_chat = []
        insertado = False
        
        for linea in chat_lines:
            nuevo_chat.append(linea)
            # Buscar la línea que contiene el nombre del audio
            if nombre_audio in linea and "(Transcripción:" not in linea and not insertado:
                nuevo_chat.append(f"    (Transcripción: {transcripcion})\n")
                nuevo_chat.append(f"    (SHA-256 del audio: {hash_audio})\n")
                insertado = True
        
        if not insertado:
            return None, f"No se encontró línea para '{nombre_audio}' o ya fue insertada"
        
        return nuevo_chat, None
        
    except Exception as e:
        return None, f"Error al insertar transcripción: {str(e)}"

def parsear_chat_whatsapp(chat_lines):
    """Parsea un chat de WhatsApp y encuentra archivos de audio"""
    import re
    
    archivos_audio = []
    patron_audio = re.compile(r'(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}) - ([^:]+): ‎([A-Z]{3}-\d{8}-WA\d{4}\.(mp3|wav|m4a|ogg|opus|aac)) \(archivo adjunto\)')
    
    for i, linea in enumerate(chat_lines):
        match = patron_audio.search(linea)
        if match:
            fecha_hora = match.group(1)
            remitente = match.group(2)
            archivo = match.group(3)
            extension = match.group(4)
            
            archivos_audio.append({
                'linea': i,
                'fecha_hora': fecha_hora,
                'remitente': remitente,
                'archivo': archivo,
                'extension': extension,
                'contenido_linea': linea.strip()
            })
    
    return archivos_audio

def insertar_transcripcion_en_chat_whatsapp(chat_lines, nombre_audio, transcripcion, hash_audio):
    """Inserta una transcripción en un chat de WhatsApp específicamente"""
    import re
    
    # Buscar la línea que contiene el archivo de audio
    patron_audio = re.compile(r'(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}) - ([^:]+): ‎([A-Z]{3}-\d{8}-WA\d{4}\.(mp3|wav|m4a|ogg|opus|aac)) \(archivo adjunto\)')
    
    for i, linea in enumerate(chat_lines):
        match = patron_audio.search(linea)
        if match and nombre_audio in match.group(3):
            # Insertar la transcripción después de esta línea
            chat_lines.insert(i + 1, f"   📝 Transcripción: {transcripcion}\n")
            chat_lines.insert(i + 2, f"   🔐 SHA-256: {hash_audio}\n")
            return True
    
    return False

def log_evento(analista, accion, detalles):
    """Registra un evento forense (versión simplificada)"""
    try:
        log_entry = {
            "timestamp_utc": datetime.utcnow().isoformat(),
            "analista": analista,
            "accion": accion,
            "detalles": detalles
        }
        
        # Crear directorio de logs si no existe
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Escribir log
        log_file = os.path.join(log_dir, f"log_sesion_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    except Exception as e:
        print(f"Error al escribir log: {e}")

def procesar_lote_audios(archivos, assemblyai_key, analista, caso_expediente):
    """Procesa múltiples archivos de audio en lote"""
    resultados = []
    errores = []
    
    log_evento(analista, "INICIO_PROCESAMIENTO_LOTE", {
        "total_archivos": len(archivos), 
        "caso_expediente": caso_expediente
    })
    
    for i, archivo_path in enumerate(archivos):
        nombre_archivo = Path(archivo_path).name
        
        log_evento(analista, "PROCESANDO_ARCHIVO", {
            "archivo": nombre_archivo, 
            "caso_expediente": caso_expediente
        })
        
        transcripcion, error, hash_archivo = procesar_audio_individual(archivo_path, assemblyai_key)
        
        if error:
            errores.append({
                "archivo": nombre_archivo,
                "error": error
            })
        else:
            print(f"✅ Transcripción exitosa para {nombre_archivo}: {transcripcion[:50]}...")
            resultados.append({
                "archivo": nombre_archivo,
                "transcripcion": transcripcion,
                "hash": hash_archivo
            })
            
            log_evento(analista, "TRANSCRIPCION_RECIBIDA", {
                "archivo": nombre_archivo,
                "caso_expediente": caso_expediente
            })
    
    return resultados, errores
