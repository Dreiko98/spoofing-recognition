#!/usr/bin/env python3
"""Generador de muestras TTS para Linux (alternativa a Siri)

Este script usa el motor TTS nativo de Linux (espeak/pyttsx3) para generar
audio sintético, simulando lo que haría Siri en macOS.

Uso:
    python generate_linux_tts_samples.py --output_dir data/raw/linux_tts --num_samples 50

Requiere: 
    sudo apt-get install espeak espeak-ng
    pip install pyttsx3
"""

import argparse
import os
from pathlib import Path
import random
import json
import time
import subprocess
import tempfile


# Frases de ejemplo en español
SAMPLE_TEXTS = [
    "Hola, soy un asistente de inteligencia artificial",
    "El tiempo está despejado esta tarde",
    "¿En qué puedo ayudarte hoy?",
    "Tu cita está programada para las cuatro",
    "Por favor verifica tu información personal",
    "Mañana habrá tormentas eléctricas",
    "El paquete se entregará el próximo martes",
    "¿Deseas que active una notificación?",
    "La temperatura es de veinticinco grados",
    "Tienes cinco correos sin leer",
    "Bienvenido al sistema de autenticación",
    "Tu solicitud ha sido procesada",
    "Buenos días, ¿cómo estás?",
    "La reunión comenzará en cinco minutos",
    "Tu pedido está en camino",
    "Gracias por contactarnos",
    "El servicio estará disponible pronto",
    "Por favor, espere un momento",
    "La conexión se ha establecido correctamente",
    "Actualizando información del sistema",
]

# Voces disponibles en espeak para español
ESPEAK_VOICES = [
    'es',           # Español (defecto)
    'es-la',        # Español latinoamericano
    'es+f1',        # Español femenino variante 1
    'es+f2',        # Español femenino variante 2
    'es+f3',        # Español femenino variante 3
    'es+m1',        # Español masculino variante 1
    'es+m2',        # Español masculino variante 2
]

ESPEAK_SPEEDS = [140, 150, 160, 170, 180]  # Palabras por minuto
ESPEAK_PITCHES = [30, 40, 50, 60, 70]       # Tono de voz


def check_espeak_installed():
    """Verifica que espeak esté instalado"""
    try:
        result = subprocess.run(['espeak', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ espeak encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ espeak no está instalado correctamente")
            return False
    except FileNotFoundError:
        print("❌ espeak no está instalado")
        print("Instálalo con: sudo apt-get install espeak espeak-ng")
        return False
    except Exception as e:
        print(f"Error verificando espeak: {e}")
        return False


def generate_espeak_audio(text, output_path, voice='es', speed=160, pitch=50):
    """Genera audio usando espeak (TTS nativo de Linux)
    
    Args:
        text: texto a sintetizar
        output_path: ruta del archivo de salida (.wav)
        voice: voz de espeak a usar
        speed: velocidad en palabras por minuto
        pitch: tono de voz (0-99)
    
    Returns:
        True si se generó correctamente, False en caso contrario
    """
    try:
        # Crear archivo temporal WAV
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Comando espeak
        cmd = [
            'espeak',
            '-v', voice,
            '-s', str(speed),
            '-p', str(pitch),
            '-w', tmp_path,
            text
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(tmp_path):
            # Mover archivo temporal al destino final
            os.rename(tmp_path, output_path)
            return True
        else:
            print(f"  Error en espeak: {result.stderr}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  Timeout generando audio")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def try_pyttsx3(text, output_path):
    """Intenta usar pyttsx3 como alternativa"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Configurar voz española
        voices = engine.getProperty('voices')
        spanish_voices = [v for v in voices if 'spanish' in v.name.lower() or 'español' in v.name.lower()]
        
        if spanish_voices:
            engine.setProperty('voice', spanish_voices[0].id)
        
        # Configurar velocidad y volumen
        engine.setProperty('rate', random.randint(140, 180))
        engine.setProperty('volume', 0.9)
        
        # Guardar audio
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()
        
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        
    except Exception as e:
        print(f"  Error con pyttsx3: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Generar muestras TTS en Linux (alternativa a Siri)')
    parser.add_argument('--output_dir', type=str, default='data/raw/linux_tts',
                        help='Directorio de salida para los audios')
    parser.add_argument('--num_samples', type=int, default=50,
                        help='Número de muestras a generar')
    parser.add_argument('--engine', type=str, default='espeak',
                        choices=['espeak', 'pyttsx3', 'auto'],
                        help='Motor TTS a usar')
    parser.add_argument('--vary_params', action='store_true',
                        help='Variar voz, velocidad y tono para cada muestra')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Verificar disponibilidad de motores
    espeak_available = check_espeak_installed()
    
    if args.engine == 'espeak' and not espeak_available:
        print("\n❌ espeak no disponible. Instálalo o usa --engine pyttsx3")
        return
    
    if args.engine == 'auto':
        engine = 'espeak' if espeak_available else 'pyttsx3'
        print(f"\n✨ Usando motor: {engine}")
    else:
        engine = args.engine

    metadata = []
    successful = 0

    print(f"\n{'='*60}")
    print(f"Generando {args.num_samples} muestras con {engine.upper()}")
    print(f"Directorio: {output_dir}")
    print(f"Variación de parámetros: {'Sí' if args.vary_params else 'No'}")
    print(f"{'='*60}\n")

    for i in range(args.num_samples):
        text = random.choice(SAMPLE_TEXTS)
        
        # Configurar parámetros variables
        if args.vary_params:
            voice = random.choice(ESPEAK_VOICES)
            speed = random.choice(ESPEAK_SPEEDS)
            pitch = random.choice(ESPEAK_PITCHES)
        else:
            voice = 'es'
            speed = 160
            pitch = 50
        
        filename = f"linux_tts_{engine}_{i:05d}.wav"
        output_path = output_dir / filename

        success = False
        
        if engine == 'espeak':
            success = generate_espeak_audio(text, output_path, voice, speed, pitch)
        elif engine == 'pyttsx3':
            success = try_pyttsx3(text, output_path)

        if success:
            metadata.append({
                'filename': filename,
                'text': text,
                'tts_engine': f'linux_{engine}',
                'voice': voice if engine == 'espeak' else 'default',
                'speed': speed if engine == 'espeak' else 'default',
                'pitch': pitch if engine == 'espeak' else 'default',
            })
            successful += 1
            
            if (i + 1) % 10 == 0:
                print(f"  ✅ Generadas {i + 1}/{args.num_samples}...")
        else:
            print(f"  ❌ Error en muestra {i + 1}")

    # Guardar metadata
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✅ Generadas {successful}/{args.num_samples} muestras exitosamente")
    print(f"📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    print(f"{'='*60}")
    
    if successful < args.num_samples:
        print(f"\n⚠️  {args.num_samples - successful} muestras fallaron")
    
    print(f"\n💡 Los archivos ya están en formato WAV")
    print(f"   Pero necesitan conversión a 16kHz mono para AASIST")


if __name__ == '__main__':
    main()
