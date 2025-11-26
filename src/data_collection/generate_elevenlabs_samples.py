#!/usr/bin/env python3
"""Generador de muestras de voz ElevenLabs

Este script usa la API de ElevenLabs para generar audio sintético.

Uso:
    export ELEVENLABS_API_KEY="tu_clave_aqui"
    python generate_elevenlabs_samples.py --output_dir data/raw/elevenlabs --num_samples 100

Requiere: pip install elevenlabs
"""

import argparse
import os
from pathlib import Path
import random
import json
import time


# Voces en español VERIFICADAS que funcionan con plan gratuito
# Nota: Solo estas 2 voces funcionan consistentemente sin error "voice_limit_reached"
SPANISH_VOICES = {
    'colombiano_mujer': {'id': 'VmejBeYhbrcTPwDniox7', 'name': 'Colombiana Mujer'},
    'peruano_mujer': {'id': '5vkxOzoz40FrElmLP4P7', 'name': 'Peruana Mujer'},
    # Las siguientes voces causan error "voice_limit_reached" en plan gratuito:
    # 'colombiano_hombre': {'id': 'o2vbTbO3g4GrKUg7rehy', 'name': 'Colombiano Hombre'},
    # 'chileno_hombre': {'id': '0cheeVA5B3Cv6DGq65cT', 'name': 'Chileno Hombre'},
    # 'español_mujer': {'id': '1eHrpOW5l98cxiSRjbzJ', 'name': 'Española Mujer'},
    # 'español_hombre': {'id': 'CdAqYBLnsNjmTqYgD5Ha', 'name': 'Español Hombre'},
    # 'chileno_mujer': {'id': 'GJid0jgRsqjUy21Avuex', 'name': 'Chilena Mujer'},
    # 'peruano_hombre': {'id': 'G9D0re5CXvFlaorVnZjj', 'name': 'Peruano Hombre'},
}

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
]


def check_api_key():
    """Verifica que la API key esté configurada"""
    # Primero intentar desde variable de entorno, luego fallback a hardcoded
    api_key = os.getenv('ELEVENLABS_API_KEY') or '2e180d88ba9986b26f37c8d1c7ef246f21b4f193fde6c031af2d4d49d5089638'
    if not api_key:
        print("ERROR: Variable de entorno ELEVENLABS_API_KEY no configurada")
        print("Ejecuta: export ELEVENLABS_API_KEY='tu_clave'")
        return False
    return api_key


def list_available_voices(client):
    """Lista las voces disponibles en ElevenLabs"""
    try:
        voices = client.voices.get_all()
        print("\nVoces disponibles en ElevenLabs:")
        for voice in voices.voices:
            print(f"  - {voice.name} (ID: {voice.voice_id})")
        return voices.voices
    except Exception as e:
        print(f"Error listando voces: {e}")
        return []


