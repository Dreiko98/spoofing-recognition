#!/usr/bin/env python3
"""
Script para procesar y analizar audios de WhatsApp
"""

import os
import sys
from pathlib import Path
import librosa
import soundfile as sf
import subprocess

def convert_whatsapp_audio(input_path, output_path, target_sr=16000):
    """Convierte audio de WhatsApp (OGG) a formato estándar WAV"""
    try:
        # Cargar audio (librosa maneja .ogg automáticamente)
        audio, sr = librosa.load(input_path, sr=target_sr, mono=True)
        
        # Normalizar volumen
        if audio.max() > 0:
            audio = audio / audio.max() * 0.9
        
        # Guardar como WAV 16kHz mono
        sf.write(output_path, audio, target_sr)
        return True, len(audio) / target_sr  # Retorna duración
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, 0

def main():
    print("=" * 70)
    print("  📱 PROCESAMIENTO DE AUDIOS DE WHATSAPP")
    print("=" * 70)
    
    # Directorios
    input_dir = Path("data/test_validation/human")
    output_dir = Path("data/test_validation/whatsapp_processed")
    output_dir.mkdir(exist_ok=True)
    
    # Buscar archivos .ogg
    ogg_files = list(input_dir.glob("*.ogg"))
    
    if not ogg_files:
        print("\n⚠️  No se encontraron archivos .ogg en data/test_validation/human/")
        return
    
    print(f"\n📊 Archivos de WhatsApp encontrados: {len(ogg_files)}")
    print(f"📁 Input: {input_dir}")
    print(f"📁 Output: {output_dir}")
    
    print("\n🔄 Convirtiendo a formato estándar (WAV 16kHz mono)...\n")
    
    processed_files = []
    total_duration = 0
    
    for i, ogg_file in enumerate(ogg_files, 1):
        # Nombre de salida más limpio
        output_name = f"whatsapp_{i:02d}.wav"
        output_path = output_dir / output_name
        
        print(f"[{i}/{len(ogg_files)}] {ogg_file.name}")
        print(f"         → {output_name}", end=" ")
        
        success, duration = convert_whatsapp_audio(ogg_file, output_path)
        
        if success:
            print(f"✅ ({duration:.1f}s)")
            processed_files.append(str(output_path))
            total_duration += duration
        else:
            print()
    
    print(f"\n✅ {len(processed_files)}/{len(ogg_files)} archivos procesados correctamente")
    print(f"⏱️  Duración total: {total_duration:.1f} segundos")
    
    if not processed_files:
        print("\n❌ No se procesó ningún archivo")
        return
    
    # Ejecutar detector
    print("\n" + "=" * 70)
    print("  🔍 EJECUTANDO DETECTOR DE DEEPFAKES")
    print("=" * 70)
    print()
    
    # Construir comando
    cmd = [
        "python",
        "src/realtime/realtime_detection.py",
        "--files"
    ] + processed_files
    
    # Ejecutar
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("  📋 RESUMEN FINAL")
    print("=" * 70)
    print(f"\n📊 Archivos de WhatsApp analizados: {len(processed_files)}")
    print(f"📁 Archivos procesados guardados en: {output_dir}")
    print(f"\n💡 Interpretación:")
    print("   ✅ Todos deberían ser detectados como HUMANO (bonafide)")
    print("   ⚠️  Si alguno es detectado como DEEPFAKE:")
    print("      • Puede ser por compresión de WhatsApp")
    print("      • Calidad del audio afectada")
    print("      • Ruido de fondo")
    
    print("\n🎯 Archivos originales en:")
    print(f"   {input_dir}")
    print("🎯 Archivos procesados en:")
    print(f"   {output_dir}")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
