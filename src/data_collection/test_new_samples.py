#!/usr/bin/env python3
"""
Script para probar el modelo con muestras nuevas nunca vistas
Convierte los audios a formato estándar y ejecuta el detector
"""

import os
import sys
import subprocess
from pathlib import Path
import librosa
import soundfile as sf
import json

def convert_audio_to_standard(input_path, output_path, target_sr=16000):
    """Convierte audio a formato estándar: WAV, 16kHz, mono"""
    try:
        # Cargar audio
        audio, sr = librosa.load(input_path, sr=target_sr, mono=True)
        
        # Normalizar
        if audio.max() > 0:
            audio = audio / audio.max() * 0.9
        
        # Guardar
        sf.write(output_path, audio, target_sr)
        return True
    except Exception as e:
        print(f"   ❌ Error convirtiendo {input_path.name}: {e}")
        return False

def main():
    print("=" * 70)
    print("  🧪 TEST DE MODELO CON MUESTRAS NUEVAS")
    print("=" * 70)
    
    # Directorios
    test_dir = Path("data/test_validation")
    human_dir = test_dir / "human"
    elevenlabs_dir = test_dir / "elevenlabs"
    processed_dir = test_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    # Verificar que existen muestras
    human_files = list(human_dir.glob("*.wav")) if human_dir.exists() else []
    elevenlabs_files = list(elevenlabs_dir.glob("*.mp3")) if elevenlabs_dir.exists() else []
    
    print(f"\n📊 Muestras encontradas:")
    print(f"   🧑 Humanas: {len(human_files)}")
    print(f"   🤖 ElevenLabs: {len(elevenlabs_files)}")
    
    if len(human_files) == 0 and len(elevenlabs_files) == 0:
        print("\n⚠️  No se encontraron muestras.")
        print("\n💡 Ejecuta primero:")
        print("   1. python src/data_collection/record_validation_samples.py")
        print("   2. python src/data_collection/generate_new_elevenlabs_samples.py")
        return
    
    print("\n🔄 Convirtiendo audios a formato estándar (WAV 16kHz mono)...")
    
    processed_files = []
    labels = []
    
    # Convertir muestras humanas
    print("\n📁 Procesando muestras humanas...")
    for i, human_file in enumerate(human_files, 1):
        output_file = processed_dir / f"human_{human_file.stem}.wav"
        print(f"   [{i}/{len(human_files)}] {human_file.name} → {output_file.name}")
        
        if convert_audio_to_standard(human_file, output_file):
            processed_files.append(str(output_file))
            labels.append("HUMANO (bonafide)")
    
    # Convertir muestras de ElevenLabs
    print("\n📁 Procesando muestras ElevenLabs...")
    for i, elevenlabs_file in enumerate(elevenlabs_files, 1):
        output_file = processed_dir / f"elevenlabs_{elevenlabs_file.stem}.wav"
        print(f"   [{i}/{len(elevenlabs_files)}] {elevenlabs_file.name} → {output_file.name}")
        
        if convert_audio_to_standard(elevenlabs_file, output_file):
            processed_files.append(str(output_file))
            labels.append("DEEPFAKE (spoof)")
    
    print(f"\n✅ {len(processed_files)} archivos procesados correctamente")
    
    # Ejecutar detector
    print("\n" + "=" * 70)
    print("  🔍 EJECUTANDO DETECTOR EN TIEMPO REAL")
    print("=" * 70)
    print()
    
    # Ejecutar el detector en modo batch
    cmd = [
        "python",
        "src/realtime/realtime_detection.py",
        "--files"
    ] + processed_files
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    # Crear resumen manual
    print("\n" + "=" * 70)
    print("  📋 RESUMEN DE VALIDACIÓN")
    print("=" * 70)
    print(f"\n📊 Total de muestras testeadas: {len(processed_files)}")
    print(f"   🧑 Humanas: {len(human_files)}")
    print(f"   🤖 ElevenLabs: {len(elevenlabs_files)}")
    
    print("\n💡 Interpretación:")
    print("   • HUMANO → Debería detectar como VOZ HUMANA (bonafide)")
    print("   • DEEPFAKE → Debería detectar como DEEPFAKE (spoof)")
    print()
    print("✅ Si todas las predicciones son correctas = Modelo generaliza bien")
    print("⚠️  Si hay errores = Puede necesitar más datos de entrenamiento")
    
    print("\n" + "=" * 70)
    print("  🎯 Archivos de validación guardados en:")
    print(f"     {processed_dir}")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
