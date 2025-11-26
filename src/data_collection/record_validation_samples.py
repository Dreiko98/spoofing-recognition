#!/usr/bin/env python3
"""
Script rápido para grabar nuevas muestras de voz humana para validación
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from pathlib import Path

def record_sample(duration=3, sample_rate=16000):
    """Graba una muestra de audio"""
    print("🎤 Preparado para grabar...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    print("   🔴 GRABANDO!\n")
    
    # Grabar
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("   ✅ Grabación completa\n")
    return audio.flatten()

def main():
    output_dir = Path("data/test_validation/human")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("  🎤 GRABACIÓN DE MUESTRAS DE VALIDACIÓN")
    print("=" * 70)
    print("\n💡 Vamos a grabar 5 muestras nuevas de tu voz")
    print("   Duración: 3 segundos cada una")
    print("   Habla de forma natural, di diferentes frases\n")
    
    frases_sugeridas = [
        "Hola, esta es una prueba del detector de deepfakes",
        "Buenos días, mi nombre es Germán y estoy probando el sistema",
        "¿Cómo estás? Espero que todo vaya bien hoy",
        "Este es un mensaje de audio completamente real",
        "La inteligencia artificial está avanzando rápidamente"
    ]
    
    samples = []
    
    for i in range(5):
        print(f"\n{'='*70}")
        print(f"  MUESTRA {i+1}/5")
        print(f"{'='*70}")
        print(f"\n💬 Frase sugerida (opcional):")
        print(f'   "{frases_sugeridas[i]}"')
        print()
        
        input("Presiona ENTER cuando estés listo...")
        
        # Grabar
        audio = record_sample()
        
        # Guardar
        filename = f"human_validation_{i+1:02d}.wav"
        filepath = output_dir / filename
        sf.write(filepath, audio, 16000)
        
        print(f"💾 Guardado: {filepath}")
        samples.append(filepath)
        
        time.sleep(1)
    
    print("\n" + "="*70)
    print("  ✅ GRABACIÓN COMPLETADA")
    print("="*70)
    print(f"\n📁 {len(samples)} muestras guardadas en: {output_dir}")
    print("\n🎯 Archivos creados:")
    for sample in samples:
        print(f"   • {sample.name}")
    
    print("\n💡 Próximo paso:")
    print("   python src/data_collection/generate_new_elevenlabs_samples.py")

if __name__ == '__main__':
    main()
