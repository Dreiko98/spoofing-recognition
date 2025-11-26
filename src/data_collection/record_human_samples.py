#!/usr/bin/env python3
"""Grabador de muestras de voz humana

Script interactivo para grabar muestras de voz humana usando el micrófono.

Uso:
    python record_human_samples.py --output_dir data/raw/human --num_samples 50

Requiere: pip install sounddevice soundfile
"""

import argparse
from pathlib import Path
import json
import random

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError:
    print("ERROR: Instala las dependencias:")
    print("  pip install sounddevice soundfile numpy")
    exit(1)


# Frases para leer (mismo conjunto que Siri/ElevenLabs para comparar)
SAMPLE_TEXTS = [
    "Hola, soy una persona real",
    "El clima está soleado hoy",
    "¿Necesitas ayuda con algo?",
    "La reunión es a las tres de la tarde",
    "Por favor confirma tu identidad",
    "El pronóstico indica lluvia para mañana",
    "Tu pedido llegará en dos días",
    "¿Quieres que configure una alarma?",
    "La temperatura actual es de veinte grados",
    "Tienes tres mensajes nuevos",
    "Bienvenido al sistema de verificación",
    "Tu solicitud ha sido aprobada",
]


def list_audio_devices():
    """Lista los dispositivos de audio disponibles"""
    print("\nDispositivos de audio disponibles:")
    print(sd.query_devices())


def record_audio(duration=5, sample_rate=48000):
    """Graba audio del micrófono
    
    Args:
        duration: duración en segundos
        sample_rate: tasa de muestreo (luego se convertirá a 16kHz)
    
    Returns:
        numpy array con el audio grabado
    """
    print(f"\n🎤 Grabando por {duration} segundos...")
    print("   (habla claro y natural)")
    
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    print("   ✅ Grabación completada")
    
    return audio.flatten()


def main():
    parser = argparse.ArgumentParser(description='Grabar muestras de voz humana')
    parser.add_argument('--output_dir', type=str, default='data/raw/human',
                        help='Directorio de salida para las grabaciones')
    parser.add_argument('--num_samples', type=int, default=20,
                        help='Número de muestras a grabar')
    parser.add_argument('--duration', type=int, default=3,
                        help='Duración de cada grabación en segundos')
    parser.add_argument('--sample_rate', type=int, default=48000,
                        help='Sample rate de grabación (se convertirá a 16kHz después)')
    parser.add_argument('--list_devices', action='store_true',
                        help='Listar dispositivos de audio y salir')
    parser.add_argument('--speaker_id', type=str, default='german',
                        help='Identificador del hablante (ej: german, maria)')
    parser.add_argument('--playback_speed', type=float, default=3.0,
                        help='Velocidad de reproducción (1.0=normal, 3.0=3x velocidad)')
    args = parser.parse_args()

    if args.list_devices:
        list_audio_devices()
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🎙️  GRABACIÓN DE MUESTRAS DE VOZ HUMANA")
    print("=" * 60)
    print(f"\nVas a grabar {args.num_samples} muestras")
    print(f"Duración de cada grabación: {args.duration} segundos")
    print(f"Hablante: {args.speaker_id}")
    print("\nInstrucciones:")
    print("  - Lee cada frase de forma natural")
    print("  - Habla claro y a volumen normal")
    print("  - Evita ruidos de fondo")
    print("  - Presiona ENTER para iniciar cada grabación")
    print("  - Escribe 'skip' para saltar una frase")
    print("  - Escribe 'quit' para terminar")
    print("\n" + "=" * 60)

    # Test de audio
    input("\nPresiona ENTER para hacer una grabación de prueba...")
    test_audio = record_audio(duration=3, sample_rate=args.sample_rate)
    print(f"🔊 Reproduciendo prueba a {args.playback_speed}x velocidad...")
    sd.play(test_audio, int(args.sample_rate * args.playback_speed))
    sd.wait()
    
    response = input("¿Se escucha bien? (s/n): ").lower()
    if response != 's':
        print("Ajusta tu micrófono y vuelve a intentar")
        return

    metadata = []
    successful = 0
    texts_copy = SAMPLE_TEXTS.copy()
    random.shuffle(texts_copy)

    for i in range(args.num_samples):
        if i >= len(texts_copy):
            # Si se acaban las frases, mezclar de nuevo
            texts_copy = SAMPLE_TEXTS.copy()
            random.shuffle(texts_copy)
        
        text = texts_copy[i % len(texts_copy)]
        
        print(f"\n{'─' * 60}")
        print(f"Muestra {i + 1}/{args.num_samples}")
        print(f"{'─' * 60}")
        print(f"\n📝 Lee esta frase:")
        print(f"\n    \"{text}\"\n")
        
        response = input("Presiona ENTER para grabar (o 'skip'/'quit'): ").strip().lower()
        
        if response == 'quit':
            print("Grabación cancelada por el usuario")
            break
        elif response == 'skip':
            print("Saltando...")
            continue
        
        # Grabar
        audio = record_audio(duration=args.duration, sample_rate=args.sample_rate)
        
        # Preguntar si repetir
        print(f"🔊 Reproduciendo a {args.playback_speed}x velocidad...")
        sd.play(audio, int(args.sample_rate * args.playback_speed))
        sd.wait()
        
        response = input("¿Guardar esta grabación? (s/n): ").strip().lower()
        if response != 's':
            print("Descartada, repitiendo...")
            continue
        
        # Guardar
        filename = f"human_{args.speaker_id}_{successful:05d}.wav"
        output_path = output_dir / filename
        sf.write(output_path, audio, args.sample_rate)
        
        metadata.append({
            'filename': filename,
            'text': text,
            'speaker_id': args.speaker_id,
            'duration': args.duration,
            'sample_rate': args.sample_rate,
            'source': 'human'
        })
        successful += 1
        print(f"✅ Guardada: {filename}")

    # Guardar metadata
    metadata_path = output_dir / f'metadata_{args.speaker_id}.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"✅ Grabadas {successful} muestras exitosamente")
    print(f"📁 Audios guardados en: {output_dir}")
    print(f"📄 Metadata guardada en: {metadata_path}")
    print(f"\n⚠️  Recuerda convertir los audios a .wav 16kHz mono con el script de conversión")
    print("=" * 60)


if __name__ == '__main__':
    main()