def generate_elevenlabs_audio(client, text, voice_id, output_path, model="eleven_flash_v2_5"):
    """Genera audio usando ElevenLabs API
    
    Args:
        client: cliente de ElevenLabs
        text: texto a sintetizar
        voice_id: ID de la voz a usar
        output_path: ruta del archivo de salida (.mp3)
        model: modelo de TTS a usar
    
    Returns:
        True si se generó correctamente, False en caso contrario
    """
    try:
        # Generar audio usando la API correcta (método simplificado)
        audio_generator = client.generate(
            text=text,
            voice=voice_id,
            model=model
        )
        
        # Guardar archivo
        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                if isinstance(chunk, bytes):
                    f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error generando audio con voz {voice_id}: {e}")
        # Intentar con método alternativo
        try:
            print(f"  Intentando método alternativo...")
            audio_generator = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=model,
                output_format="mp3_44100_128"
            )
            
            with open(output_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            return True
        except Exception as e2:
            print(f"  Error en método alternativo: {e2}")
            return False


def list_spanish_voices():
    """Lista las voces en español disponibles"""
    print("\n🎤 Voces en español disponibles:")
    print("=" * 60)
    for key, voice in SPANISH_VOICES.items():
        print(f"  {key:<20} → {voice['name']:<20} (ID: {voice['id']})")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Generar muestras de audio con ElevenLabs')
    parser.add_argument('--output_dir', type=str, default='data/raw/elevenlabs',
                        help='Directorio de salida para los audios')
    parser.add_argument('--num_samples', type=int, default=50,
                        help='Número de muestras a generar')
    parser.add_argument('--model', type=str, default='eleven_flash_v2_5',
                        choices=['eleven_flash_v2_5', 'eleven_multilingual_v2', 'eleven_turbo_v2_5'],
                        help='Modelo de TTS a usar')
    parser.add_argument('--voice_id', type=str, default=None,
                        help='ID de voz específica')
    parser.add_argument('--voice_type', type=str, default=None,
                        choices=list(SPANISH_VOICES.keys()),
                        help='Tipo de voz en español (ej: colombiano_mujer, español_hombre)')
    parser.add_argument('--list_voices', action='store_true',
                        help='Listar voces disponibles de ElevenLabs')
    parser.add_argument('--list_spanish', action='store_true',
                        help='Listar voces en español verificadas')
    parser.add_argument('--rate_limit', type=float, default=1.0,
                        help='Segundos de espera entre requests (para evitar rate limit)')
    parser.add_argument('--random_spanish', action='store_true',
                        help='Usar voces en español aleatorias para cada muestra')
    args = parser.parse_args()

    api_key = check_api_key()
    if not api_key:
        return

    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        print("ERROR: Instala el paquete elevenlabs:")
        print("  pip install elevenlabs")
        return

    # Inicializar cliente
    client = ElevenLabs(api_key=api_key)

    if args.list_voices:
        list_available_voices(client)
        return
    
    if args.list_spanish:
        list_spanish_voices()
        return

    # Determinar qué voz usar
    use_random_spanish = args.random_spanish
    
    if args.voice_id:
        # Voz específica por ID
        voice_id = args.voice_id
        voice_name = "custom"
    elif args.voice_type:
        # Voz específica de español
        selected = SPANISH_VOICES[args.voice_type]
        voice_id = selected['id']
        voice_name = selected['name']
    else:
        # Por defecto, usar voz española aleatoria
        selected_key = random.choice(list(SPANISH_VOICES.keys()))
        selected = SPANISH_VOICES[selected_key]
        voice_id = selected['id']
        voice_name = selected['name']
        print(f"\n✨ Usando voz en español: {voice_name} ({selected_key})")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = []
    successful = 0

    print(f"\nGenerando {args.num_samples} muestras...")
    print(f"Modelo: {args.model}")
    print(f"Voz: {voice_name} ({voice_id})")
    print(f"Rate limit: {args.rate_limit}s entre requests\n")

    for i in range(args.num_samples):
        text = random.choice(SAMPLE_TEXTS)
        
        # Si se usa random_spanish, cambiar voz para cada muestra
        if use_random_spanish:
            selected_key = random.choice(list(SPANISH_VOICES.keys()))
            selected = SPANISH_VOICES[selected_key]
            current_voice_id = selected['id']
            current_voice_name = selected['name']
        else:
            current_voice_id = voice_id
            current_voice_name = voice_name
        
        filename = f"elevenlabs_{args.model}_{i:05d}.mp3"
        output_path = output_dir / filename

        if generate_elevenlabs_audio(client, text, current_voice_id, output_path, model=args.model):
            metadata.append({
                'filename': filename,
                'text': text,
                'voice_id': current_voice_id,
                'voice_name': current_voice_name,
                'model': args.model,
                'tts_engine': 'elevenlabs'
            })
            successful += 1
            if (i + 1) % 10 == 0:
                print(f"  Generadas {i + 1}/{args.num_samples}...")
        
        # Rate limiting
        if i < args.num_samples - 1:
            time.sleep(args.rate_limit)

    # Guardar metadata
    metadata_path = output_dir / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generadas {successful} muestras exitosamente")
    print(f"📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    print(f"\n⚠️  Recuerda convertir los .mp3 a .wav 16kHz mono con el script de conversión")


if __name__ == '__main__':
    main()
