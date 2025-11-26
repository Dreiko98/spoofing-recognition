#!/usr/bin/env python3
"""Generador de muestras de voz Siri (macOS)

Este script usa el comando `say` de macOS para generar audio sintético
con la voz de Siri en diferentes idiomas.

Uso:
    python generate_siri_samples.py --output_dir data/raw/siri --num_samples 100

Requiere: macOS con comando `say` disponible
"""

import argparse
import subprocess
from pathlib import Path
import random
import json


# Frases de ejemplo en español
SAMPLE_TEXTS_ES = [
    "Hola, soy un asistente virtual",
    "El clima está soleado hoy",
    "¿Necesitas ayuda con algo?",
    "La reunión es a las tres de la tarde",
    "Por favor confirma tu identidad",
    "El pronóstico indica lluvia para mañana",
    "Tu pedido llegará en dos días",
    "¿Quieres que configure una alarma?",
    "La temperatura actual es de veinte grados",
    "Tienes tres mensajes nuevos",
]

# Frases en inglés
SAMPLE_TEXTS_EN = [
    "Hello, I am a virtual assistant",
    "The weather is sunny today",
    "Do you need help with something?",
    "The meeting is at three PM",
    "Please confirm your identity",
    "The forecast shows rain for tomorrow",
    "Your order will arrive in two days",
    "Would you like me to set an alarm?",
    "The current temperature is seventy degrees",
    "You have three new messages",
]

# Voces disponibles en macOS (ejemplo, varían según versión)
SIRI_VOICES = {
    'es': ['Monica', 'Paulina', 'Jorge'],  # español
    'en': ['Samantha', 'Alex', 'Victoria'],  # inglés
}


def check_say_available():
    """Verifica que el comando 'say' esté disponible (solo macOS)"""
    try:
        subprocess.run(['say', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def list_available_voices():
    """Lista las voces disponibles en el sistema"""
    try:
        result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True, check=True)
        print("Voces disponibles en el sistema:")
        print(result.stdout)
        return result.stdout
    except Exception as e:
        print(f"Error listando voces: {e}")
        return None


def generate_siri_audio(text, voice, output_path):
    """Genera un archivo de audio usando el comando 'say'
    
    Args:
        text: texto a sintetizar
        voice: nombre de la voz (ej: 'Monica', 'Samantha')
        output_path: ruta del archivo de salida (.aiff)
    
    Returns:
        True si se generó correctamente, False en caso contrario
    """
    try:
        # say genera AIFF por defecto, luego lo convertimos
        cmd = ['say', '-v', voice, '-o', str(output_path), text]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generando audio: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Generar muestras de audio con Siri (macOS)')
    parser.add_argument('--output_dir', type=str, default='data/raw/siri',
                        help='Directorio de salida para los audios')
    parser.add_argument('--num_samples', type=int, default=50,
                        help='Número de muestras a generar')
    parser.add_argument('--language', type=str, default='es', choices=['es', 'en'],
                        help='Idioma (es o en)')
    parser.add_argument('--list_voices', action='store_true',
                        help='Listar voces disponibles y salir')
    args = parser.parse_args()

    if args.list_voices:
        list_available_voices()
        return

    if not check_say_available():
        print("ERROR: El comando 'say' no está disponible.")
        print("Este script solo funciona en macOS.")
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    texts = SAMPLE_TEXTS_ES if args.language == 'es' else SAMPLE_TEXTS_EN
    voices = SIRI_VOICES.get(args.language, ['Monica'])

    metadata = []
    successful = 0

    print(f"Generando {args.num_samples} muestras en {args.language}...")
    print(f"Voces: {voices}")

    for i in range(args.num_samples):
        text = random.choice(texts)
        voice = random.choice(voices)
        filename = f"siri_{args.language}_{voice}_{i:05d}.aiff"
        output_path = output_dir / filename

        if generate_siri_audio(text, voice, output_path):
            metadata.append({
                'filename': filename,
                'text': text,
                'voice': voice,
                'language': args.language,
                'tts_engine': 'macos_siri'
            })
            successful += 1
            if (i + 1) % 10 == 0:
                print(f"  Generadas {i + 1}/{args.num_samples}...")

    # Guardar metadata
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generadas {successful} muestras exitosamente")
    print(f"📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    print(f"\n⚠️  Recuerda convertir los .aiff a .wav 16kHz mono con el script de conversión")


if __name__ == '__main__':
    main()
